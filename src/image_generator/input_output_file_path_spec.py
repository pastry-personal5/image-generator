"""
Define InputOutputFilePathSpec class.
"""
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