# LoRA로 보는 파인튜닝과 학습의 원리

우아한테크코스 8기 테코톡 발표용 Manim 애니메이션.
발표는 **영상 재생 → 설명 → 다음 영상** 방식으로 진행한다.

> 처음 보는 사람(또는 새 채팅)은 **[`docs/00_HANDOFF.md`](docs/00_HANDOFF.md)** 부터 읽을 것.

## 핵심 메시지

1. 최적값은 **편미분**으로 찾는다: 하나만 남기고 고정해 미분 → 방향별 기울기를 모아 반대로 한 걸음.
2. 그 지형의 높이가 **손실**이고, 우리가 구하는 건 고칠 양 **ΔW**다.
3. **LoRA**는 거대한 ΔW를 작은 행렬 두 개(B × A)로 표현해서 학습한다. 원본 W는 그대로.

## 본편 영상 (발표 순서)

| 순서 | 내용 | 파일 · 클래스 |
|---|---|---|
| 1 | 편미분: 하나 고정 → 단면 → 방향별 델타 → 반대로 한 걸음 (η) | `s00_partial` · `PartialDerivative` |
| 2 | 공 굴리기: 나침반(방향별 증감) + 손실 지형 | `s00e_ball` · `BallDescent` |
| (선택) | 손실 계산: 다음 단어 확률 → −log p | `s00a_loss` · `LossCalc` |
| 3 | ΔW: 가중치 4096개로 확장, 가중치는 표(행렬), 실제 크기 | `s00b_delta_w` · `DeltaW` |
| 4 | 작은 행렬 두 개로 큰 행렬: 구구단표 → 패턴 → 근사 → 학습 | `s02c_lora_matrix` · `LoRAMatrix` |

나머지 장면은 이전 버전, 추가 후보, 백업이다. 목록은 [`docs/05_PRODUCTION.md`](docs/05_PRODUCTION.md).

## 문서

| 문서 | 내용 |
|---|---|
| [`docs/00_HANDOFF.md`](docs/00_HANDOFF.md) | 전체 요약, 현재 상태, 열린 문제, 다음 할 일 |
| [`docs/01_MESSAGE.md`](docs/01_MESSAGE.md) | 전달하려는 메시지와 시나리오 |
| [`docs/02_SCRIPT.md`](docs/02_SCRIPT.md) | 영상별 발표 대본 |
| [`docs/03_CONCEPTS.md`](docs/03_CONCEPTS.md) | 개념, 숫자, 정확성 주의점, 예상 질문 |
| [`docs/04_DECISIONS.md`](docs/04_DECISIONS.md) | 넣고 뺀 것과 이유 |
| [`docs/05_PRODUCTION.md`](docs/05_PRODUCTION.md) | 환경, 렌더, 검수, 장면 파일 지도 |

## 빠른 실행

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
./render.sh s02c_lora_matrix LoRAMatrix m          # 720p
python3 tools/contact_sheet.py media/videos/s02c_lora_matrix/720p30/LoRAMatrix.mp4 check.png 12
```

자세한 환경 설정은 `docs/05_PRODUCTION.md`.
