# -*- coding: utf-8 -*-
"""
YouTube Script Image Generator
================================
Generates MS Paint-style stickman images for each timestamp in a YouTube script
using Pollinations.AI -- completely free, no API key required, unlimited generations.

Usage:
    uv run generate_images.py
"""

import sys
import time
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
sys.stdout.reconfigure(line_buffering=True)

# ─────────────────────────────────────────────
# CONFIG -- Edit these for future videos
# ─────────────────────────────────────────────

# Output folder (relative to this script's location). Matches repository Assets/Generated_Images
OUTPUT_DIR = Path(__file__).parent.parent.parent / "Assets" / "Generated_Images"

# Pollinations.AI settings
IMAGE_WIDTH   = 1920
IMAGE_HEIGHT  = 1080
MODEL         = "flux"   # Options: flux, turbo, flux-realism
RETRY_LIMIT   = 3        # Retries per image on failure
DELAY_BETWEEN = 2        # Seconds to wait between requests

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


# ─────────────────────────────────────────────
# GENERATOR
# ─────────────────────────────────────────────

def build_url(scene_prompt: str) -> str:
    """Build the Pollinations.AI image URL."""
    full_prompt = f"{STYLE_PREFIX}, {scene_prompt}"
    encoded = quote(full_prompt)
    return (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width={IMAGE_WIDTH}&height={IMAGE_HEIGHT}"
        f"&nologo=true&model={MODEL}"
    )


def generate_image(timestamp: str, scene_prompt: str, output_dir: Path) -> bool:
    """Download and save a single image. Returns True on success."""
    url = build_url(scene_prompt)
    filename = output_dir / f"{timestamp}.png"

    for attempt in range(1, RETRY_LIMIT + 1):
        try:
            print(f"  Requesting from Pollinations.AI (attempt {attempt}/{RETRY_LIMIT})...")
            response = requests.get(url, timeout=90)

            content_type = response.headers.get("content-type", "")
            if response.status_code == 200 and content_type.startswith("image"):
                filename.write_bytes(response.content)
                size_kb = len(response.content) // 1024
                print(f"  [OK] Saved -> {filename.name}  ({size_kb} KB)")
                return True
            else:
                print(f"  [WARN] Unexpected response: {response.status_code} -- retrying...")

        except requests.exceptions.Timeout:
            print(f"  [TIMEOUT] Attempt {attempt} timed out -- retrying...")
        except requests.exceptions.RequestException as e:
            print(f"  [ERROR] Request error: {e} -- retrying...")

        if attempt < RETRY_LIMIT:
            time.sleep(5)

    print(f"  [FAIL] Failed after {RETRY_LIMIT} attempts -- skipping {timestamp}.png")
    return False


def main():
    print("")
    print("=" * 55)
    print("  YouTube Script Image Generator - Pollinations.AI")
    print("=" * 55)

    # Ensure output folder exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n[DIR] Output folder: {OUTPUT_DIR}\n")

    # Skip already-generated images
    to_generate = []
    skipped = []
    for timestamp, prompt in IMAGES:
        target = OUTPUT_DIR / f"{timestamp}.png"
        if target.exists():
            skipped.append(timestamp)
        else:
            to_generate.append((timestamp, prompt))

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
