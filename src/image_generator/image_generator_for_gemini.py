"""
Define ImageGeneratorForGemini class.
"""
import pprint
import time
from typing import Optional
from google import genai
from google.genai.errors import ClientError
from loguru import logger
from PIL import Image
from io import BytesIO

from src.image_generator.image_generator_base import ImageGeneratorBase
from src.image_generator.input_output_file_path_spec import InputOutputFilePathSpec

class ImageGeneratorForGemini(ImageGeneratorBase):
    def __init__(self):
        self.client: Optional[genai.Client] = None

    def generate_image(self, input_output_file_path_spec: InputOutputFilePathSpec, prompt: str) -> bool:
        if not self.client:
            logger.error("Gemini client is not initialized.")
            return False
        for item in input_output_file_path_spec.get_item_list():
            r = self._generate_one_image(
                item['input_file_path_list'][0],
                item['input_file_path_list'][1],
                item['output_file_path_list'][0],
                prompt
            )
            logger.info(f"Image generation result: {r}")
            if item != input_output_file_path_spec.get_item_list()[-1]:
                logger.info("Waiting for 60 seconds to avoid hitting rate limits...")
                const_time_to_sleep_in_seconds = 60
                time.sleep(const_time_to_sleep_in_seconds)
        return True

    def _generate_one_image(self, input_source_file_path: str, input_reference_file_path: str, output_image_path: str, prompt: str) -> bool:
        try:
            image0 = Image.open(input_source_file_path)
        except Exception as e:
            logger.error(f"Failed to open image at {input_source_file_path}: {e}")
            return False
        try:
            image1 = Image.open(input_reference_file_path)
        except Exception as e:
            logger.error(f"Failed to open image at {input_reference_file_path}: {e}")
            return False
        const_model_name = "models/gemini-2.5-flash-image-preview"
        try:
            logger.info("Calling Gemini API...")
            response = self.client.models.generate_content(
                model=const_model_name,
                contents=[prompt, image0, image1],
            )
            logger.info("Done.")
            self.show_reseponse_info(response)
            if not response.candidates:
                logger.error("No candidates in the response.")
                return False
            if not response.candidates[0].content:
                logger.error("The first candidate has no content.")
                return False
            if not response.candidates[0].content.parts:
                logger.error("The first candidate has no content parts.")
                return False
            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    logger.info(part.text)
                elif part.inline_data is not None:
                    logger.info("Saving image...")
                    image = Image.open(BytesIO(part.inline_data.data))
                    image.save(output_image_path)
                    logger.info("Saved.")
        except ClientError as e:
            logger.error(f"Gemini API error: {e}")
            return False
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

    def show_reseponse_info(self, response):
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
            api_key = gemini_config.get('api_key')
            if not api_key:
                logger.error("Gemini API key is missing in the configuration.")
                return False
            self.client = genai.Client(api_key=api_key)
        return True

    def do_task_with_gemini(self, gemini_config: dict, prompt_config: dict, input_output_file_path_spec: InputOutputFilePathSpec) -> bool:
        r = self._initialize_gemini_client(gemini_config)
        if not r:
            return False
        prompt = prompt_config.get('prompt')
        return self.generate_image(input_output_file_path_spec, prompt)
