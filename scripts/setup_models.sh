#!/usr/bin/env bash
set -euo pipefail

cat <<'MSG'
Yojana Mitra model setup

Place offline model files in these folders:

  models/llm/model.gguf
  models/embeddings/bge-small-en-v1.5/
  models/ocr/
  models/whisper/ggml-small.bin

This script intentionally does not download anything by default, so the
runtime application remains air-gapped. Add manual download commands here
only for a one-time connected setup machine.
MSG
