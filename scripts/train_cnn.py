#!/usr/bin/env python3
"""Two-stage training for the local CNN: pretrain on an external garbage dataset,
then fine-tune on our own kiosk captures.

Why two stages: kiosk-only can't learn organic from ~a dozen frames, and
external-only fails the domain gap (clean studio photos don't match held items
on a reflective office background). Pretraining learns material features from
~5k external images; fine-tuning adapts them to the kiosk. The honest metric is
val accuracy on a held-out slice of the *kiosk* captures.

Run on a machine with torch (the Mac -- uses Apple MPS GPU if available), NOT
the Pi:

    python scripts/fetch_external.py      # once: pulls external_data/
    python scripts/label_captures.py      # on the Pi: models/labels.csv
    python scripts/train_cnn.py           # -> models/trash_cnn.{onnx,json}

The "empty" label is intentionally dropped: the proximity sensor already gates
presence, so a dedicated empty class only made the model fire false "empty" on
real items. Uncertain frames are handled at runtime by CNN_MIN_CONFIDENCE.
"""
import csv
import json
import random
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import torch
import torch.nn as nn
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms

from config.settings import HardwareConfig  # noqa: E402

IMG_DIR = Path(HardwareConfig.IMAGE_SAVE_DIR)
if not IMG_DIR.is_absolute():
    IMG_DIR = REPO / IMG_DIR
LABELS = REPO / "models" / "labels.csv"
EXTERNAL_DIR = REPO / "external_data"
OUT_ONNX = REPO / "models" / "trash_cnn.onnx"
OUT_JSON = REPO / "models" / "trash_cnn.json"

# Fixed 3-bin output (no "empty"; sorted to match CNNClassifier expectations).
CLASSES = ["blue", "brown", "yellow"]
CLS_IDX = {c: i for i, c in enumerate(CLASSES)}
# external dataset folder -> bin (mirrors scripts/fetch_external.EXTERNAL_MAP)
EXTERNAL_MAP = {"biological": "brown", "paper": "blue", "cardboard": "blue",
                "plastic": "yellow", "metal": "yellow"}
IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

PRETRAIN_EPOCHS = 12
FINETUNE_EPOCHS = 30
BATCH = 32
MEAN, STD = [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]
random.seed(0)
torch.manual_seed(0)

DEVICE = ("mps" if torch.backends.mps.is_available()
          else "cuda" if torch.cuda.is_available() else "cpu")


def kiosk_items():
    """(path, bin) for kiosk captures whose GPT label is a real bin."""
    items = []
    for r in csv.DictReader(open(LABELS)):
        lab = r["trash_class"]
        if lab in CLASSES:
            p = IMG_DIR / r["filename"]
            if p.exists():
                items.append((p, lab))
    return items


def external_items():
    items = []
    for folder, binc in EXTERNAL_MAP.items():
        d = EXTERNAL_DIR / folder
        if d.is_dir():
            items += [(p, binc) for p in d.iterdir() if p.suffix.lower() in IMG_EXT]
    return items


TRAIN_TF = transforms.Compose([
    transforms.RandomResizedCrop(224, scale=(0.6, 1.0)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(20),
    transforms.ColorJitter(0.3, 0.3, 0.3, 0.05),
    transforms.ToTensor(), transforms.Normalize(MEAN, STD)])
EVAL_TF = transforms.Compose([
    transforms.Resize(256), transforms.CenterCrop(224),
    transforms.ToTensor(), transforms.Normalize(MEAN, STD)])


class DS(Dataset):
    def __init__(self, items, tf):
        self.items, self.tf = items, tf

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        p, l = self.items[i]
        try:
            img = Image.open(p).convert("RGB")
        except Exception:
            img = Image.new("RGB", (224, 224))  # skip-proof: corrupt file -> blank
        return self.tf(img), CLS_IDX[l]


def class_weights(items):
    from collections import Counter
    c = Counter(l for _, l in items)
    w = torch.tensor([1.0 / max(1, c[k]) for k in CLASSES])
    return (w / w.sum() * len(CLASSES)).to(DEVICE), dict(c)


def run_epochs(net, items, epochs, lr, tag, val=None):
    loader = DataLoader(DS(items, TRAIN_TF), batch_size=BATCH, shuffle=True, num_workers=4)
    w, dist = class_weights(items)
    crit = nn.CrossEntropyLoss(weight=w)
    opt = torch.optim.AdamW(net.parameters(), lr=lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, epochs)
    print(f"[{tag}] {len(items)} imgs {dist} on {DEVICE}, {epochs} epochs")
    best, best_sd, best_conf = 0.0, None, None
    for ep in range(epochs):
        net.train()
        for x, y in loader:
            x, y = x.to(DEVICE), y.to(DEVICE)
            opt.zero_grad()
            crit(net(x), y).backward()
            opt.step()
        sched.step()
        if val is not None:
            acc, conf = evaluate(net, val)
            if acc >= best:
                best, best_conf = acc, conf
                best_sd = {k: v.detach().cpu().clone() for k, v in net.state_dict().items()}
            print(f"[{tag}] ep {ep:2d}  kiosk_val_acc={acc:.3f}  best={best:.3f}", flush=True)
    if best_sd is not None:
        net.load_state_dict(best_sd)
    return best, best_conf


def evaluate(net, items):
    net.eval()
    loader = DataLoader(DS(items, EVAL_TF), batch_size=BATCH, num_workers=4)
    correct = 0
    conf = torch.zeros(len(CLASSES), len(CLASSES), dtype=int)
    with torch.no_grad():
        for x, y in loader:
            pred = net(x.to(DEVICE)).argmax(1).cpu()
            correct += (pred == y).sum().item()
            for t, p in zip(y, pred):
                conf[t, p] += 1
    return correct / max(1, len(items)), conf


def main():
    kiosk = kiosk_items()
    if not kiosk:
        sys.exit("No kiosk captures with bin labels; run label_captures.py first.")
    # stratified 80/20 split of the kiosk data -> the honest eval set
    by = {c: [p for p, l in kiosk if l == c] for c in CLASSES}
    ktrain, kval = [], []
    for c, ps in by.items():
        random.shuffle(ps)
        k = max(1, int(len(ps) * 0.2))
        kval += [(p, c) for p in ps[:k]]
        ktrain += [(p, c) for p in ps[k:]]

    net = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.IMAGENET1K_V1)
    net.classifier[3] = nn.Linear(net.classifier[3].in_features, len(CLASSES))
    net = net.to(DEVICE)

    ext = external_items()
    if ext:
        run_epochs(net, ext, PRETRAIN_EPOCHS, 3e-4, "pretrain")  # stage 1
    else:
        print("No external_data/ found -- kiosk-only training. "
              "Run scripts/fetch_external.py for the two-stage boost.")

    best, conf = run_epochs(net, ktrain, FINETUNE_EPOCHS, 1e-4, "finetune", val=kval)  # stage 2

    print(f"\nBEST kiosk_val_acc = {best:.3f}  (n={len(kval)})")
    print("confusion (rows=true, cols=pred):", CLASSES)
    for i, c in enumerate(CLASSES):
        print(f"  {c:8s}", conf[i].tolist())

    net = net.to("cpu").eval()
    torch.onnx.export(net, torch.randn(1, 3, 224, 224), str(OUT_ONNX),
                      input_names=["input"], output_names=["logits"],
                      opset_version=13, dynamo=False)
    json.dump({"classes": CLASSES, "mean": MEAN, "std": STD}, open(OUT_JSON, "w"), indent=2)
    print(f"exported {OUT_ONNX.name} + {OUT_JSON.name}")


if __name__ == "__main__":
    main()
