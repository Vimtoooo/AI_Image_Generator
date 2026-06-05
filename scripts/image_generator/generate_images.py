# -*- coding: utf-8 -*-
"""
YouTube Script Image Generator
=================================
Generates MS Paint-style stickman images for each timestamp in a YouTube script.
Prefers a local ComfyUI API (recommended) or local AUTOMATIC1111 WebUI; Pollinations.AI
is kept only as a remote fallback and may be rate-limited.

Usage:
    uv run generate_images.py
"""

import sys
import time
import os
import argparse
import base64
import json
import re
from pathlib import Path
from urllib.parse import quote

# Provide a clear error if required third-party modules are missing. This helps
# when the script is run with a different Python interpreter than the one
# where dependencies were installed (common with `uv` or virtualenv setups).
try:
    import requests
except ImportError:
    print("\n[ERROR] Missing dependency: 'requests'\n")
    print("Install into the Python interpreter you're using, for example:")
    print(f"  {sys.executable} -m pip install requests")
    print("Or activate the virtual environment used by 'uv' (e.g. `uv sync`) and re-run.")
    sys.exit(1)

# Force line-buffered output so logs appear immediately when redirected
sys.stdout.reconfigure(line_buffering=True) # type: ignore[attr-defined]

# ─────────────────────────────────────────────
# CONFIG -- Edit these for future videos
# ─────────────────────────────────────────────

# Output folder (relative to this script's location). Matches repository Assets/Generated_Images
OUTPUT_DIR = Path(__file__).parent.parent.parent / "Assets" / "Generated_Images"

# Remote Pollinations (fallback) settings
IMAGE_WIDTH   = 1920
IMAGE_HEIGHT  = 1080
MODEL         = "flux"   # Options: flux, turbo, flux-realism
RETRY_LIMIT   = 3        # Retries per image on failure
DELAY_BETWEEN = 3        # Seconds to wait between requests
BACKOFF_BASE  = 10       # Base seconds for exponential backoff on 402 responses
MAX_BACKOFF   = 120      # Max backoff wait in seconds

# ComfyUI/Comfy API settings: prefer an explicit env var but fall back to localhost
COMFY_URL = os.environ.get("COMFY_API_URL", "http://127.0.0.1:8188")

# Style applied to every image -- matches the MS Paint / stickman brief
STYLE_PREFIX = (
    "MS Paint amateur beginner drawing style, white background, "
    "thick uneven wobbly black hand-drawn outlines, stick figure humans "
    "with round circle heads, flat simple colors only (red, blue, green, "
    "yellow, orange, brown, grey), no shading, no 3D, no realistic style, "
    "childish funny intentionally bad drawing, simple geometric shapes only, "
    "wide horizontal 16:9 YouTube scene, lots of empty white space"
)

# ─────────────────────────────────────────────
# IMAGES -- (timestamp_filename, scene_description)
# Add or remove entries here for future videos.
# ─────────────────────────────────────────────

IMAGES = [
    # -- Svalbard Seed Vault Script ------------------------------------------
    (
        "1.01",
        "rows of simple shelves drawn as horizontal lines with many tiny rectangular "
        "seed packets stacked on them, a stick figure with wide circle eyes and open "
        "mouth looking amazed at the shelves, bold wobbly handwritten text reading "
        "1.2 MILLION in the corner"
    ),
    (
        "1.09",
        "two shelves side by side, left shelf labeled NORTH KOREA with a simple flag "
        "drawn above it and seed packets on it, right shelf labeled USA with a simple "
        "flag and seed packets, both shelves touching each other peacefully"
    ),
    (
        "1.17",
        "stick figure people from different countries standing in a line shaking hands, "
        "simple different flags drawn above each stick figure, each person holding a "
        "small leaf or plant, text BOTANICAL PEACE SUMMIT written in wobbly letters below"
    ),
    (
        "1.26",
        "three simple panels side by side: left panel shows a simple explosion with "
        "red fire lines labeled WAR, middle panel shows rain lines and flood waves "
        "labeled DISASTER, right panel shows a broken machine with an X on it labeled "
        "FAILURE, red border around each panel"
    ),
    (
        "1.33",
        "a simple drawing of a plant or crop in the center with a big red X drawn "
        "through it, bold wobbly text reading GONE FOREVER below it, a sad stick "
        "figure with downturned mouth standing next to it, lots of white empty space"
    ),
    (
        "1.41",
        "a simple hand-drawn calendar showing the year 2015 with a circle around it, "
        "a stick figure wearing a simple lab coat opening a rectangular vault door, "
        "a seed packet drawn in the stick figure hand"
    ),
    (
        "1.48",
        "a stick figure wearing a simple headscarf carrying a seed packet in both hands, "
        "a very simple map on the right side with a red circle marking Syria, "
        "an arrow pointing from Syria to the stick figure, flat simple colors"
    ),
    (
        "1.55",
        "three simple steps shown left to right with arrows between them: step 1 shows "
        "a tiny seed packet, step 2 shows a simple plant growing, step 3 shows many "
        "plants in a row, then a final arrow pointing to a simple mountain building "
        "labeled VAULT, wobbly text labels under each step"
    ),
    (
        "2.04",
        "a simple mountain drawing with a vault door entrance, a small label reading "
        "SVALBARD VAULT, below it a wobbly handwritten text reading QUIET INSURANCE "
        "POLICY, a small planet Earth circle drawn nearby, peaceful simple scene, "
        "no people, lots of white space"
    ),
    (
        "2.09",
        "a simple rectangle in the center shaped like a hard drive or USB drive, "
        "labeled GLOBAL BACKUP DRIVE with wobbly letters, a fork and a spoon drawn "
        "on top of the rectangle, a small plate with food doodle next to it"
    ),
    (
        "2.17",
        "a big red rectangle in the center labeled SUBSCRIBE in bold wobbly letters, "
        "a stick figure hand cursor with a pointing finger clicking the button, "
        "a simple bell icon drawn to the right of the button, flat red color"
    ),
    (
        "2.22",
        "a stick figure with a round circle head standing with a big thought bubble "
        "above it containing a red question mark, below the thought bubble wobbly "
        "handwritten text reads WHAT WOULD YOU PUT IN A GLOBAL BACKUP VAULT, "
        "lots of white space around"
    ),
]


def sanitize_timestamp_for_filename(ts: str) -> str:
    """Return a filesystem-safe filename for a timestamp string."""
    # Replace colons and spaces with dots, remove any characters except [0-9a-zA-Z._-]
    s = ts.strip()
    s = s.replace(":", ".").replace(" ", ".").replace("/", "-")
    s = re.sub(r"[^0-9A-Za-z._-]", "", s)
    return s


def load_images_from_script(path: str) -> list:
    """Load timestamp/prompt pairs from a plain-text script file.

    Supports simple formats where a line starting with a timestamp begins a
    new prompt. Timestamp formats supported include `MM:SS`, `H:MM:SS`, or
    `M.SS` (dots) and `MM.SS`. The description may continue on the same
    line after a dash or on subsequent indented/non-timestamp lines.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)

    text = p.read_text(encoding="utf-8")

    # First, try to detect inline timestamps like: (0:02) Some text (0:10) more text
    inline_re = re.compile(r"\(?\s*(\d{1,2}(?::\d{2}){1,2}|\d{1,2}\.\d{2})\s*\)?")
    matches = list(inline_re.finditer(text))
    if matches and len(matches) > 0:
        entries = []
        for i, m in enumerate(matches):
            ts = m.group(1)
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            prompt = text[start:end].strip()
            # Clean surrounding punctuation/newlines
            prompt = prompt.strip(" \t\n\r-–—:;,.\'")
            if prompt:
                entries.append((ts, prompt))
        return entries

    # Fallback: original line-based parsing where each line starts with a timestamp
    lines = text.splitlines()
    entries = []
    current_ts = None
    current_lines = []

    # Timestamp regex: matches 1:23, 01:23, 1.23, 1:02:33 at start of line
    ts_line_re = re.compile(r"^\s*(\d{1,2}(?::\d{2}){0,2}|\d{1,2}\.\d{2})\s*(?:[-–—]\s*)?(.*)$")

    for ln in lines:
        m = ts_line_re.match(ln)
        if m:
            # flush previous
            if current_ts is not None:
                prompt = " ".join([l.strip() for l in current_lines if l.strip()])
                entries.append((current_ts, prompt))
            current_ts = m.group(1)
            rest = m.group(2) or ""
            current_lines = [rest] if rest else []
        else:
            # continuation line
            if current_ts is not None:
                current_lines.append(ln)

    # flush last
    if current_ts is not None:
        prompt = " ".join([l.strip() for l in current_lines if l.strip()])
        entries.append((current_ts, prompt))

    return entries


# ─────────────────────────────────────────────
# GENERATOR
# ─────────────────────────────────────────────

def build_url(scene_prompt: str) -> str:
    """Build the Pollinations.AI fallback image URL."""
    full_prompt = f"{STYLE_PREFIX}, {scene_prompt}"
    encoded = quote(full_prompt)
    return (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width={IMAGE_WIDTH}&height={IMAGE_HEIGHT}"
        f"&nologo=true&model={MODEL}"
    )

    # banner printed in main()

def generate_image(timestamp: str, scene_prompt: str, output_dir: Path) -> bool:
    """Download and save a single image. Returns True on success."""
    # Priority order for local backends:
    # 1. ComfyUI API (set COMFY_API_URL)
    # 2. AUTOMATIC1111 WebUI (set LOCAL_SD_URL)
    # Prefer ComfyUI endpoint (can be a full path); COMFY_URL defaults to localhost if unset
    comfy_url = COMFY_URL
    if comfy_url:
        workflow_path = os.getenv("COMFY_WORKFLOW_PATH")
        return generate_image_comfy(timestamp, scene_prompt, output_dir, comfy_url, workflow_path)

    # If a local Stable Diffusion WebUI is available, use it instead of Pollinations.
    # Set the environment variable `LOCAL_SD_URL` to the base URL, e.g.:
    #   http://127.0.0.1:7860
    local_sd = os.getenv("LOCAL_SD_URL")
    if local_sd:
        return generate_image_local_sd(timestamp, scene_prompt, output_dir, local_sd)

    url = build_url(scene_prompt)
    safe_name = sanitize_timestamp_for_filename(timestamp)
    filename = output_dir / f"{safe_name}.png"
    # Use browser-like headers — some endpoints block unknown user-agents or require a referer.
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/125.0 Safari/537.36"
        ),
        "Referer": "https://pollinations.ai/",
        "Accept": "image/*,*/*;q=0.8",
    }

    for attempt in range(1, RETRY_LIMIT + 1):
        try:
            print(f"  Requesting Pollinations.AI (fallback) (attempt {attempt}/{RETRY_LIMIT})...")
            response = requests.get(url, timeout=90, headers=headers)

            content_type = response.headers.get("content-type", "")
            if response.status_code == 200 and content_type.startswith("image"):
                filename.write_bytes(response.content)
                size_kb = len(response.content) // 1024
                print(f"  [OK] Saved -> {filename.name}  ({size_kb} KB)")
                return True
            # Handle rate-limit / queue-full (Pollinations returns 402 with JSON explaining the queue)
            if response.status_code == 402:
                try:
                    body = response.json()
                    err = body.get("error") if isinstance(body, dict) else str(body)
                except Exception:
                    err = response.text[:1000]

                print(f"  [WARN] 402 rate/queue response: {err}")
                # Exponential backoff based on attempt number
                backoff = min(BACKOFF_BASE * (2 ** (attempt - 1)), MAX_BACKOFF)
                print(f"  [WAIT] Backing off for {backoff} seconds before retrying...")
                time.sleep(backoff)
                # continue to next attempt
                continue

            # On other non-image responses, print a short snippet of the body to aid debugging
            snippet = None
            try:
                snippet = response.text[:1000]
            except Exception:
                snippet = f"<unable to decode response body; length={len(response.content)} bytes>"

            print(f"  [WARN] Unexpected response: {response.status_code} -- {content_type}")
            print(f"  [RESP] {snippet}")

        except requests.exceptions.Timeout:
            print(f"  [TIMEOUT] Attempt {attempt} timed out -- retrying...")
        except requests.exceptions.RequestException as e:
            print(f"  [ERROR] Request error: {e} -- retrying...")

        if attempt < RETRY_LIMIT:
            time.sleep(5)

    print(f"  [FAIL] Failed after {RETRY_LIMIT} attempts -- skipping {timestamp}.png")
    return False


def generate_image_local_sd(timestamp: str, scene_prompt: str, output_dir: Path, sd_url: str) -> bool:
    """Generate image using a local AUTOMATIC1111-style WebUI (/sdapi/v1/txt2img).
    sd_url should be like 'http://127.0.0.1:7860' and the WebUI must be running.
    """
    full_prompt = f"{STYLE_PREFIX}, {scene_prompt}"
    payload = {
        "prompt": full_prompt,
        "width": IMAGE_WIDTH,
        "height": IMAGE_HEIGHT,
        "sampler_name": "Euler a",
        "steps": 20,
        "cfg_scale": 7.0,
        "batch_size": 1,
    }

    api = sd_url.rstrip("/") + "/sdapi/v1/txt2img"
    try:
        print(f"  Requesting local SD WebUI at {api}...")
        resp = requests.post(api, json=payload, timeout=120)
    except requests.exceptions.RequestException as e:
        print(f"  [ERROR] Local SD request failed: {e}")
        return False

    if resp.status_code != 200:
        snippet = resp.text[:1000] if resp.text else f"<no body; status {resp.status_code}>"
        print(f"  [WARN] Local SD returned {resp.status_code}: {snippet}")
        return False

    try:
        data = resp.json()
        images = data.get("images") or []
        if not images:
            print("  [WARN] No images returned from local SD")
            return False

        b64 = images[0]
        image_bytes = base64.b64decode(b64.split(",")[-1])
        filename = output_dir / f"{sanitize_timestamp_for_filename(timestamp)}.png"
        filename.write_bytes(image_bytes)
        print(f"  [OK] Saved -> {filename.name}  ({len(image_bytes)//1024} KB)")
        return True
    except Exception as e:
        print(f"  [ERROR] Failed to decode/save image from local SD: {e}")
        return False


def generate_image_comfy(timestamp: str, scene_prompt: str, output_dir: Path, comfy_url: str, workflow_path: str | None) -> bool:
    """Attempt to generate an image by calling a ComfyUI API endpoint.

    The function will try common endpoints and payload shapes and will attempt
    to decode a base64 image from the response. If you exported a workflow
    JSON (e.g. gsl_starter_1_1.json), set the environment variable
    `COMFY_WORKFLOW_PATH` to include it and the payload will include the workflow.
    """
    full_prompt = f"{STYLE_PREFIX}, {scene_prompt}"
    endpoints = [
        "/api/generate",
        "/api/v1/generate",
        "/generate",
        "/api/workflow/run",
        "/api/v1/workflow/run",
        "/api/run_workflow",
    ]

    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    # Load workflow JSON if provided
    workflow_json = None
    if workflow_path:
        try:
            p = Path(workflow_path)
            workflow_json = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  [WARN] Failed to load COMFY_WORKFLOW_PATH '{workflow_path}': {e}")
            workflow_json = None

    payload_variants = []
    # Simple txt2img payload
    payload_variants.append({"prompt": full_prompt, "width": IMAGE_WIDTH, "height": IMAGE_HEIGHT})
    # Explicit inputs container
    payload_variants.append({"inputs": {"prompt": full_prompt, "width": IMAGE_WIDTH, "height": IMAGE_HEIGHT}})
    # Workflow-run payload if we have workflow JSON
    if workflow_json is not None:
        payload_variants.append({"workflow": workflow_json, "inputs": {"prompt": full_prompt}})

    base = comfy_url.rstrip("/")
    for ep in endpoints:
        url = base + ep
        for payload in payload_variants:
            try:
                print(f"  Requesting ComfyUI endpoint {url} with payload keys: {', '.join(payload.keys())}...")
                resp = requests.post(url, json=payload, headers=headers, timeout=120)
            except requests.exceptions.RequestException as e:
                print(f"  [ERROR] Request to {url} failed: {e}")
                continue

            if resp.status_code != 200:
                snippet = resp.text[:1000] if resp.text else f"<no body; status {resp.status_code}>"
                print(f"  [WARN] ComfyUI {url} returned {resp.status_code}: {snippet}")
                continue

            # Try to parse JSON and extract common image fields (base64)
            try:
                data = resp.json()
            except Exception:
                print("  [WARN] ComfyUI response not JSON; attempting to save raw content if it is an image")
                ct = resp.headers.get("content-type", "")
                if ct.startswith("image"):
                    fname = output_dir / f"{sanitize_timestamp_for_filename(timestamp)}.png"
                    fname.write_bytes(resp.content)
                    print(f"  [OK] Saved raw image -> {fname.name}")
                    return True
                continue

            # Search for base64 image in common fields
            candidates = []
            if isinstance(data, dict):
                for key in ("images", "image", "result", "outputs", "data"):
                    if key in data:
                        candidates.append(data[key])

            # Normalize candidates to list of base64 strings
            b64_list = []
            for cand in candidates:
                if isinstance(cand, str):
                    b64_list.append(cand)
                elif isinstance(cand, list):
                    for item in cand:
                        if isinstance(item, str):
                            b64_list.append(item)
                        elif isinstance(item, dict) and "b64" in item:
                            b64_list.append(item.get("b64"))

            # If nothing found, try to walk the JSON for base64-like strings
            if not b64_list:
                def find_b64(obj):
                    if isinstance(obj, str) and obj.strip().startswith("data:image"):
                        return obj
                    if isinstance(obj, dict):
                        for v in obj.values():
                            r = find_b64(v)
                            if r:
                                return r
                    if isinstance(obj, list):
                        for v in obj:
                            r = find_b64(v)
                            if r:
                                return r
                    return None

                found = find_b64(data)
                if found:
                    b64_list.append(found)

            if not b64_list:
                print("  [WARN] No base64 image found in ComfyUI response JSON")
                continue

            # Decode first base64 image and save
            try:
                raw = b64_list[0]
                if raw.startswith("data:image"):
                    raw = raw.split(",", 1)[1]
                image_bytes = base64.b64decode(raw)
                fname = output_dir / f"{sanitize_timestamp_for_filename(timestamp)}.png"
                fname.write_bytes(image_bytes)
                print(f"  [OK] Saved -> {fname.name}  ({len(image_bytes)//1024} KB)")
                return True
            except Exception as e:
                print(f"  [ERROR] Failed to decode/save ComfyUI image: {e}")
                continue

    print("  [FAIL] All ComfyUI endpoints/payloads failed for this prompt")
    return False


def main():
    parser = argparse.ArgumentParser(description="Generate images per timestamped script lines")
    parser.add_argument("--script", "-s", help="Path to a text script containing timestamps and descriptions")
    parser.add_argument("--test", "-t", type=int, default=None,
                        help="Generate only the first N images (quick test mode)")
    args = parser.parse_args()

    print("")
    print("=" * 55)
    print("  YouTube Script Image Generator - ComfyUI (preferred)")
    print("=" * 55)

    # Ensure output folder exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n[DIR] Output folder: {OUTPUT_DIR}\n")

    # Determine list of (timestamp, prompt) pairs. Prefer a script file if provided
    # via CLI or the SCRIPT_PATH environment variable. Otherwise fall back to
    # the in-script `IMAGES` list.
    script_path = args.script or os.getenv("SCRIPT_PATH")
    # If no script path provided, look for scripts in the repository `prompts/` folder
    if not script_path:
        repo_root = Path(__file__).parent.parent.parent
        prompts_dir = repo_root / "prompts"
        found = None
        if prompts_dir.exists() and prompts_dir.is_dir():
            # prefer a file named `my_video_script.txt` if present
            preferred = prompts_dir / "my_video_script.txt"
            if preferred.exists():
                found = preferred
            else:
                # pick the first .txt file in the prompts folder
                for p in sorted(prompts_dir.glob("*.txt")):
                    found = p
                    break
        if found:
            script_path = str(found)
            print(f"[AUTO] Using script from prompts/: {script_path}")
    if script_path:
        try:
            parsed = load_images_from_script(script_path)
            if parsed:
                image_list = parsed
            else:
                print(f"[WARN] No timestamped entries found in script: {script_path}; using built-in IMAGES")
                image_list = IMAGES
        except Exception as e:
            print(f"[WARN] Failed to load script '{script_path}': {e}; using built-in IMAGES")
            image_list = IMAGES
    else:
        image_list = IMAGES

    # Skip already-generated images
    to_generate = []
    skipped = []
    for timestamp, prompt in image_list:
        safe_name = sanitize_timestamp_for_filename(timestamp)
        target = OUTPUT_DIR / f"{safe_name}.png"
        if target.exists():
            skipped.append(safe_name)
        else:
            to_generate.append((timestamp, prompt))

    # If test mode is enabled, only generate the first N images
    if args.test is not None:
        try:
            n = int(args.test)
            if n < 0:
                n = 0
        except Exception:
            n = 0
        to_generate = to_generate[:n]
        print(f"[TEST] Test mode active — generating first {len(to_generate)} image(s)")

    if skipped:
        print(f"[SKIP] Already exists ({len(skipped)}): {', '.join(skipped)}\n")

    if not to_generate:
        print("[DONE] All images already generated! Nothing to do.")
        return

    print(f"[GEN]  Generating {len(to_generate)} image(s)...\n")

    success_count = 0
    fail_count = 0

    for i, (timestamp, prompt) in enumerate(to_generate, 1):
        print(f"[{i}/{len(to_generate)}] Timestamp {timestamp}")
        ok = generate_image(timestamp, prompt, OUTPUT_DIR)
        if ok:
            success_count += 1
        else:
            fail_count += 1

        # Polite delay between requests
        if i < len(to_generate):
            time.sleep(DELAY_BETWEEN)

    # Summary
    print("")
    print("-" * 55)
    print(f"  Success : {success_count}")
    if fail_count:
        print(f"  Failed  : {fail_count}  (re-run the script to retry)")
    print(f"  Saved to: {OUTPUT_DIR}")
    print("-" * 55)
    print("")

    if fail_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
