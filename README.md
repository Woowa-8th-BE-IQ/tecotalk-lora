# LoRA로 보는 파인튜닝과 학습의 원리

우아한테크코스 8기 테코톡 발표용 Manim 애니메이션.

## 씬

| # | 파일 | 클래스 | 내용 |
|---|---|---|---|
| 1 | `s01_network.py` | `NetworkToLoRA` | 신경망 = 가중치 → 풀 파인튜닝 vs LoRA 우회로 |
| 2 | `s02_matrix.py` | `LowRankSplit` | ΔW = B × A, r 다이얼, 0.39% |
| 3 | (예정) | | r, α, target modules |
| 4 | (예정) | | 학습률 2D: 보폭별 수렴/발산 |
| 5 | (예정) | | 3D 손실 골짜기: SGD vs Momentum vs AdamW |
| 6 | (선택) | | Muon: 골짜기 펴기 |

## 실행

```bash
# macOS
brew install py3cairo ffmpeg pango pkg-config
brew install --cask mactex-no-gui   # 수식(MathTex)용

python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

./render.sh s01_network NetworkToLoRA      # 480p 미리보기
./render.sh s01_network NetworkToLoRA h    # 1080p 발표용
```

결과: `media/videos/<파일>/<해상도>/<클래스>.mp4`

## 스타일

색과 폰트는 `common/style.py` 한 곳에서 관리. 한글은 `Noto Sans CJK KR`.
