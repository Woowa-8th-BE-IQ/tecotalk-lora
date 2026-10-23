# 영상 제작 가이드

## 환경

```bash
# macOS
brew install py3cairo ffmpeg pango pkg-config
brew install --cask mactex-no-gui        # MathTex(수식)용

# Ubuntu (Claude 작업 환경에서 실제로 필요했던 것)
apt-get install -y libpango1.0-dev dvisvgm

python3 -m venv .venv
.venv/bin/pip install -U pip setuptools wheel
.venv/bin/pip install -r requirements.txt     # manim==0.22.0, numpy
```

- 한글 폰트: `Noto Sans CJK KR` (`common/style.py`의 `FONT`). 없으면 설치하거나 바꿀 것.
- 시스템 파이썬에 manim을 깔면 Debian 패키지와 충돌한다. **반드시 venv.**
- LaTeX 수식 안에 한글을 넣지 않는다 (kotex 없음). 한글은 `Text`로 따로.

## 렌더

```bash
./render.sh <파일> <클래스> [l|m|h|k]        # l=480p 미리보기, m=720p, h=1080p
./render.sh s02c_lora_matrix LoRAMatrix m

# 애니메이션 구간만 (n번째부터 m번째)
./render_part.sh <파일> <클래스> <시작,끝> <출력이름> [품질]
```

- 결과: `media/videos/<파일>/<해상도>/<클래스>.mp4`
- 3D 장면(`s00_partial`, `s00e_ball`, `s05_optimizers`)은 720p에 5~10분. 먼저 `l`로 확인.

## 검수 (필수)

렌더할 때마다 프레임을 뽑아서 눈으로 본다. 겹침, 잘림, 잔상이 자주 생긴다.

```bash
python3 tools/contact_sheet.py media/videos/.../X.mp4 check.png 12
```

자주 생긴 문제와 해결:

| 문제 | 해결 |
|---|---|
| 자막·라벨 겹침 | `to_edge(DOWN, buff=…)`로 줄 분리, 이전 텍스트를 `FadeOut` |
| 화면 밖 잘림 | 배치 좌표 조정 (화면은 가로 약 ±7.1, 세로 ±4) |
| 3D 장면에서 고정 텍스트가 엉뚱한 곳에 | `add_fixed_in_frame_mobjects` 후 `remove`, `FadeIn`으로 등장. 카메라 `frame_center`를 옮기지 말고 3D 물체 자체를 이동 |
| 3D 장면에서 `Indicate` 잔상 | 고정 객체에는 `Indicate` 대신 `animate.set_stroke(width=…)` |
| `always_redraw`가 고정 객체에서 깨짐 | 같은 구조를 유지하는 `add_updater` + `become`/`set_stroke` 사용 |

## 스타일

- 배경 `#0F1115`, 색은 `common/style.py`에 모아 둠.
  - `POS` 파랑(양수), `NEG` 빨강(음수), `LORA` 초록(패치·내리막), `ACCENT` 주황(강조·η), `MUTED` 회색.
  - 편미분 x 방향 = 주황, y 방향 = 보라(`#B48CFF`).
- 자막은 화면 위쪽 한 줄, 34pt 안팎. 짧게.

## 장면 파일 지도

### 본편 (현재)

| 파일 | 클래스 | 내용 |
|---|---|---|
| `s00_partial.py` | `PartialDerivative` | 영상 1. 편미분 (3D) |
| `s00e_ball.py` | `BallDescent` | 영상 2. 나침반 + 공 굴리기 (3D) |
| `s00a_loss.py` | `LossCalc` | 선택. 손실 계산 (LLM 다음 단어) |
| `s00b_delta_w.py` | `DeltaW` | 영상 3. ΔW, 가중치는 표, 실제 크기 |
| `s02c_lora_matrix.py` | `LoRAMatrix` | 영상 4. 작은 행렬 두 개로 큰 행렬 |

### 이전 버전 / 추가 후보 / 백업

| 파일 | 클래스 | 내용 | 상태 |
|---|---|---|---|
| `s01_network.py` | `NetworkToLoRA` | 신경망 → LoRA 우회로 (B=0, 두 길 합산) | 신경망 제외 결정으로 본편 밖 |
| `s00c_backprop.py` | `Backprop` | 역전파 (LLM 다음 단어, 연쇄법칙 없이) | 본편 밖 |
| `s00d_curve.py` | `TrainingCurve` | 배치, 울퉁불퉁한 로스 곡선 | 추가 후보 |
| `s01c_problem.py` | `ProblemScale`, `PaperResult` | GPT-3 175B 비용 / 논문 결과 | 추가 후보 |
| `s01d_roadmap.py` | `Roadmap` | h = Wx + (α/r)BAx 지도 | 추가 후보 |
| `s02_matrix.py` | `LowRankSplit` | ΔW = B × A, r 다이얼, 0.39% | 영상 4와 겹침 |
| `s02a_weights_matrix.py` | `WeightsAreMatrix` | 연결선 → 행렬 칸 | 신경망 제외로 본편 밖 |
| `s02b_rank_tradeoff.py` | `RankTradeoff` | r↑ 비용·성능 포화 (개념도) | 추가 후보 |
| `s03_hyperparams.py` | `Hyperparams` | α, α/r, target modules | 추가 후보 |
| `s04_learning_rate.py` | `LearningRate` | 학습률 크기별 비교 | 추가 후보 |
| `s05_optimizers.py` | `Optimizers3D` | SGD vs Momentum vs AdamW (3D) | 추가 후보 |
| `s06_muon.py` | `Muon` | Muon, QK-Clip | 백업 |
| `s07_active_params.py` | `ActiveParams` | MoE 활성 파라미터 | 백업 |
| `s08_outro.py` | `Outro` | 마무리, 요약 | 추가 후보 |
