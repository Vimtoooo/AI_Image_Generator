from comfy_generator.file_system import FileSystem
from comfy_generator.exceptions import *
from traceback import format_exc

def file_system_test():
    try:
        fs = FileSystem()
        fs.load_workflow_json()
        print(fs.current_workflows_data)
        fs.load_video_script("my_script.txt")
    except (
        InvalidOperatingSystem,
        NonSettableInstanceException,
        AssetsPathNotFoundError,
        RootProjectFolderNotFoundError,
        IllegalPathAlterationError,
        FileNotFoundError,
        ValueError,
    ) as e:
        print(f"{type(e).__name__}: {e}")
        print(format_exc())
    except Exception as e:
        print(f"Unexpected {type(e).__name__}: {e}")
        print(format_exc())

def main():
    file_system_test()


if __name__ == "__main__":
    main()
