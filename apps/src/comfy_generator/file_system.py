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
from typing import Final, Never

from exceptions import *

class FileSystem:

    # Class Attributes:
    ALLOWED_PLATFORMS: Final[tuple[str, str, str]] = ("win32", "darwin", "linux")
    
    def __init__(self):
        current_system: str = sys.platform

        if not any(current_system.startswith(p) for p in self.ALLOWED_PLATFORMS):
            raise InvalidOperatingSystem(f"Only PC operating systems are allowed. Not '{current_system}'")
        self.__system: str = current_system

        # Store the path to the root of the project
        self.__project_root: Path = Path(__file__).resolve().parents[3]
        
        # Current Path of Script -> cleans up path by starting from the root of the hard drive -> goes 4 levels upward -> overrides 'pathlib' to join the other paths
        self.__path_to_assets: Path = self.__project_root / "assets" / "generated_images"

        # If the path to the assets and generated_images folder does not exist, it'll make it automatically
        self.__path_to_assets.mkdir(parents=True, exist_ok=True)

        # Store the path to the workflows folder
        self.__path_to_workflows: Path = self.__project_root / "apps" / "workflows"

        # Path to prompts folder
        self.__path_to_prompts: Path = self.__project_root / "prompts"

        # Path to scripts folder
        self.__path_to_scripts: Path = self.__project_root / "scripts"

        # Store the current workflow data from the ComfyUI's API and maintain it's parsed data as a Python dictionary
        self.__current_workflow_data: dict | None = None

    # Getter, setter and deleter methods:
    
    @property
    def system(self) -> str:
        return self.__system
    
    @system.setter
    def system(self, new_system: str) -> Never:
        raise NonSettableInstanceException(f"Altering operating systems are not permitted. Given argument: {new_system}")
    
    @property
    def path_to_assets(self) -> Path:
        return self.__path_to_assets
    
    @path_to_assets.setter
    def path_to_assets(self, new_path: Path):
        if not isinstance(new_path, Path):
            raise ValueError(f"Invalid data type for the argument 'new_path': {new_path}")

        if "assets" not in new_path.parts:
            raise AssetsPathNotFoundError(f"The given path does not include the 'assets' folder")

        if not new_path.is_relative_to(self.__project_root):
            raise RootProjectFolderNotFoundError("The given path is not related to the project root folder")

        self.__path_to_assets = new_path
        self.__path_to_assets.mkdir(parents=True, exist_ok=True)

    @property
    def project_root(self) -> Path:
        return self.__project_root
    
    @project_root.setter
    def project_root(self, new_path: Path) -> Never:
        raise IllegalPathAlterationError(f"Altering root project paths is forbidden. Given argument: {new_path}")
    
    @property
    def path_to_workflows(self) -> Path:
        return self.__path_to_workflows
    
    @path_to_workflows.setter
    def path_to_workflows(self, new_path: Path) -> Never:
        raise IllegalPathAlterationError(f"Altering the workflows path is forbidden. Given argument: {new_path}")
    
    @property
    def path_to_prompts(self) -> Path:
        return self.__path_to_prompts
    
    @path_to_prompts.setter
    def path_to_prompts(self, new_path: Path) -> Never:
        raise IllegalPathAlterationError(f"Altering the prompts path is forbidden. Given argument: {new_path}")
    
    @property
    def path_to_scripts(self) -> Path:
        return self.__path_to_scripts
    
    @path_to_scripts.setter
    def path_to_scripts(self, new_path: Path) -> Never:
        raise IllegalPathAlterationError(f"Altering the scripts path is forbidden. Given argument: {new_path}")
    
    @property
    def current_workflows_data(self) -> dict | None:
        return self.__current_workflow_data
    
    @current_workflows_data.setter
    def current_workflows_data(self, new_workflows_data: dict | None) -> None:
        if not isinstance(new_workflows_data, dict):
            raise ValueError(f"Invalid data type for the argument 'new_workflows_data': {new_workflows_data}")
        
        if not any(self.__path_to_workflows.glob("comfyui_api.json")):
            raise FileNotFoundError(f"The 'comfyui_api.json' file is not present in the workflows folder. Current path: {self.__path_to_workflows}")
        
        self.__current_workflow_data = new_workflows_data