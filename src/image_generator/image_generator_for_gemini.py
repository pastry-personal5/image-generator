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

class ImageGeneratorForGemini(ImageGeneratorBase):

    def __init__(self):
        self.client: Optional[genai.Client] = None
        logger.add("gemini_api_call.log", rotation="10 MB", compression="zip", level="INFO", filter=filter_log_message_for_gemini_api_call)

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
                item['input_file_path_list'][0],
                item['input_file_path_list'][1],
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

    def _generate_images_using_api_call(self, input_source_file_path: str, input_reference_file_path: str, output_file_path_list_as_arg: list[str], prompt: str) -> bool:
        try:
            image0 = Image.open(input_source_file_path)
        except (FileNotFoundError, OSError) as e:
            logger.error(f"Failed to open image at {input_source_file_path}: {e}")
            return False
        try:
            image1 = Image.open(input_reference_file_path)
        except (FileNotFoundError, OSError) as e:
            logger.error(f"Failed to open image at {input_reference_file_path}: {e}")
            return False

        count_saved = 0
        try:
            generate_content_config = self._get_generate_content_config()
            logger.info("Calling Gemini API...")
            const_model_name = "models/gemini-2.5-flash-image-preview"
            response = self.client.models.generate_content(
                model=const_model_name,
                contents=[prompt, image0, image1],
                config=generate_content_config,
            )
            logger.info("Done.")
            self.show_response_info(response)
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
                        image.save(output_image_paths[0])
                        image.save(output_image_paths[1])
                        logger.info("Saved.")
                        # @FIXME(dennis.oh) Escape strings properly.
                        prompt_to_log = prompt.strip()
                        logger.info(f"\"[GEMINI_API_CALL]\",\"{output_image_paths[0]}\",\"{output_image_paths[1]}\",\"{input_source_file_path}\",\"{input_reference_file_path}\",\"{prompt_to_log}\"")
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

    def show_response_info(self, response):
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

    def do_task_with_gemini(self, gemini_config: dict, prompt_config: dict, input_output_file_path_spec: InputOutputFilePathSpec) -> bool:
        r = self._initialize_gemini_client(gemini_config)
        if not r:
            return False
        prompt = prompt_config.get("prompt")
        return self.generate_one_batch_of_images(input_output_file_path_spec, prompt)
