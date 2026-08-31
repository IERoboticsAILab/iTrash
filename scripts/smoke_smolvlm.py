#!/usr/bin/env python3
"""Smoke test the local SmolVLM backend against real captured frames.

Verifies the whole path the hardware loop uses -- encode, POST to llama-server,
grammar-constrained JSON, validation -- and reports per-image latency, which is
the number that actually decides whether SmolVLM is viable on a Pi 4.

    ./scripts/smoke_smolvlm.py                      # newest 5 captured_images
    ./scripts/smoke_smolvlm.py path/to/image.jpg    # one specific file
"""

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ["AI_BACKEND"] = "smolvlm"

import cv2

from config.settings import AIConfig, HardwareConfig
from core.ai_classifier import SmolVLMClassifier


def pick_images(argv):
    if argv:
        return [Path(p) for p in argv]
    capture_dir = Path(HardwareConfig.IMAGE_SAVE_DIR)
    if not capture_dir.is_dir():
        sys.exit(f"No images given and {capture_dir} does not exist.")
    shots = sorted(capture_dir.glob("frame_*"), key=lambda p: p.stat().st_mtime)
    if not shots:
        sys.exit(f"No captured frames found in {capture_dir}.")
    return shots[-5:]


def main():
    images = pick_images(sys.argv[1:])
    classifier = SmolVLMClassifier()
    print(f"Server: {AIConfig.LLAMA_SERVER_URL}")
    print(f"Testing {len(images)} image(s)\n")

    timings = []
    for path in images:
        frame = cv2.imread(str(path))
        if frame is None:
            print(f"  {path.name}: SKIP (unreadable)")
            continue
        started = time.perf_counter()
        result = classifier.classify(frame)
        elapsed = time.perf_counter() - started
        timings.append(elapsed)
        print(f"  {path.name}: {result or '(empty)':<8} {elapsed:6.2f}s")

    if not timings:
        sys.exit("\nNo images classified. Is llama-server running?")

    timings.sort()
    print(f"\nmedian {timings[len(timings) // 2]:.2f}s   max {timings[-1]:.2f}s")
    # The user is standing at the bin; PROCESSING_TO_RESULT_DELAY adds 3s on top.
    if timings[-1] > 5:
        print("WARNING: >5s per image. Too slow for the kiosk flow on this hardware.")


if __name__ == "__main__":
    main()
