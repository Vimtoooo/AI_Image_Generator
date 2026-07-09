# Autonomous Storyboard Pipeline: ComfyUI Image Generator

![Video Demonstration](assets/readme_assets/project_demonstration.gif)

This directory contains the automated tools designed to simply the generation of images on the fly. The primary application is a **ComfyUI Image Generator** that interacts with a local AI instance to generate custom visual assets programmatically.

**Status:** Completed & Stable (Production ready)

**License:** This repository is licensed under the GNU General Public License v3 (GPLv3). See the [License](License) file for the full text.

## 🤖 ComfyUI Image Generator

This Python application automates the interaction with ComfyUI's API. Instead of manually using the web interface, this script loads predefined workflows, injects dynamic prompts (like the "MS Paint" style defined in our project), and triggers the GPU to generate images.

### 🛠 Prerequisites
The prerequisites below reflect the current state: some automation pieces are implemented, others are planned.

* Having a **GPU** is **highly recommended** for using this system for executing high-demand tasks in your computer.
* **Modern CPU (i5 / AMD Ryzen 5 or above)** helps the computer keep up with all compilation and calculations.

Minimum required to start using the generator today:

1. **ComfyUI installed and running locally** (API accessible). The app expects ComfyUI to be available at a local URL such as `http://127.0.0.1:8188`. Make sure to clone the [official ComfyUI repository here](https://github.com/Comfy-Org/ComfyUI) and export it into a suitable location in your hard drive (recommended near the root file system).
2. **Download your target AI Image Model Checkpoint:** Download your preferred `.safetensors` file from [Civitai](https://civitai.com/) or [Hugging Face](https://huggingface.co/) and place it inside your local `ComfyUI/models/checkpoints/` directory.
3. **Configure your Text-Generation LLM:** Ensure you have access to your recommended external Large Language Model (either locally via **Ollama** or via a cloud API provider) to pre-process your script text into the target keyword schema.
4. **ComfyUI: Dev / API export enabled** so you can Save workflows in the "API Format (JSON)" and place them in `apps/workflows/`.
5. **Python 3.10+** and the project dependencies installed (`pip install -r apps/requirements.txt`).

### 🎛️ AI Model & LLM Pairing Guide

To customize the generation style of the output video frames, configure your local ComfyUI checkpoint directory (`ComfyUI/models/checkpoints/`) with your preferred Base Model, and instruct your prompt-generation LLM to match its corresponding prompt engineering schema:

| Target Visual Goal | Preferred ComfyUI Checkpoint | Recommended External LLM | Prompt Optimization Style |
| :--- | :--- | :--- | :--- |
| **Cinematic Dark Fantasy** | `DreamShaper_8_pruned` (SD 1.5) | Llama 3 / Mistral 7B | Dense comma-separated keyword tokens & modifiers |
| **Photorealism / Documentary**| `Juggernaut_XL_v9` (SDXL) | GPT-4o / Claude 3.5 | Rich descriptive prose, camera lens & daylight specs |
| **Anime & Graphic Manga** | `Animagine_XL_v3` (SDXL) | Qwen2.5 / Command R+ | Pure Danbooru tag arrays (`1girl, weapon, aesthetic`) |
| **Minimalist MS Paint/Sketch**| `v1-5-pruned-emaonly` (Base) | Gemma 2 / DeepSeek-V3 | Primitive object strings, zero artistic adjectives |

#### Generating with Newer Models (SDXL and higher)

Newer generation models like **Flux.1 Shnell, Fluxed up and Persephone**, has an incredible high demand on VRAM, reaching heights of 12GB+. Preparing your launch file for non-dedicated GPUs can be crucial for preventing *Out-of-Memory (OOM) crashes*. To perform generative tasks while maintaining high efficiency, it is encouraged to tell ComfyUI to use a low-memory optimizer:

1. Go to the `ComfyUI_windows_portable` folder.
2. **Right click** on the preferred .bat` file that will open the ComfyUI system and select **Edit**.
3. Certify that the startup command line includes the following:

```bash
.\python_embeded\python.exe -s ComfyUI\main.py --windows-standalone-build --lowvram
```

> 💡 **Portfolio Tip:** Ensure the checkpoint filename inside your ComfyUI directory matches the `ckpt_name` value located inside Node `4` (or your specific canvas Checkpoint Loader Node) within your `comfyui_api.json` workflow file!

### 🚀 Installation & Setup

1.  **Navigate to the App Directory**:
    ```bash
    cd apps
    ```
2.  **Install Dependencies**:
    ```bash
    # Using pip:
    pip install -r requirements.txt

    # Using UV (recommended):
    uv sync
    ```
3.  **Configure Environment**:
    Create or update the `.env` file in `apps` with your local settings:
    ```dotenv
    COMFY_API_URL=http://127.0.0.1:8188
    OUTPUT_DIR=../../Assets/Generated_Images
    WORKFLOW_DIR=./workflows
    ```

### 📋 Execution Steps

1.  **Prepare your Workflow**:
    - Design your workflow in ComfyUI.
    - Use the **"Save (API Format)"** button to export a JSON file.
    - Place this file inside `apps/workflows/` (e.g., `basic_workflow.json`).
2.  **Identify Node IDs**:
    - Open your exported JSON and find the ID for the `CLIPTextEncode` node where you want to inject your prompt (standard IDs are often `6` or `11`).
3.  **Run the Generator**:
    ```bash
    python src/main.py

    # Or
    uv run src/main.py
    ```

### 📂 Project Structure

- `main.py`: The entry point that coordinates the workflow loading, prompt injection, and API calls.
- `__init__.py`: Initializing dependencies.
- `client.py`: Handles all HTTP communication and error checking with the ComfyUI server.
- `file_system.py`: Responsible for managing and maneuvering through files and folders in the hard drive.
- `payload_mgr.py`: Logic for reading, traversing, and modifying the JSON workflow files.
- `/workflows`: Storage for your exported ComfyUI API templates.

Other notable files and folders:

- `apps/src/comfy_generator/file_system.py` — handles project-relative paths and creates the `assets/generated_images` folder automatically; some setter validations and exception handling are implemented and unit tests are currently not included in the repo.
- `apps/src/comfy_generator/exceptions.py` — custom exception classes used by the generator utilities.
- `assets/generated_images/` — target directory for generated images (created automatically by the file system helper when the code runs).
- `prompts/` and `scripts/` — contain prompt templates and timestamped script fragments referenced by the generator.

Testing and CI:

- There are no automated tests or CI configuration included yet. Adding `pytest` tests for error paths (file not found, invalid platform, setters) is recommended.

### Architecture & Design Patters:

* **Strict Decoupling:** Modules communicate via a master orchestrator (`main.py`) to prevent coupling vulnerabilities.
* **Memory Sandbox Isolation:** `PayloadManager` utilizes deep memory copying (`copy.deepcopy()`) to prevent reference mutations across frames.
* **Persistent WebSocket Streaming:** The client utilizes a blocking network listener thread to intercept downstream completion event packets without polling.

### Current Tasks:

1. `file_system.py`:
    - [x] **Path Management**: Define where everything lives in the working directory, especially making it dynamical to locate the project's root folder and the `Assets` folder. Avoid hardcoding strings for defining paths, and use the built-in `pathlib` module and utilize the `__file__` variable to anchor paths relatively.
    - [x] **Workflow Loading**: Read the ComfyUI Canvas configuration, by creating a function that opens the `workflow_api.json` file, parses its contents, and returns it as a native Python dictionary so other scripts can modify it later. Use proper file-handling blocks like `with open(...)` to ensure files close automatically, and consider how to catch errors if the file is missing or corrupted.
    - [x] **Asset Preparation**: Prepare a landing pad for the generated images, making another function that verifies if the `Assets` directory exists. If it does not exist yet, create it automatically on the fly. Use `pathlib` for creating these directories safely without throwing an error if the directory already exists.
    - [x] **Dynamic File Identification**: Methods can read through folders and automatically identify whether there is one specific file present, creating a smarter program to create filename paths autonomously.

2. `client.py`:
    - [x] **Server Address Configurations:** Define where the ComfyUI engine resides, store base configurations for hostnames and ports (like `127.0.0.1:8188`), requiring a unique identification string (with `uuid.uuid4()` to generate a unique token for the client instance).
    - [x] **The Base Health Connection Check:** Confirm the AIP server is alive before running intensive tasks. Create a standard connectivity function for making basic `GET` requests using the `requests` library to a simple ComfyUI checking endpoint (such as `/system_stats` or `/history`), returning a clean boolean state (`True`/`False`).
    - [x] **The HTTP Loader:** Submits workflow execution orders, with a function that is capable of accepting your configures workflow dictionary, wraps it in a secure transaction template, and ships it via a `POST` request directly to ComfyUI's `/prompt` endpoint.

3. `payload_mgr.py`:
    - [x] **Node Key Mapping (The Directory Coordinates):** Prevent the code from filling up with confusing raw strings and arbitrary string numbers (`"3"`, `"6"`, or `"24"`). Making a manager class that maps these abstract numbers to human-readable names using **Class Constants** or internal, private instance attributes, defining variables that state exactly which noe index holds the position prompt text field.
    - [x] **Workflow State Holder:** Hold a temporary working copy of your graph dictionary in an instance variable. This is crucial for making *reference safety*, since Python dictionaries are passed by **reference**. If the manager mutates a dictionary directly, it will modify the original version sitting inside the `FileSystem` classe. Prevent the structural memory pollution across loops by using Python's built-in `copy.deepcopy()` to clone a clean, isolated version of the graph every time it is loaded.

4. `main.py`:
    - [x] **The initialization Sequence:** Instantiate core modules sequentially, while checking the server's initial health status, loading the target configuration assets and retrieving the data payload straight into your data mutation module.
    - [x] **Dynamic Loop Orchestration:** The generations runner loop should step through the time-stamped files line by line, separating the timestamp data from the core scene description text and execute a chain mutation for every independent line item. Run the chain mutation sequence to prepare a distinct frame.
    - [x] **Execution and Handoff Routing:** Responsible for transferring the newly calculated `ready_graph` dictionary payload directly into your network submitter: `prompt_id = comfy_client.queue_workflow(ready_graph)`. Pass the active execution identifier token straight into the tracker block: `comfy_client.track_generation_progress(prompt_id)`. Once the websocket loop hits its exit condition and breaks, it'll mean that ComfyUI has successfully dropped your newly generated image directly into the user's computer output file space!

## 📈 Future Roadmap

- [x] **Polling Mechanism**: Implement real-time status checking to wait for generation completion.
- [x] **Automatic Retrieval**: Automatically download and rename images based on script timestamps.
- [x] **Utility Classes**: Simplify the code exhibition by separating what must be considered as an utility and helper action.
- [x] **Addition to Flexibility**: Be able to optionally select files in folders, swapping models.
- [ ] **Simple UI**: Easy to use UI for quickly configuring options and generating images.