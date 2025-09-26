"""
Define main functions for image generation.
"""
import os
from typing import Optional
import yaml

from loguru import logger

from src.image_generator.image_generator_generate_content_config import ImageGeneratorGenerateContentConfig
from src.image_generator.image_generator_for_gemini import ImageGeneratorForGemini
from src.image_generator.input_output_file_path_spec import InputOutputFilePathSpec
from src.image_generator.input_output_file_path_spec_builder import InputOutputFilePathSpecBuilderForPairOfDirectories


class GlobalConfigEnum:
    const_type_pair_of_directories = "pair_of_directories"
    const_type_single_directory = "single_directory"


class GlobalConfigValidator:

    def __init__(self):
        pass

    def validate(self, config: dict) -> bool:
        if 'global' not in config:
            logger.error("Missing 'global' in global config.")
            return False
        if 'input_output_spec' not in config['global']:
            logger.error("Missing 'input_output_spec' in global config.")
            return False
        if 'type' not in config['global']['input_output_spec']:
            logger.error("Missing 'type' in 'input_output_spec' in global config.")
            return False
        if config['global']['input_output_spec']['type'] not in [
            GlobalConfigEnum.const_type_pair_of_directories,
            GlobalConfigEnum.const_type_single_directory
        ]:
            logger.error(f"Invalid 'type' in 'input_output_spec': {config['global']['input_output_spec']['type']}")
            return False

        # Gemini-specific
        if config.get('gemini'):
            if config['gemini'].get('api_key'):
                const_default_gemini_api_key_template_string = "YOUR GEMINI API KEY"
                if config['gemini']['api_key'] == const_default_gemini_api_key_template_string:
                    logger.error("Please specify a Gemini API key.")
                    return False

        return True


class GlobalConfig:

    def __init__(self, config: dict):
        self.config = config

    def validate(self) -> bool:
        validator = GlobalConfigValidator()
        return validator.validate(self.config)


class MainController:
    """
    Main controller for image generation.
    """

    def __init__(self):
        pass

    def _load_config(self, config_path):
        """
        Load YAML configuration from the specified path.
        """
        with open(config_path, encoding="utf-8", mode="r") as f:
            return yaml.safe_load(f)

    def _get_global_config_and_generate_content_config(self) -> Optional[tuple[GlobalConfig, ImageGeneratorGenerateContentConfig]]:
        """
        Load global and generate content configurations.
        """
        global_config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'config', 'global_config.yaml')
        global_config = self._load_config(global_config_path)
        generate_content_config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'config', 'generate_content_config.yaml')
        generate_content_config = self._load_config(generate_content_config_path)

        global_config_object = GlobalConfig(global_config)
        if not global_config_object.validate():
            logger.error("Invalid global configuration. Exiting.")
            return None, None

        generate_content_config_key = global_config_object.config['global'].get('generate_content_config_key', 'default')
        if generate_content_config_key not in generate_content_config:
            logger.error(f"Generate content config key '{generate_content_config_key}' not found in prompt configuration. Exiting.")
            return None, None
        prompt = generate_content_config[generate_content_config_key].get('prompt', None)

        image_generator_generate_content_config = ImageGeneratorGenerateContentConfig()
        image_generator_generate_content_config.set_prompt(prompt)
        if 'temperature' in generate_content_config[generate_content_config_key]:
            image_generator_generate_content_config.set_temperature(generate_content_config[generate_content_config_key]['temperature'])
        if 'top_p' in generate_content_config[generate_content_config_key]:
            image_generator_generate_content_config.set_top_p(generate_content_config[generate_content_config_key]['top_p'])

        return global_config_object, image_generator_generate_content_config

    def _build_input_output_file_path_spec(self, global_config_object: GlobalConfig) -> InputOutputFilePathSpec:
        const_source_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'data', 'source')
        const_reference_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'data', 'reference')
        const_output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'data', 'output')

        if global_config_object.config['global']['input_output_spec']['type'] == GlobalConfigEnum.const_type_single_directory:
            from src.image_generator.input_output_file_path_spec_builder import InputOutputFilePathSpecBuilderForSingleDirectory
            builder = InputOutputFilePathSpecBuilderForSingleDirectory()
            return builder.build(const_source_dir, const_output_dir)
        elif global_config_object.config['global']['input_output_spec']['type'] == GlobalConfigEnum.const_type_pair_of_directories:
            builder = InputOutputFilePathSpecBuilderForPairOfDirectories()
            return builder.build(const_source_dir, const_reference_dir, const_output_dir)
        else:
            logger.error(f"Unsupported input_output_spec type: {global_config_object.config['global']['input_output_spec']['type']}")
            return None

    def _build_and_show_input_output_file_path_spec(self, global_config_object: GlobalConfig) -> Optional[InputOutputFilePathSpec]:
        input_output_file_path_spec = self._build_input_output_file_path_spec(global_config_object)

        if input_output_file_path_spec is None:
            logger.error("InputOutputFilePathSpec is None. Exiting.")
            return None

        input_output_file_path_spec.show_input_output_file_path_spec()

        return input_output_file_path_spec

    def _get_user_input_to_continue(self) -> bool:
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

    def do_main_task(self):
        """
        Main task function to load config and perform image generation.
        """
        (global_config_object, image_generator_generate_content_config) = self._get_global_config_and_generate_content_config()
        if not global_config_object or not image_generator_generate_content_config:
            return
        input_output_file_path_spec = self._build_and_show_input_output_file_path_spec(global_config_object)
        if not input_output_file_path_spec:
            return
        flag_continue = self._get_user_input_to_continue()
        if not flag_continue:
            return
        if global_config_object.config.get('gemini'):
            image_generator = ImageGeneratorForGemini()
            model_specific_config = global_config_object.config['gemini']
            image_generator.do_generation(model_specific_config, image_generator_generate_content_config, input_output_file_path_spec)
        else:
            logger.error("Gemini is not configured. Exiting.")
            return


def main():
    main_controller = MainController()
    main_controller.do_main_task()


if __name__ == "__main__":
    main()
