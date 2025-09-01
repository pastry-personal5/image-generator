"""
Define InputOutputFilePathSpec class.
"""
import os

from loguru import logger

class InputOutputFilePathSpec:

    def __init__(self):
        self.item_list = []

    def add_item_with_lists(self, input_file_path_list: list, output_file_path_list: list) -> None:
        """
        Add two lists: input_file_path_list, output_file_path_list.
        """
        self.item_list.append({
            'input_file_path_list': input_file_path_list,
            'output_file_path_list': output_file_path_list
        })

    def add_item(self, input_file_path_0000: str, input_file_path_0001, output_file_path: str):
        self.item_list.append({
            'input_file_path_list': [
                input_file_path_0000,
                input_file_path_0001
            ],
            'output_file_path_list': [
                output_file_path
            ],
        })

    def get_item_list(self):
        return self.item_list

    def show_input_output_file_path_spec(self):
        print("---")
        print("[InputOutputFilePathSpec]")
        for item in self.item_list:
            for x in item['input_file_path_list']:
                print(f"({os.path.basename(x)})", end=" ")
            print("")
        print("---")
