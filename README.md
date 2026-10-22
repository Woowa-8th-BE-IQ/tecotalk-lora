# LoRA로 보는 파인튜닝과 학습의 원리

우아한테크코스 8기 테코톡 발표용 Manim 애니메이션.

## 씬

| # | 파일 | 클래스 | 내용 |
|---|---|---|---|
| 0 | `s00_partial.py` | `PartialDerivative` | 편미분: 하나 고정 → 단면 → 방향별 델타 → 기울기 (렌더 약 5분) |
| 0-b | `s00b_delta_w.py` | `DeltaW` | 편미분 식→숫자→Δz, ΔW, 왜 행렬인가, 연쇄법칙, δ·xᵀ = rank 1 |
| 1 | `s01_network.py` | `NetworkToLoRA` | 신경망 = 가중치 → 풀 파인튜닝 vs LoRA 우회로 |
| 2 | `s02_matrix.py` | `LowRankSplit` | ΔW = B × A, r 다이얼, 0.39% |
| 3 | `s03_hyperparams.py` | `Hyperparams` | α 볼륨, α/r, target modules, 기본값 |
| 4 | `s04_learning_rate.py` | `LearningRate` | 학습률 = 보폭, 4가지 η 비교, 로스 곡선 |
| 5 | `s05_optimizers.py` | `Optimizers3D` | 3D 골짜기: SGD vs Momentum vs AdamW (렌더 약 5분) |
| 6 | `s06_muon.py` | `Muon` | Muon 직교화, 특이값, QK-Clip |
| 7 | `s07_active_params.py` | `ActiveParams` | MoE 활성 파라미터 vs LoRA |
| 8 | `s08_outro.py` | `Outro` | 넓게 배우고 좁게 고치기, 요약, 엔딩 |

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
