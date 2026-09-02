#!/usr/bin/env python3
"""Download the external garbage dataset used to pretrain the CNN.

Pulls only the class folders that map to our 3 bins (no Kaggle auth needed) from
a HuggingFace imagefolder dataset, into external_data/. Idempotent -- skips if
already present. Run on the training machine (the Mac), not the Pi.

    python scripts/fetch_external.py

Mapping (see EXTERNAL_MAP): biological->brown, paper/cardboard->blue,
plastic/metal->yellow. Glass/battery/clothes/shoes/trash are ignored (no bin).
"""
from pathlib import Path

from huggingface_hub import snapshot_download

REPO = "omasteam/waste-garbage-management-dataset"
DEST = Path(__file__).resolve().parent.parent / "external_data"
# dataset folder -> our bin color
EXTERNAL_MAP = {
    "biological": "brown",
    "paper": "blue",
    "cardboard": "blue",
    "plastic": "yellow",
    "metal": "yellow",
}


def main():
    DEST.mkdir(exist_ok=True)
    patterns = [f"{c}/*" for c in EXTERNAL_MAP]
    print(f"Downloading {list(EXTERNAL_MAP)} from {REPO} -> {DEST}")
    snapshot_download(
        repo_id=REPO,
        repo_type="dataset",
        allow_patterns=patterns,
        local_dir=str(DEST),
    )
    counts = {c: len(list((DEST / c).glob("*"))) for c in EXTERNAL_MAP if (DEST / c).is_dir()}
    print("fetched per class:", counts)
    print(f"done -> {DEST}")


if __name__ == "__main__":
    main()
