#!/usr/bin/env bash
# 사용법: ./render.sh <파일명(확장자 없이)> <씬 클래스> [품질: l|m|h|k]
#   ./render.sh s01_network NetworkToLoRA      # 미리보기 480p
#   ./render.sh s01_network NetworkToLoRA h    # 발표용 1080p
set -euo pipefail
cd "$(dirname "$0")"
FILE="$1"; SCENE="$2"; Q="${3:-l}"
PY="${PYTHON:-.venv/bin/python}"
"$PY" -m manim -q"$Q" "scenes/$FILE.py" "$SCENE" --media_dir media
