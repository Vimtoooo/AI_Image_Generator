from typing import Final
from random import randint
from pathlib import Path
from comfy_generator.exceptions import (
    InvalidFileTypeError
)

"""Utility file for handling aspect-ration, output paths and math calculations."""

WIDTH: Final[int] = 720
HEIGHT: Final[int] = 720

PERMITTED_ASPECT_RATIOS: Final[tuple[str, ...]] = (
    "16:9", "9:16", "custom"
)
PERMITTED_FILE_TYPES: Final[tuple[str, ...]] = (
    "json", "txt", "png", "jpg", "jpeg"
)


def calculate_landscape_dimensions(width: int | None = None, height: int | None = None) -> tuple[int, int]:
    """
    Calculates the recommended aspect ratio for a 16:9 display.
    
    <h4>Throws</h4>

    - **ValueError:** If the argument's data type is invalid.
    """

    if not isinstance(width, (int, type(None))):
        raise ValueError(f"Invalid dimension input data type for the argument 'width'. Given: {type(width)}")
    
    if not isinstance(height, (int, type(None))):
        raise ValueError(f"Invalid dimension input data type for the argument 'height'. Given: {type(height)}")
    
    if width is None and height is None:
        return (WIDTH, HEIGHT)
    
    if height is not None and width is None:
        return (int(height * 16 // 9), height)
    
    if width is not None and height is None:
        return (width, int(width * 9 // 16))
    
    if width is not None and height is not None:
        # Logical resolution (SCALE TO FIT) when BOTH width and height are provided:
        # Verify which dimension is the "bottleneck" for a 16:9 box.
        if width // height > 16 // 9:
            return (int(height * 16 // 9), height)  # Width is too wide; the height is the limiting constraint
        return (width, int(width * 9 // 16))  # Height is too tall; the width is the limiting constraint
    
    raise ValueError("Invalid dimension inputs for landscape calculation")

def calculate_portrait_dimensions(width: int | None = None, height: int | None = None) -> tuple[int, int]:
    """
    Calculates 9:16 portrait dimensions, prioritizing containment if both are
    provided.
    
    <h4>Throws</h4>

    - **ValueError:** If the argument's data type is invalid.
    """

    if not isinstance(width, (int, type(None))):
        raise ValueError(f"Invalid dimension input data type for the argument 'width'. Given: {type(width)}")
    
    if not isinstance(height, (int, type(None))):
        raise ValueError(f"Invalid dimension input data type for the argument 'height'. Given: {type(height)}")
    
    if width is None and height is None:
        return (WIDTH, HEIGHT)
    if height is not None and width is None:
        return (int(height * 9 // 16), height)
    
    if width is not None and height is None:
        return (width, int(width * 16 // 9))
    
    if width is not None and height is not None:
        # Compare the aspect ratio against 16:9 to determine the limiting dimension.
        if height // width > 16 // 9:
            return (width, int(width * 16 // 9))
        return (int(height * 9 // 16), height)
    
    raise ValueError("Invalid dimension inputs for portrait calculation")

def generate_random_seed() -> int:
    """Generates a random seed between `100000000000000` and `999999999999999`."""
    return randint(100000000000000, 999999999999999)

def define_filename_path(path_to_folder: Path, filename: str, file_type: str) -> Path:
    """
    Defines a path directly to the passed filename, which can be of a certain
    given file type.

    <h4>Throws:</h4>

    - **ValueError:** If the argument's data type is invalid or not implemented.
    - **FileNotFoundError:** If the file is not located in the hard drive or
    is not a valid directory folder.
    - **InvalidFileTypeError:** If given an unsupported file type extension.
    """

    # 1. Parameter Type Validation
    if not isinstance(path_to_folder, Path):
        raise ValueError(f"Invalid data type for the argument 'path_to_folder'. Given: {type(path_to_folder)}")
    
    if not isinstance(filename, str):
        raise ValueError(f"Invalid data type for the argument 'filename'. Given: {type(filename)}")
    
    if not isinstance(file_type, str):
        raise ValueError(f"Invalid data type for the argument 'file_type'. Given: {type(file_type)}")
    
    # 2. String Presence Validation
    cleaned_filename = filename.strip()
    if not cleaned_filename:
        raise ValueError("The argument 'filename' cannot be empty or blank whitespace.")
    
    cleaned_file_type = file_type.strip()
    if not cleaned_file_type:
        raise ValueError("The argument 'file_type' cannot be empty or blank whitespace.")
    
    # 3. Normalization & Extension Safety Check
    normalized_type = cleaned_file_type.lstrip(".").lower()
    if normalized_type not in PERMITTED_FILE_TYPES:
        raise InvalidFileTypeError(
            f"Unsupported file type extension: '{file_type}'. "
            f"Permitted extensions are: {PERMITTED_FILE_TYPES}"
        )
    
    # 4. Fixed Safety Rail: Disambiguate folder locations from file paths
    if not path_to_folder.is_dir():
        raise FileNotFoundError(f"The path target is missing or is not a valid directory folder: {path_to_folder}")
    
    # 5. Fixed Safety Rail: Eliminate double extension defects (e.g., 'image.png' -> 'image')
    safe_stem = Path(cleaned_filename).stem
    
    # 6. Fixed Safety Rail: Clean out destructive cross-platform OS filesystem characters
    for forbidden_char in ['<', '>', ':', '"', '/', '\\', '|', '?', '*']:
        safe_stem = safe_stem.replace(forbidden_char, "")
        
    if not safe_stem:
        raise ValueError("The filename contains only illegal filesystem characters.")
    
    # 7. Build and return the completely secure file path
    final_path: Path = path_to_folder / f"{safe_stem}.{normalized_type}"
    return final_path