import unittest
from src.image_generator.main import GlobalConfigValidator

class TestGlobalConfigValidator(unittest.TestCase):
    def setUp(self):
        self.validator = GlobalConfigValidator()

    def test_valid_pair_of_directories_config(self):
        config = {
            "global": {
                "input_output_spec": {
                    "type": "pair_of_directories"
                },
                "generate_content_config_key": "some-key"
            },
            "gemini": {
                "api_key": "real-api-key"
            }
        }
        self.assertTrue(self.validator.validate(config))

    def test_valid_single_directory_config(self):
        config = {
            "global": {
                "input_output_spec": {
                    "type": "single_directory"
                }
            },
            "gemini": {
                "api_key": "real-api-key"
            }
        }
        self.assertTrue(self.validator.validate(config))

    def test_missing_global(self):
        config = {
            "gemini": {
                "api_key": "real-api-key"
            }
        }
        self.assertFalse(self.validator.validate(config))

    def test_missing_input_output_spec(self):
        config = {
            "global": {},
            "gemini": {
                "api_key": "real-api-key"
            }
        }
        self.assertFalse(self.validator.validate(config))

    def test_missing_type(self):
        config = {
            "global": {
                "input_output_spec": {}
            },
            "gemini": {
                "api_key": "real-api-key"
            }
        }
        self.assertFalse(self.validator.validate(config))

    def test_invalid_type(self):
        config = {
            "global": {
                "input_output_spec": {
                    "type": "invalid_type"
                }
            },
            "gemini": {
                "api_key": "real-api-key"
            }
        }
        self.assertFalse(self.validator.validate(config))

    def test_default_gemini_api_key(self):
        config = {
            "global": {
                "input_output_spec": {
                    "type": "pair_of_directories"
                }
            },
            "gemini": {
                "api_key": "YOUR GEMINI API KEY"
            }
        }
        self.assertFalse(self.validator.validate(config))

    def test_missing_gemini(self):
        config = {
            "global": {
                "input_output_spec": {
                    "type": "pair_of_directories"
                }
            }
        }
        # Should still pass since gemini is not strictly required for validation
        self.assertTrue(self.validator.validate(config))

if __name__ == "__main__":
    unittest.main()
