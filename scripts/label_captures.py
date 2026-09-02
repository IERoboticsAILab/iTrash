#!/usr/bin/env python3
"""Auto-label captured_images/ with the GPT backend to build a training set.

The GPT classifier is the teacher: we distill its labels into a fast local CNN
(see train_cnn.py). Run this where OPENAI_API_KEY is configured (e.g. on the Pi,
whose .env has it) -- it reuses the exact GPTClassifier the live system uses, so
labels match production.

    OPENAI_API_KEY=... python scripts/label_captures.py

Writes models/labels.csv (filename,trash_class); "" means no object / empty bin.
"""
import csv
import os
import sys
import types
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
os.environ["AI_BACKEND"] = "gpt"
# core.ai_classifier imports inference_sdk (legacy YOLO); stub it for headless runs.
sys.modules.setdefault("inference_sdk", types.ModuleType("inference_sdk"))
sys.modules["inference_sdk"].InferenceHTTPClient = object

import cv2

from config.settings import HardwareConfig
from core.ai_classifier import GPTClassifier

CAP = Path(HardwareConfig.IMAGE_SAVE_DIR)
OUT = REPO / "models" / "labels.csv"
OUT.parent.mkdir(exist_ok=True)


def main():
    clf = GPTClassifier()
    if not clf.api_key:
        sys.exit("OPENAI_API_KEY not set; nothing to label with.")
    imgs = sorted(CAP.glob("frame_*"))
    if not imgs:
        sys.exit(f"No captures in {CAP}.")
    print(f"labeling {len(imgs)} images...", flush=True)

    def label(p):
        img = cv2.imread(str(p))
        return (p.name, "READ_FAIL") if img is None else (p.name, clf.classify(img))

    rows, done = [], 0
    with ThreadPoolExecutor(max_workers=6) as ex:
        for name, cls in ex.map(label, imgs):
            rows.append((name, cls))
            done += 1
            if done % 20 == 0:
                print(f"  {done}/{len(imgs)}", flush=True)

    with open(OUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["filename", "trash_class"])
        w.writerows(rows)
    print("distribution:", dict(Counter(c for _, c in rows)))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
