"""모든 씬이 공유하는 색·폰트·헬퍼."""
from manim import Text, config

# 화면
BG = "#0F1115"
config.background_color = BG

# 색
FG = "#E8E8EC"        # 기본 글자
MUTED = "#7A7F8C"     # 보조 글자
FROZEN = "#3A3F4B"    # 얼린 가중치
POS = "#4C8DFF"       # 양수 가중치
NEG = "#FF5C5C"       # 음수 가중치
LORA = "#2BD9A0"      # LoRA 패치
ACCENT = "#FFB547"    # 강조

FONT = "Noto Sans CJK KR"


def t(s, size=32, color=FG, weight="NORMAL", **kw):
    """한글 텍스트 단축."""
    return Text(s, font=FONT, font_size=size, color=color, weight=weight, **kw)


def weight_color(w):
    return POS if w >= 0 else NEG


def weight_width(w):
    return 0.8 + 3.2 * min(abs(w), 1.0)
