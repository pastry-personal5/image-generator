"""
Define main functions for image generation.
"""
from datetime import datetime
import os
from typing import Optional
import yaml

from loguru import logger

from src.image_generator.image_generator_for_gemini import ImageGeneratorForGemini
from src.image_generator.input_output_file_path_spec import InputOutputFilePathSpec


def remove_file_extension(file_path):
    """
    Removes the file extension from a file path.
    Example: 'path/to/image.jpg' -> 'path/to/image'
    """
    return os.path.splitext(file_path)[0]


def get_date_and_time_part() -> str:
    """Get current date and time as a string."""

    now = datetime.now()
    return now.strftime("%Y%m%d-%H%M%S")


def get_output_image_name(source_image_name: str, reference_image_name: str) -> str:
    """Generate output image path based on input image names."""
    date_and_time_part = get_date_and_time_part()
    # Order matters.
    return remove_file_extension(reference_image_name) + '-with-' + remove_file_extension(source_image_name) + '-' + date_and_time_part + '.png'


class InputOutputFilePathSpecBuilderForDirectories():
    """
    Build InputOutputFilePathSpec from input and output directories.
    """

    def __init__(self):
        pass

    def build(self, source_dir: str, reference_dir: str, output_dir: str) -> InputOutputFilePathSpec | None:
        """
        Build InputOutputFilePathSpec from input and output directories.
        Assumes input_dir contains pairs of images named as image_0000.png and image_0001.png.
        """
        const_file_extension_tuple = (".png", ".jpg", ".jpeg", ".webp", ".avif")
        try:
            source_files = sorted([f for f in os.listdir(source_dir) if f.endswith(const_file_extension_tuple)])
            reference_files = sorted([f for f in os.listdir(reference_dir) if f.endswith(const_file_extension_tuple)])
        except Exception as e:
            logger.error(f"Error reading directories: {e}")
            return None

        logger.info(source_files)
        logger.info(reference_files)

        spec = InputOutputFilePathSpec()
        for source in source_files:
            for reference in reference_files:
                output_image_name = get_output_image_name(source, reference)
                input_file_path_list = [os.path.join(source_dir, source), os.path.join(reference_dir, reference)]
                output_file_path_list = [os.path.join(output_dir, output_image_name)]
                spec.add_item_with_lists(input_file_path_list, output_file_path_list)

        return spec


def load_config(config_path):
    """
    Load YAML configuration from the specified path.
    """
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def build_input_output_file_path_spec() -> InputOutputFilePathSpec:
    const_source_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'data', 'source')
    const_reference_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'data', 'reference')
    const_output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'data', 'output')
    builder = InputOutputFilePathSpecBuilderForDirectories()
    return builder.build(const_source_dir, const_reference_dir, const_output_dir)


def get_global_config_and_prompt_config():
    global_config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'config', 'global_config.yaml')
    global_config = load_config(global_config_path)
    logger.info(f"Loaded global config: {global_config}")
    prompt_config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'config', 'prompt_config.yaml')
    prompt_config = load_config(prompt_config_path)
    logger.info(f"Loaded prompt config: {prompt_config}")

    return global_config, prompt_config


def build_and_show_input_output_file_path_spec() -> Optional[InputOutputFilePathSpec]:
    input_output_file_path_spec = build_input_output_file_path_spec()

    if input_output_file_path_spec is None:
        logger.error("InputOutputFilePathSpec is None. Exiting.")
        return None

    input_output_file_path_spec.show_input_output_file_path_spec()

    return input_output_file_path_spec


def get_user_input_to_continue() -> bool:
    """
    Get user input to continue or exit.
    """
    while True:
        user_input = input("Input 'continue' to proceed or 'exit' to quit: ")
        if user_input.strip().lower() == 'continue':
            return True
        elif user_input.strip().lower() == 'exit':
            logger.info("Exiting as per user input.")
            return False
        else:
            print("Invalid input. Please type 'continue' or 'exit'.")


def do_main_task():
    """
    Main task function to load config and perform image generation.
    """
    (global_config, prompt_config) = get_global_config_and_prompt_config()
    input_output_file_path_spec = build_and_show_input_output_file_path_spec()
    if not input_output_file_path_spec:
        return
    flag_continue = get_user_input_to_continue()
    if not flag_continue:
        return
    image_generator = ImageGeneratorForGemini()
    image_generator.do_task_with_gemini(global_config['gemini'], prompt_config['gemini'], input_output_file_path_spec)


def main():
    do_main_task()


if __name__ == "__main__":
    main()
