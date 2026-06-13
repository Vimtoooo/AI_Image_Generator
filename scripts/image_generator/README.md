# Image Generator — ComfyUI

Generates MS Paint-style stickman images for every timestamp in a YouTube script.
Prefers a local ComfyUI API (recommended) or local AUTOMATIC1111 WebUI; a remote
Pollinations.AI endpoint is available as a fallback but may be rate-limited.

---

## Setup

> **Requires:** Python 3.10+ and [UV](https://docs.astral.sh/uv/getting-started/installation/)

### 1. Install UV (if you haven't already)
```powershell
pip install uv
```

### 2. Navigate to this folder and install dependencies
```powershell
cd scripts\image_generator
uv sync
```

If you are not using `uv`, or you run the script directly with `python`, ensure required packages are installed into the interpreter you will use:

```powershell
python -m pip install requests
```

### Where to store scripts

- Use the existing `scripts/` folder as the top-level place for utility scripts.
- For this generator, keep files under `scripts/image_generator/` (the current
	location) so everything related to image generation (script, workflows, README)
	stays together and is easy to version. If you add auxiliary helpers, consider
	`scripts/utils/` or `scripts/tools/` for shared scripts.
- Storing them in the root `scripts/` folder is fine for general utilities; keep
	project-specific scripts inside `scripts/<tool-name>/`.

### Troubleshooting: "module not found" errors

- If you see an import error like `ModuleNotFoundError: No module named 'requests'`, you're likely running the script with a different Python interpreter than the one where dependencies were installed.
- Fixes:
	- Activate the same environment `uv` is using, or install into the interpreter you run: `python -m pip install -r requirements.txt`.
	- Verify `python` points to the expected interpreter: `python -c "import sys; print(sys.executable)"`.
	- After installing, re-run `uv run generate_images.py` (or `python generate_images.py`).

### 3. Run the generator
```powershell
uv run generate_images.py
```

That's it! Images will be saved to `assets/Generated_Images/` with timestamp filenames.

---

## How it works

- Prefers a running ComfyUI API (local) and will send your exported workflow JSON
	when available. This gives the most reliable results for batch generation.
- If ComfyUI is not reachable, the generator falls back to a local AUTOMATIC1111
	WebUI if `LOCAL_SD_URL` is set.
- As a last resort the script can call Pollinations.AI (remote) but that service is
	rate-limited and may return `402` queue responses.
- Generates each image at **1920×1080 (16:9)** in MS Paint stickman style.
- Skips images that already exist (safe to re-run) and auto-retries failed images up to 3 times.

## Rate limits and 402 responses (Pollinations fallback)

If the script falls back to Pollinations.AI it may return HTTP `402` with a JSON
body indicating "Queue full for IP" when the remote endpoint is busy. The
generator implements exponential backoff on `402` responses but high-volume use
should be done with a local backend (ComfyUI/AUTOMATIC1111).

Options when seeing 402 responses:
- Wait and re-run later (the queue clears over time).
- Sign up at https://enter.pollinations.ai for higher/unlimited access.
- Use a local ComfyUI or AUTOMATIC1111 WebUI for unlimited local generations.

## Local Stable Diffusion (recommended for high-volume use)

If you have an NVIDIA GPU (like an RTX 3050), running Stable Diffusion locally is one option. This repository is now focused on ComfyUI as the primary backend. The generator expects a running ComfyUI API by default.

Quick overview (AUTOMATIC1111 WebUI) — OPTIONAL fallback (not required):

1. Install NVIDIA drivers and CUDA runtime (use latest stable drivers from NVIDIA).
2. Install Miniconda (recommended) on Windows.
3. Open a PowerShell terminal and run:

```powershell
cd %USERPROFILE%\Downloads
git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git
cd stable-diffusion-webui
.
# On Windows use the bundled webui-user.bat which sets up the environment and deps
./webui-user.bat
```

4. The WebUI will start and be available at `http://127.0.0.1:7860` by default.
5. In this generator, set the environment variable `LOCAL_SD_URL` to that URL before running:

```powershell
setx LOCAL_SD_URL "http://127.0.0.1:7860"
```

Security & safety notes:

- Installing and running Stable Diffusion locally is generally safe if you use official repositories and releases. Avoid running untrusted scripts from unknown sources.
- Ensure your GPU drivers and Windows updates are current; running models uses system resources and should be monitored for temperature.
- Some model checkpoints may have licensing or usage restrictions — only download models from trusted sources and respect their licenses.

If you'd like, I can add a `--local` CLI flag and small example scripts to automate starting the WebUI and running a batch.

### ComfyUI API integration (preferred)

This generator calls a running ComfyUI API when available. To enable it:

1. Start ComfyUI and install an API extension (if required by your ComfyUI build).
2. Export or save a workflow JSON (e.g. `gsl_starter_1_1.json`) into the
	repository (recommended path shown below).
3. Configure environment variables and run

Set persistent environment variables (PowerShell, user-level):

```powershell
setx COMFY_API_URL "http://127.0.0.1:8188"
setx COMFY_WORKFLOW_PATH "C:\path\to\gsl_starter_1_1.json"
setx SCRIPT_PATH "C:\path\to\your_script.txt"  # optional default script path
```

Set variables for the current PowerShell session only (useful for testing):

```powershell
$env:COMFY_API_URL = "http://127.0.0.1:8188"
$env:COMFY_WORKFLOW_PATH = "C:\path\to\gsl_starter_1_1.json"
$env:SCRIPT_PATH = "C:\path\to\your_script.txt"
```

On macOS / Linux (bash/zsh) set for the session:

```bash
export COMFY_API_URL="http://127.0.0.1:8188"
export COMFY_WORKFLOW_PATH="/full/path/to/gsl_starter_1_1.json"
export LOCAL_SD_URL="http://127.0.0.1:7860"
export SCRIPT_PATH="/full/path/to/your_script.txt"
```

Install dependencies and sync `uv` (if using `uv`) then run the generator:

```powershell
# from repo root
cd scripts\image_generator
uv sync           # installs deps into uv-managed environment
uv run generate_images.py --script ..\..\prompts\my_video_script.txt
```

Or run directly with your Python interpreter (no uv):

```powershell
python .\scripts\image_generator\generate_images.py --comfy-url http://127.0.0.1:8188 --script .\prompts\my_video_script.txt
```

Notes:
- `--script` overrides `SCRIPT_PATH` environment variable for that run.
- Recommended workflow location: `scripts/image_generator/workflows/gsl_starter_1_1.json`.
- The script sanitizes timestamps to produce safe filenames (for example `0:02` → `0.02.png`).

Notes:
- The script will try several common ComfyUI API endpoints and payload shapes. If your API exposes a different path, set `COMFY_API_URL` to include that path (for example `http://127.0.0.1:8188/api/generate`).
- The script will try several common ComfyUI API endpoints and payload shapes. If your API exposes a different path, set `COMFY_API_URL` to include that path (for example `http://127.0.0.1:8188/api/generate`).
- The script searches the JSON response for base64-encoded images (data:image/* or plain base64 strings) and saves the first image it finds.

Recommended location for exported workflows (keeps them with the generator):

`scripts/image_generator/workflows/gsl_starter_1_1.json`

If you want, I can add a small helper that verifies your ComfyUI endpoint and prints a test image before running the full batch.

---

## Reusing for future videos

1. Open `generate_images.py`
2. Replace the entries in the `IMAGES` list with your new timestamps and scene descriptions
3. Run `uv run generate_images.py` again

Each entry follows the format:
```python
("timestamp", "scene description for this frame"),
```

Example:
```python
("0.05", "stick figure walking into a door labeled BANK, confused face"),
```

---

## Configuration

All settings are at the top of `generate_images.py`:

| Setting | Default | Description |
|---|---|---|
| `OUTPUT_DIR` | `Assets/Generated_Images` | Where images are saved |
| `COMFY_API_URL` | `http://127.0.0.1:8188` | Base URL for ComfyUI API (script defaults to this)
| `COMFY_WORKFLOW_PATH` | `` | Path to exported ComfyUI workflow JSON (optional)
| `LOCAL_SD_URL` | `` | Local AUTOMATIC1111 WebUI base URL (fallback) |
| `MODEL` | `flux` | Pollinations model (`flux`, `turbo`) — only used if the script falls back to Pollinations |
| `IMAGE_WIDTH` | `1920` | Output image width |
| `IMAGE_HEIGHT` | `1080` | Output image height |
| `RETRY_LIMIT` | `3` | Retries per image on failure |
| `DELAY_BETWEEN` | `2` | Seconds between requests |
