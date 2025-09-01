import unittest
from src.image_generator.input_output_file_path_spec import InputOutputFilePathSpec

class TestInputOutputFilePathSpec(unittest.TestCase):
    def setUp(self):
        self.spec = InputOutputFilePathSpec()

    def test_empty_spec(self):
        self.assertEqual(self.spec.get_item_list(), [])

    def test_add_item_with_lists(self):
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

    def test_legacy_add_item(self):
        self.spec.add_item('input0.png', 'input1.png', 'output.png')
        expected = [{
            'input_file_path_list': ['input0.png', 'input1.png'],
            'output_file_path_list': ['output.png']
        }]
        self.assertEqual(self.spec.get_item_list(), expected)

    def test_show_input_output_file_path_spec(self):
        # This test just ensures the method runs without error
        self.spec.add_item_with_lists(['inputA.png', 'inputB.png'], ['outputA.png'])
        try:
            self.spec.show_input_output_file_path_spec()
        except Exception as e:
            self.fail(f"show_input_output_file_path_spec raised an exception: {e}")

if __name__ == '__main__':
    unittest.main()
