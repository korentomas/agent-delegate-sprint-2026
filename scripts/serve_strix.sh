#!/usr/bin/env bash
# Run inside the user's existing rocmfpx distrobox; loopback only.
set -euo pipefail
source "$HOME/qwen38-stack/rocm-env.sh"
DELEGATE_LLAMA_SERVER="${DELEGATE_LLAMA_SERVER:-$HOME/qwen38-stack/llama.cpp/build-hip/bin/llama-server}"
DELEGATE_MODEL="${DELEGATE_MODEL:-$HOME/models/agent-delegate/Qwen3-4B-Instruct-2507-Q4_K_M.gguf}"
exec "$DELEGATE_LLAMA_SERVER" -m "$DELEGATE_MODEL" -ngl 99 -fa on --jinja -fit off --parallel 1 -c 8192 --host 127.0.0.1 --port "${DELEGATE_PORT:-8094}"
