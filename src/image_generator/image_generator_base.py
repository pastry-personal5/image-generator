"""

"""
from abc import ABC, abstractmethod
from src.image_generator.main import InputOutputFilePathSpec

class ImageGeneratorBase(ABC):
    @abstractmethod
    def generate_image(self, input_output_file_path_spec: InputOutputFilePathSpec, prompt: str) -> bool:
        pass
