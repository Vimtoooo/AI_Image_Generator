# Image Generator — ComfyUI

Generates MS Paint-style stickman images for every timestamp in a YouTube script.
**Free, no API key, unlimited generations.**

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

- Calls [Pollinations.AI](https://pollinations.ai) — a completely free, no-login image API
- Generates each image at **1920×1080 (16:9)** in MS Paint stickman style
- Skips images that already exist (safe to re-run)
- Auto-retries failed images up to 3 times

## Rate limits and 402 responses

- Pollinations may return HTTP `402` with a JSON body indicating "Queue full for IP" when the free endpoint is busy or your IP has a pending request in their queue.
- The generator now implements exponential backoff on `402` responses and will wait before retrying, but you may still hit limits during heavy usage.
- Options:
	- Wait and re-run later (the queue clears over time).
	- Sign up at https://enter.pollinations.ai for higher/unlimited access.
	- Increase `DELAY_BETWEEN` or reduce the number of images requested at once.

## Local Stable Diffusion (recommended for high-volume use)

If you have an NVIDIA GPU (like an RTX 3050), running Stable Diffusion locally is the most reliable way to generate many images without rate limits.

Quick overview (AUTOMATIC1111 WebUI):

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

### ComfyUI API integration

This generator can call a running ComfyUI API. To enable it:

1. Start ComfyUI and install an API extension (search "ComfyUI API" or "ComfyUI Web API" extension in the ComfyUI community plugins).
2. Export or save a workflow JSON (you mentioned `gsl_starter_1_1.json`).
3. Set these environment variables before running the generator:

```powershell
setx COMFY_API_URL "http://127.0.0.1:8188"
setx COMFY_WORKFLOW_PATH "C:\path\to\gsl_starter_1_1.json"
```

Notes:
- The script will try several common ComfyUI API endpoints and payload shapes. If your API exposes a different path, set `COMFY_API_URL` to include that path (for example `http://127.0.0.1:8188/api/generate`).
- The script searches the JSON response for base64-encoded images (data:image/* or plain base64 strings) and saves the first image it finds.

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
| `OUTPUT_DIR` | `assets/Generated_Images` | Where images are saved |
| `MODEL` | `flux` | Pollinations model (`flux`, `turbo`) |
| `IMAGE_WIDTH` | `1920` | Output image width |
| `IMAGE_HEIGHT` | `1080` | Output image height |
| `RETRY_LIMIT` | `3` | Retries per image on failure |
| `DELAY_BETWEEN` | `2` | Seconds between requests |
