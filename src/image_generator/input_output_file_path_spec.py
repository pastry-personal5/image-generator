"""
Define InputOutputFilePathSpec class.
"""
import os
from loguru import logger


class InputOutputFilePathSpec:

    def __init__(self):
        self.item_list = []

    def add_item_with_lists(self, input_file_path_list: list[str], output_file_path_list: list[str]) -> None:
        """
        Add two lists: input_file_path_list, output_file_path_list.
        """
        self.item_list.append({
            'input_file_path_list': input_file_path_list,
            'output_file_path_list': output_file_path_list
        })

    def get_item_list(self) -> list[dict[str, list[str]]]:
        return self.item_list

    def show_input_output_file_path_spec(self) -> None:
        """
        Print the input and output file path specification.
        """
        logger.info("---")
        logger.info("[InputOutputFilePathSpec]")
        logger.info("[Input Files]")
        for item in self.item_list:
            for x in item['input_file_path_list']:
                logger.info(f"({os.path.basename(x)}) ")
        logger.info("---")
        logger.info("[Output Files]")
        for item in self.item_list:
            for x in item['output_file_path_list']:
                logger.info(f"({os.path.basename(x)}) ")
        logger.info("---")
