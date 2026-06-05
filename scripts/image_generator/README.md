# Image Generator — Pollinations.AI

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
