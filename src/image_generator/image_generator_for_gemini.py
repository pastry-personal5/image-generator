"""
Define ImageGeneratorForGemini class.
"""
import os
import pprint
import time
from typing import Optional

from google import genai
from google.genai import types
from google.genai.errors import ClientError, ServerError
from loguru import logger
from PIL import Image
from io import BytesIO

from src.image_generator.image_generator_base import ImageGeneratorBase
from src.image_generator.input_output_file_path_spec import InputOutputFilePathSpec


def filter_log_message_for_gemini_api_call(record):
    return "[GEMINI_API_CALL]" in record["message"]


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class LoggerSingletonForGeminiAPICall(metaclass=Singleton):

    def __init__(self):
        pass

    def init_logger(self):
        logger.add("gemini_api_call.log", rotation="10 MB", compression="zip", level="INFO", filter=filter_log_message_for_gemini_api_call)


class FilePathBuilder():

    def __init__(self):
        # It's just a reference.
        self.input_output_file_path_spec = None

    def set_reference_to_input_output_file_path_spec(self, input_output_file_path_spec: InputOutputFilePathSpec) -> None:
        self.input_output_file_path_spec = input_output_file_path_spec


class ImageGeneratorForGemini(ImageGeneratorBase):

    def __init__(self):
        self.client: Optional[genai.Client] = None
        self.extra_gemini_api_logger = LoggerSingletonForGeminiAPICall()
        self.extra_gemini_api_logger.init_logger()
        self.file_path_builder = FilePathBuilder()

    def generate_one_batch_of_images(self, input_output_file_path_spec: InputOutputFilePathSpec, prompt: str) -> bool:
        len_of_generation_request = len(input_output_file_path_spec.get_item_list())
        count = 0
        count_success = 0
        count_failure = 0
        if not self.client:
            logger.error("Gemini client is not initialized.")
            return False
        for item in input_output_file_path_spec.get_item_list():
            r = self._generate_images_using_api_call(
                item['input_file_path_list'],
                item['output_file_path_list'],
                prompt
            )
            logger.info(f"Image generation result: {r}")
            count += 1
            if r:
                count_success += 1
            else:
                count_failure += 1
            if item != input_output_file_path_spec.get_item_list()[-1]:
                const_time_to_sleep_in_seconds = 8
                logger.info(f"Waiting for {const_time_to_sleep_in_seconds} seconds to avoid hitting rate limits...")
                time.sleep(const_time_to_sleep_in_seconds)
            logger.info(f"Among: {len_of_generation_request} So far... total requests: {count}, Success: {count_success}, Failure: {count_failure}")
        return True

    def _get_generate_content_config(self):
        # As of 2025-09-03, a substring "IMAGE" in category is not supported yet.
        # i.e. please note that HARM_CATEGORY_IMAGE_HARASSMENT nor HARM_CATEGORY_IMAGE_SEXUALLY_EXPLICIT are not supported yet.
        # Instead, use text-related categories only.
        # For the latest information, please refer to: https://developers.generativeai.google/api/gemini/reference/rest/v1/models/generateContent
        generate_content_config = types.GenerateContentConfig(
            temperature = 1,
            top_p = 0.95,
            max_output_tokens = 32768,
            response_modalities = ["IMAGE"],
            safety_settings = [types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=types.HarmBlockThreshold.BLOCK_NONE
            ),types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=types.HarmBlockThreshold.BLOCK_NONE
            )],
        )
        return generate_content_config

    def _load_input_image_files(self, input_file_path_list_as_arg: list[str]) -> tuple[bool, list[Image.Image]]:
        input_image_file_list = []
        for input_file_path in input_file_path_list_as_arg:
            try:
                image_file = Image.open(input_file_path)
            except (FileNotFoundError, OSError) as e:
                logger.error(f"Failed to open image at {input_file_path}: {e}")
                return (False, None, None)
            input_image_file_list.append(image_file)
        return (True, input_image_file_list)

    def _generate_images_using_api_call(self, input_file_path_list_as_arg: list[str], output_file_path_list_as_arg: list[str], prompt: str) -> bool:
        (result, input_image_file_list) = self._load_input_image_files(input_file_path_list_as_arg)
        if not result:
            return False
        result = self._generate_and_write_output_images(prompt, input_image_file_list, input_file_path_list_as_arg, output_file_path_list_as_arg)
        return result

    def _log_gemini_api_call(self, prompt: str, input_file_path_list: list[str], output_image_paths: list[str]) -> None:
        prompt_to_log = prompt.strip()
        string_to_log = f"\"[GEMINI_API_CALL]\","
        for output_image_path in output_image_paths:
            string_to_log += f"\"{output_image_path}\","
        for input_file_path in input_file_path_list:
            string_to_log += f"\"{input_file_path}\","
        string_to_log += f"\"{prompt_to_log}\""
        logger.info(string_to_log)

    def _generate_and_write_output_images(self, prompt: str, input_image_file_list: list[Image.Image], input_file_path_list_as_arg: list[str], output_file_path_list_as_arg: list[str]) -> bool:

        count_saved = 0
        try:
            generate_content_config = self._get_generate_content_config()
            const_model_name = "models/gemini-2.5-flash-image-preview"
            contents = []
            contents.append(prompt)
            for image_file in input_image_file_list:
                contents.append(image_file)
            logger.info("Calling Gemini API...")
            response = self.client.models.generate_content(
                model=const_model_name,
                contents=contents,
                config=generate_content_config,
            )
            logger.info("Done.")
            self._show_response_info(response)
            if not response.candidates:
                logger.error("No candidates in the response.")
                return False
            number_of_candidates = len(response.candidates)
            logger.info(f"Number of candidates: {number_of_candidates}")
            if number_of_candidates == 0:
                logger.error("No candidates returned from the API.")
                return False

            output_image_path_list = []
            for i in range(number_of_candidates):
                if i == 0:
                    output_image_path_list.append(output_file_path_list_as_arg)
                else:
                    for o in output_file_path_list_as_arg:
                        output_image_name_modified = f"{os.path.splitext(os.path.basename(o))[0]}.candidate.{i}{os.path.splitext(o)[1]}"
                        output_image_path_modified = os.path.join(os.path.dirname(o), output_image_name_modified)
                        output_image_path_list.append(output_image_path_modified)

            index = 0
            for c in response.candidates:
                logger.info(f"Candidate: {c}")
                if not c.content:
                    logger.error("The candidate has no content.")
                    continue
                if not c.content.parts:
                    logger.error("The candidate has no content parts.")
                    continue
                for part in c.content.parts:
                    if part.text is not None:
                        logger.info(part.text)
                    elif part.inline_data is not None:
                        logger.info("Saving image...")
                        image = Image.open(BytesIO(part.inline_data.data))
                        output_image_paths = output_image_path_list[index]
                        for output_image_path in output_image_paths:
                            image.save(output_image_path)
                        logger.info("Saved.")
                        self._log_gemini_api_call(prompt, input_file_path_list_as_arg, output_image_paths)
                        count_saved += 1
                index += 1
        except ServerError as e:
            logger.error(f"Gemini server error: {e}")
            return False
        except ClientError as e:
            logger.error(f"Gemini API error: {e}")
            return False
        if count_saved > 0:
            return True
        else:
            return False

    def _show_response_info(self, response):
        logger.info(f"Response: {response}")
        logger.info(f"Response type: {type(response)}")
        logger.info(f"Response candidates count: {len(response.candidates)}")
        for i, candidate in enumerate(response.candidates):
            if candidate.content is None:
                logger.warning(f"Candidate {i} has no content.")
                continue
            logger.info(f"Candidate {i} content parts count: {len(candidate.content.parts)}")
            for j, part in enumerate(candidate.content.parts):
                if part.text is not None:
                    logger.info(f"Candidate {i} Part {j} is text with length {len(part.text)}")
                elif part.inline_data is not None:
                    logger.info(f"Candidate {i} Part {j} is inline data with mime_type {part.inline_data.mime_type} and data length {len(part.inline_data.data)}")
                elif part.uri is not None:
                    logger.info(f"Candidate {i} Part {j} is uri: {part.uri}")
                else:
                    logger.info(f"Candidate {i} Part {j} is unknown type")

    def _initialize_gemini_client(self, gemini_config: dict) -> bool:
        if self.client is None:
            api_key = gemini_config.get("api_key")
            if not api_key:
                logger.error("Gemini API key is missing in the configuration.")
                return False
            self.client = genai.Client(api_key=api_key)
        return True

    def list_all_models(self):
        pager = self.client.models.list(config={'page_size': 32})
        while True:
            for p in pager:
                pprint.pprint(p)
            try:
                pager.next_page()
            except StopIteration:
                break
            except IndexError:
                break

    def do_generation(self, model_specific_config: dict, prompt: str, input_output_file_path_spec: InputOutputFilePathSpec) -> bool:
        r = self._initialize_gemini_client(model_specific_config)
        if not r:
            return False
        return self.generate_one_batch_of_images(input_output_file_path_spec, prompt)
