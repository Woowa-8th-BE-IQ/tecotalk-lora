#!/usr/bin/env bash
# 씬의 일부 애니메이션 구간만 렌더
# 사용법: ./render_part.sh <파일> <클래스> <시작,끝> <출력이름> [품질]
#   ./render_part.sh s01_network NetworkToLoRA 0,11 s01a_network_intro m
set -euo pipefail
cd "$(dirname "$0")"
FILE="$1"; SCENE="$2"; RANGE="$3"; OUT="$4"; Q="${5:-l}"
"${PYTHON:-.venv/bin/python}" -m manim -q"$Q" "scenes/$FILE.py" "$SCENE" -n "$RANGE" -o "$OUT" --media_dir media
