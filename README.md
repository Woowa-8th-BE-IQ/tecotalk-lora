# LoRA로 보는 파인튜닝과 학습의 원리

우아한테크코스 8기 테코톡 발표용 Manim 애니메이션.

## 발표 순서

| # | 단계 | 내용 | 파일 · 클래스 |
|---|---|---|---|
| 01 | 배경 | 모델 = 숫자로 이어진 선, 순전파 | `s01_network` `NetworkToLoRA` (-n 0,11) |
| 02 | 배경 | 손실: 다음 단어 확률 → −log p → 평균 | `s00a_loss` `LossCalc` |
| 03 | 배경 | 가중치 1개: 기울기 반대로 한 걸음 | `s04_learning_rate` `LearningRate` (-n 0,11) |
| 04 | 배경 | 편미분: 단면 → 방향별 델타 → 기울기 → η | `s00_partial` `PartialDerivative` |
| 05 | 배경 | 역전파 (연쇄법칙 없이, LLM 버전) | `s00c_backprop` `Backprop` |
| 06 | 배경 | 배치와 울퉁불퉁한 로스 곡선 | `s00d_curve` `TrainingCurve` |
| 07 | 문제 | GPT-3 175B 풀 파인튜닝 비용 | `s01c_problem` `ProblemScale` |
| 08 | 해결 | 원본 얼리고 우회로 (B=0 시작, 두 길 합산) | `s01_network` `NetworkToLoRA` (-n 12) |
| 09 | 전체 그림 | h = Wx + (α/r)·BAx 지도 | `s01d_roadmap` `Roadmap` |
| 10 | 세부 | 왜 가중치는 행렬인가, 4096 vs 70억 | `s02a_weights_matrix` `WeightsAreMatrix` |
| 11 | 세부 | ΔW = B × A, 0.39% | `s02_matrix` `LowRankSplit` |
| 12 | 세부 | r 트레이드오프 (비용↑, 성능 포화) | `s02b_rank_tradeoff` `RankTradeoff` |
| 13 | 세부 | α, α/r, target modules | `s03_hyperparams` `Hyperparams` |
| 14 | 세부 | 학습률 크기별 비교 | `s04_learning_rate` `LearningRate` (-n 13) |
| 15 | 세부 | SGD vs Momentum vs AdamW | `s05_optimizers` `Optimizers3D` |
| 16 | 회수 | LoRA 논문 결과 | `s01c_problem` `PaperResult` |
| 17 | 확장 | 활성 파라미터(MoE) vs LoRA | `s07_active_params` `ActiveParams` |
| 18 | 마무리 | 넓게 배우고 좁게 고친다 | `s08_outro` `Outro` |
| B1 | 백업 | Muon, QK-Clip | `s06_muon` `Muon` |
| B2 | 백업 | ΔW와 연쇄법칙, δ·xᵀ = rank 1 | `s00b_delta_w` `DeltaW` |

구간 렌더: `./render_part.sh <파일> <클래스> <시작,끝> <출력이름> [품질]`

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
