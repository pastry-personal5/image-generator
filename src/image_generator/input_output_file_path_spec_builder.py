"""
Build InputOutputFilePathSpec from input and output directories.
"""
from datetime import datetime
import os

from loguru import logger

from src.image_generator.input_output_file_path_spec import InputOutputFilePathSpec


def remove_file_extension(file_path):
    """
    Removes the file extension from a file path.
    Example: 'path/to/image.jpg' -> 'path/to/image'
    """
    return os.path.splitext(file_path)[0]


def get_date_and_time_part() -> str:
    """Get current date and time as a string."""

    now = datetime.now()
    return now.strftime("%Y%m%d-%H%M%S")


def get_output_image_names(source_image_name: str, reference_image_name: str) -> tuple[str, str]:
    """Generate output image path based on input image names."""
    date_and_time_part = get_date_and_time_part()
    # Order matters.
    file_name_0000 =  remove_file_extension(reference_image_name) + '-applied-to-' + remove_file_extension(source_image_name) + '-' + date_and_time_part + '.png'
    file_name_0001 =  remove_file_extension(source_image_name) + '-transferred-from-' + remove_file_extension(reference_image_name) + '-' + date_and_time_part + '.png'
    return file_name_0000, file_name_0001


class InputOutputFilePathSpecBuilderForDirectories:
    """
    Build InputOutputFilePathSpec from input and output directories.
    """

    def __init__(self):
        pass

    def build(self, source_dir: str, reference_dir: str, output_dir: str) -> InputOutputFilePathSpec | None:
        """
        Build InputOutputFilePathSpec from input and output directories.
        Assumes input_dir contains pairs of images named as image_0000.png and image_0001.png.
        """
        const_file_extension_tuple = (".png", ".jpg", ".jpeg", ".webp", ".avif")
        try:
            source_files = sorted([f for f in os.listdir(source_dir) if f.endswith(const_file_extension_tuple)])
            reference_files = sorted([f for f in os.listdir(reference_dir) if f.endswith(const_file_extension_tuple)])
        except (FileNotFoundError, NotADirectoryError, PermissionError, OSError) as e:
            logger.error(f"Error reading directories: {e}")
            return None

        logger.info(source_files)
        logger.info(reference_files)

        spec = InputOutputFilePathSpec()
        for source in source_files:
            for reference in reference_files:
                output_image_names = get_output_image_names(source, reference)
                logger.info(output_image_names)
                input_file_path_list = [os.path.join(source_dir, source), os.path.join(reference_dir, reference)]
                output_file_path_list = []
                output_file_path_list.append(os.path.join(output_dir, output_image_names[0]))
                output_file_path_list.append(os.path.join(output_dir, output_image_names[1]))
                spec.add_item_with_lists(input_file_path_list, output_file_path_list)

        return spec
