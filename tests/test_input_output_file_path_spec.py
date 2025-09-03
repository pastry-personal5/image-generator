"""
Unit tests for the InputOutputFilePathSpec class.
"""

import unittest
from src.image_generator.input_output_file_path_spec import InputOutputFilePathSpec

class TestInputOutputFilePathSpec(unittest.TestCase):
    def setUp(self):
        self.spec = InputOutputFilePathSpec()

    def test_initial_state_is_empty(self):
        self.assertEqual(self.spec.get_item_list(), [])

    def test_add_item_with_lists_adds_correctly(self):
        input_files = ['inputA.png', 'inputB.png']
        output_files = ['outputA.png']
        self.spec.add_item_with_lists(input_files, output_files)
        expected = [{
            'input_file_path_list': input_files,
            'output_file_path_list': output_files
        }]
        self.assertEqual(self.spec.get_item_list(), expected)

    def test_add_multiple_items_with_lists(self):
        items = [
            (['a.png', 'b.png'], ['c.png']),
            (['x.jpg', 'y.jpg'], ['z.jpg'])
        ]
        for inp, outp in items:
            self.spec.add_item_with_lists(inp, outp)
        expected = [
            {
                'input_file_path_list': ['a.png', 'b.png'],
                'output_file_path_list': ['c.png']
            },
            {
                'input_file_path_list': ['x.jpg', 'y.jpg'],
                'output_file_path_list': ['z.jpg']
            }
        ]
        self.assertEqual(self.spec.get_item_list(), expected)

    def test_show_input_output_file_path_spec_does_not_raise(self):
        self.spec.add_item_with_lists(['inputA.png', 'inputB.png'], ['outputA.png'])
        try:
            self.spec.show_input_output_file_path_spec()
        except Exception as e:
            self.fail(f"show_input_output_file_path_spec raised an exception: {e}")
