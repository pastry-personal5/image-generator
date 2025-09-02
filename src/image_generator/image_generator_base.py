"""
Abstract base class for image generators in the image-generator project.
Defines the interface for image generation implementations.
"""

from abc import ABC, abstractmethod
from src.image_generator.input_output_file_path_spec import InputOutputFilePathSpec


class ImageGeneratorBase(ABC):
    @abstractmethod
    def generate_one_batch_of_images(self, input_output_file_path_spec: InputOutputFilePathSpec, prompt: str) -> bool:
        pass
