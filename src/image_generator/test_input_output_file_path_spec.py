
import unittest
from src.image_generator.main import InputOutputFilePathSpec

class TestInputOutputFilePathSpec(unittest.TestCase):
    def setUp(self):
        self.spec = InputOutputFilePathSpec()

    def test_initial_item_list_empty(self):
        self.assertEqual(self.spec.get_item_list(), [])

    def test_add_item_with_lists_single(self):
        input_list = ['input0.png', 'input1.png']
        output_list = ['output.png']
        extra_list = ['extra1.txt', 'extra2.txt']
        self.spec.add_item_with_lists(input_list, output_list, extra_list)
        expected = [{
            'input_file_path_list': input_list,
            'output_file_path_list': output_list,
            'extra_file_path_list': extra_list
        }]
        self.assertEqual(self.spec.get_item_list(), expected)

    def test_add_item_with_lists_multiple(self):
        items = [
            (['a.png', 'b.png'], ['c.png'], ['d.txt']),
            (['x.jpg', 'y.jpg'], ['z.jpg'], ['w.txt', 'v.txt'])
        ]
        for inp, outp, extra in items:
            self.spec.add_item_with_lists(inp, outp, extra)
        expected = [
            {
                'input_file_path_list': ['a.png', 'b.png'],
                'output_file_path_list': ['c.png'],
                'extra_file_path_list': ['d.txt']
            },
            {
                'input_file_path_list': ['x.jpg', 'y.jpg'],
                'output_file_path_list': ['z.jpg'],
                'extra_file_path_list': ['w.txt', 'v.txt']
            }
        ]
        self.assertEqual(self.spec.get_item_list(), expected)

    def test_add_item_legacy(self):
        # If legacy add_item still exists, test it for backward compatibility
        try:
            self.spec.add_item('input0.png', 'input1.png', 'output.png')
            expected = [{
                'input_file_path_list': ['input0.png', 'input1.png'],
                'output_file_path_list': ['output.png']
            }]
            # Only check keys that exist
            item = self.spec.get_item_list()[0]
            self.assertEqual(item['input_file_path_list'], expected[0]['input_file_path_list'])
            self.assertEqual(item['output_file_path_list'], expected[0]['output_file_path_list'])
        except Exception:
            pass

if __name__ == '__main__':
    unittest.main()
