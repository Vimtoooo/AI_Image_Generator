"""
                    ***Utility File***
This file must isolate all file interactions, handling:
* Loading ComfyUI workflow JSON.
* Managing and maneuver through files in the hard drive, along with a few functions.
* Ensures that the output folder `Assets\\Generated_Images` is ready to receive data!
"""

import json
import sys
from pathlib import Path

from exceptions import *

class FileSystem:

    # Class Attributes:
    ALLOWED_PLATFORMS = ("win32", "darwin", "linux")
    
    def __init__(self):
        current_system: str = sys.platform
        if current_system not in self.ALLOWED_PLATFORMS:
            raise InvalidOperatingSystem(f"Only PC operating systems are allowed. Not '{current_system}'")
        self.__system: str = current_system

        self.__path_to_assets: Path = Path(__file__).resolve().parents[3] / "assets" / "generated_images"

    # Getter, setter and deleter methods:
    
    @property
    def system(self) -> str:
        return self.__system
    
    @system.setter
    def system(self, new_system: str):
        raise NonSettableInstanceException("Altering operating systems are not permitted")
    
    @property
    def path_to_assets(self) -> Path:
        return self.__path_to_assets
    
    @path_to_assets.setter
    def path_to_assets(self, new_path: Path):
        if "assets" not in new_path.parts:
            raise AssetsPathNotFoundError(f"The given path does not include the 'assets' folder")

        self.__path_to_assets = new_path