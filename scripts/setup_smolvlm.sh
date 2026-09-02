#!/usr/bin/env bash
# Build llama.cpp and fetch SmolVLM2-500M for fully local trash classification.
# Target: Raspberry Pi 4 (aarch64) running a 64-bit OS. Idempotent - safe to re-run.
#
#   ./scripts/setup_smolvlm.sh          # build + download + smoke test
#   ./scripts/setup_smolvlm.sh serve    # just run the server in the foreground
#
# Expect ~20-30 min for the first build on a Pi 4. Subsequent runs are instant.

set -euo pipefail

LLAMA_DIR="${LLAMA_DIR:-$HOME/llama.cpp}"
MODEL_REPO="ggml-org/SmolVLM2-500M-Video-Instruct-GGUF"
# Only Q8_0 and F16 are published for this model. Q8_0 (437MB) is the right
# pick: Q4 degrades disproportionately at 500M, and RAM is not the constraint.
MODEL_QUANT="Q8_0"
PORT="${PORT:-8081}"
THREADS="${THREADS:-4}"
SERVER_BIN="$LLAMA_DIR/build/bin/llama-server"

if [ "$(uname -m)" != "aarch64" ] && [ "$(uname -m)" != "arm64" ]; then
  echo "WARNING: $(uname -m) detected. On a Pi this must be aarch64 -"
  echo "         a 32-bit Raspberry Pi OS will be markedly slower. Continuing anyway."
fi

serve() {
  echo "==> Serving $MODEL_REPO on port $PORT (Ctrl+C to stop)"
  # --jinja is required: SmolVLM's chat template drives image token placement.
  # -ngl 0 keeps everything on CPU; the Pi 4 VideoCore is not a compute device.
  exec "$SERVER_BIN" \
    -hf "$MODEL_REPO:$MODEL_QUANT" \
    --host 127.0.0.1 --port "$PORT" \
    --threads "$THREADS" \
    --ctx-size 4096 \
    -ngl 0 \
    --jinja
}

if [ "${1:-}" = "serve" ]; then
  [ -x "$SERVER_BIN" ] || { echo "ERROR: $SERVER_BIN missing. Run without 'serve' first."; exit 1; }
  serve
fi

echo "==> Installing build dependencies"
sudo apt-get update
# libcurl is not optional here: it is what backs the -hf model downloader.
sudo apt-get install -y build-essential cmake git libcurl4-openssl-dev

echo "==> Fetching llama.cpp into $LLAMA_DIR"
# Fetch the source tarball rather than `git clone`. Some Pi network/git setups
# force authentication on anonymous github.com clones (HTTP 401), but the
# codeload tarball endpoint serves the same tree with no auth. No .git is kept;
# re-running just re-downloads, which is fine for a pinned build tool.
if [ ! -f "$LLAMA_DIR/CMakeLists.txt" ]; then
  rm -rf "$LLAMA_DIR"
  mkdir -p "$LLAMA_DIR"
  curl -fsSL "https://codeload.github.com/ggml-org/llama.cpp/tar.gz/refs/heads/master" \
    | tar xz -C "$LLAMA_DIR" --strip-components=1
fi

echo "==> Building (only the two targets we need, to save a lot of Pi time)"
cmake -S "$LLAMA_DIR" -B "$LLAMA_DIR/build" \
  -DCMAKE_BUILD_TYPE=Release \
  -DLLAMA_CURL=ON \
  -DGGML_NATIVE=ON
cmake --build "$LLAMA_DIR/build" -j"$(nproc)" --target llama-server llama-mtmd-cli

echo
echo "==> Build complete."
echo
echo "    Next:  $0 serve"
echo
echo "    The first 'serve' downloads ~440MB (weights + vision projector) into"
echo "    ~/.cache/llama.cpp before it starts listening. Later runs start instantly."
echo "    Run it as your normal user, NOT with sudo, or the cache lands in /root."
echo
echo "    Then, in a second shell:  ./scripts/smoke_smolvlm.py"
echo "    Then, to run iTrash:      AI_BACKEND=smolvlm sudo -E .venv/bin/python main.py"
