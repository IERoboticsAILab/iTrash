#!/usr/bin/env python3
"""Fine-tune MobileNetV3-small on GPT-labeled captures, export ONNX for the Pi.

The `cnn` backend (core/ai_classifier.py: CNNClassifier) runs this model with
onnxruntime in ~25ms on a Pi 4 -- offline, and unlike an off-the-shelf garbage
classifier it is trained on the *real* kiosk frames, which is what closes the
domain gap. Run on a dev machine with torch/torchvision installed (NOT the Pi):

    pip install torch torchvision onnx onnxscript pillow
    python scripts/label_captures.py      # produces models/labels.csv
    python scripts/train_cnn.py           # produces models/trash_cnn.{onnx,json}

Then copy models/trash_cnn.onnx + models/trash_cnn.json to the Pi's models/ dir
and run the system with AI_BACKEND=cnn.

Note: accuracy tracks how much labeled data you have. Under-represented bins
(organic/brown is usually the sparsest) stay weak until more frames accumulate
in captured_images/ -- re-run both scripts periodically to improve the model.
"""
import csv
import json
import random
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import torch
import torch.nn as nn
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms

from config.settings import HardwareConfig  # noqa: E402  (kept for IMAGE_SAVE_DIR)
IMG_DIR = Path(HardwareConfig.IMAGE_SAVE_DIR)
if not IMG_DIR.is_absolute():
    IMG_DIR = REPO / IMG_DIR
LABELS = REPO / "models" / "labels.csv"
OUT_ONNX = REPO / "models" / "trash_cnn.onnx"
OUT_JSON = REPO / "models" / "trash_cnn.json"

MIN_PER_CLASS = 8   # drop classes too rare to train/eval meaningfully
EPOCHS = 25
BATCH = 16
MEAN, STD = [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]
random.seed(0)
torch.manual_seed(0)


def load_rows():
    rows = []
    for r in csv.DictReader(open(LABELS)):
        lab = r["trash_class"] or "empty"   # "" (no object) becomes its own class
        if lab == "READ_FAIL":
            continue
        p = IMG_DIR / r["filename"]
        if p.exists():
            rows.append((p, lab))
    return rows


class DS(Dataset):
    def __init__(self, items, tf, cls_idx):
        self.items, self.tf, self.cls_idx = items, tf, cls_idx

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        p, l = self.items[i]
        return self.tf(Image.open(p).convert("RGB")), self.cls_idx[l]


def main():
    rows = load_rows()
    counts = Counter(l for _, l in rows)
    classes = sorted(c for c, n in counts.items() if n >= MIN_PER_CLASS)
    rows = [(p, l) for p, l in rows if l in classes]
    cls_idx = {c: i for i, c in enumerate(classes)}
    print("label distribution:", dict(counts))
    print("classes used:", classes, "| samples:", len(rows))

    by = {c: [] for c in classes}
    for p, l in rows:
        by[l].append(p)
    train, val = [], []
    for c, ps in by.items():
        random.shuffle(ps)
        k = max(1, int(len(ps) * 0.2))
        val += [(p, c) for p in ps[:k]]
        train += [(p, c) for p in ps[k:]]
    print(f"train={len(train)} val={len(val)}")

    train_tf = transforms.Compose([
        transforms.RandomResizedCrop(224, scale=(0.6, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(20),
        transforms.ColorJitter(0.3, 0.3, 0.3, 0.05),
        transforms.ToTensor(), transforms.Normalize(MEAN, STD)])
    eval_tf = transforms.Compose([
        transforms.Resize(256), transforms.CenterCrop(224),
        transforms.ToTensor(), transforms.Normalize(MEAN, STD)])

    tl = DataLoader(DS(train, train_tf, cls_idx), batch_size=BATCH, shuffle=True, num_workers=4)
    vl = DataLoader(DS(val, eval_tf, cls_idx), batch_size=BATCH, num_workers=4)

    net = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.IMAGENET1K_V1)
    net.classifier[3] = nn.Linear(net.classifier[3].in_features, len(classes))
    w = torch.tensor([1.0 / counts[c] for c in classes])
    crit = nn.CrossEntropyLoss(weight=w / w.sum() * len(classes))  # counter imbalance
    opt = torch.optim.AdamW(net.parameters(), lr=3e-4, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, EPOCHS)

    def evaluate():
        net.eval()
        correct = 0
        conf = torch.zeros(len(classes), len(classes), dtype=int)
        with torch.no_grad():
            for x, y in vl:
                pred = net(x).argmax(1)
                correct += (pred == y).sum().item()
                for t, p in zip(y, pred):
                    conf[t, p] += 1
        return correct / len(val), conf

    best, best_conf, best_sd = 0.0, None, None
    for ep in range(EPOCHS):
        net.train()
        for x, y in tl:
            opt.zero_grad()
            crit(net(x), y).backward()
            opt.step()
        sched.step()
        acc, conf = evaluate()
        if acc >= best:
            best, best_conf = acc, conf
            best_sd = {k: v.clone() for k, v in net.state_dict().items()}
        print(f"ep {ep:2d}  val_acc={acc:.3f}  best={best:.3f}", flush=True)

    print(f"\nBEST val_acc = {best:.3f}")
    print("confusion (rows=true, cols=pred):", classes)
    for i, c in enumerate(classes):
        print(f"  {c:8s}", best_conf[i].tolist())

    net.load_state_dict(best_sd)
    net.eval()
    torch.onnx.export(net, torch.randn(1, 3, 224, 224), str(OUT_ONNX),
                      input_names=["input"], output_names=["logits"],
                      opset_version=13, dynamo=False)
    json.dump({"classes": classes, "mean": MEAN, "std": STD}, open(OUT_JSON, "w"), indent=2)
    print(f"exported {OUT_ONNX.name} + {OUT_JSON.name}")


if __name__ == "__main__":
    main()
