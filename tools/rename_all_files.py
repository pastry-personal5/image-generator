import os
import sys
import re


def rename_files_in_directory(directory: str):
    """
    Renames files in the given directory that match the regex pattern,
    replacing the matched part with the replacement string.
    """
    pattern = r'beauty_(.*).jpeg'
    for filename in os.listdir(directory):
        result = re.match(pattern, filename)
        if result:
            new_filename = f"b{result.group(1)}.jpeg"
            try:
                os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename))
                print(f"Renamed: {filename} -> {new_filename}")
            except Exception as e:
                print(f"Error renaming {filename} to {new_filename}: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python rename_all_files.py <directory>")
        print(r"Example: python rename_all_files.py ./images")
        sys.exit(1)
    directory = sys.argv[1]
    rename_files_in_directory(directory)
