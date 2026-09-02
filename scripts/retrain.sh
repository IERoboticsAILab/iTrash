#!/usr/bin/env bash
# One-command retrain loop for the local CNN backend. Run from the Mac (or any
# machine that can SSH to the Pi and run PyTorch).
#
#   ./scripts/retrain.sh
#
# It: (1) labels all captures on the Pi with GPT, (2) pulls captures + labels
# here, (3) fine-tunes MobileNetV3-small and exports ONNX, (4) ships the model
# back to the Pi, (5) restarts the kiosk on AI_BACKEND=cnn.
#
# Env overrides: PI=pi@host  PI_REPO=iTrash  RESTART=0 (skip kiosk restart)
set -euo pipefail

PI="${PI:-pi@10.205.3.84}"
PI_REPO="${PI_REPO:-iTrash}"
RESTART="${RESTART:-1}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
TRAIN_VENV="$REPO/.venv-train"

# Training deps live in a dedicated venv so we never touch the Pi's runtime env.
if [ ! -x "$TRAIN_VENV/bin/python" ]; then
  echo "==> Creating training venv (one-time; installs torch, ~200MB)"
  python3 -m venv "$TRAIN_VENV"
  "$TRAIN_VENV/bin/pip" install -q --upgrade pip
  "$TRAIN_VENV/bin/pip" install -q torch torchvision onnx onnxscript pillow python-dotenv
fi

echo "==> 1/5 Labeling captures on $PI (GPT is the teacher)"
ssh "$PI" "cd ~/$PI_REPO && .venv/bin/python scripts/label_captures.py"

echo "==> 2/5 Pulling captures + labels to $REPO"
mkdir -p "$REPO/captured_images" "$REPO/models"
# rsync is incremental, so repeat runs only copy new frames.
rsync -a "$PI:~/$PI_REPO/captured_images/" "$REPO/captured_images/"
scp -q "$PI:~/$PI_REPO/models/labels.csv" "$REPO/models/labels.csv"

echo "==> 3/5 Training + exporting ONNX"
cd "$REPO" && "$TRAIN_VENV/bin/python" scripts/train_cnn.py

echo "==> 4/5 Deploying model to $PI"
scp -q "$REPO/models/trash_cnn.onnx" "$REPO/models/trash_cnn.json" "$PI:~/$PI_REPO/models/"

if [ "$RESTART" = "1" ]; then
  echo "==> 5/5 Restarting kiosk on AI_BACKEND=cnn"
  # [m]ain.py bracket-trick so pkill doesn't match this very command line.
  ssh "$PI" "cd ~/$PI_REPO && sudo pkill -f '[m]ain.py' 2>/dev/null; sleep 2; \
    setsid sudo AI_BACKEND=cnn DISPLAY=:0 XAUTHORITY=/home/pi/.Xauthority \
    .venv/bin/python main.py >~/itrash_cnn.log 2>&1 </dev/null & \
    sleep 10; grep -E 'Loaded CNN|System ready|Error|Traceback' ~/itrash_cnn.log | tail -5"
else
  echo "==> 5/5 Skipped restart (RESTART=0). On the Pi, relaunch main.py with AI_BACKEND=cnn."
fi

echo "==> Done. Review the confusion matrix above; brown improves as organic captures grow."
