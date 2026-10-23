"""씬 1-d. 전체 그림: h = Wx + (α/r)·BAx 한 장에 오늘 볼 것들.

렌더: ./render.sh s01d_roadmap Roadmap
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import *

from common.style import ACCENT, FG, LORA, MUTED, POS, t


def cap(s, color=FG):
    return t(s, 34, color).to_edge(UP, buff=0.3)


class Roadmap(Scene):
    def construct(self):
        c = cap("오늘의 지도: 식 하나")
        self.play(FadeIn(c))
        f = MathTex(r"h", "=", r"W", r"x", "+", r"\frac{\alpha}{r}", r"B", r"A", r"x", font_size=84).shift(UP * 0.9)
        self.play(Write(f), run_time=1.6)
        self.wait(0.4)

        def callout(part, text, color, direction, buff=0.55, size=26):
            br = Brace(part, direction, color=color, buff=0.12)
            lab = t(text, size, color).next_to(br, direction, buff=0.15)
            if direction is DOWN and lab.get_left()[0] < br.get_left()[0]:
                lab.align_to(br, LEFT)
            return VGroup(br, lab)

        steps = [
            (f[2], "원본 · 얼린다", MUTED, DOWN),
            (VGroup(f[6], f[7]), "무엇을: 작은 행렬 2개", LORA, DOWN),
            (f[5], "얼마나: r = 두께,  α = 볼륨", ACCENT, UP),
        ]
        calls = VGroup()
        for part, text, col, d in steps:
            part.generate_target()
            part.target.set_color(col)
            co = callout(part, text, col, d)
            self.play(MoveToTarget(part), GrowFromCenter(co[0]), FadeIn(co[1]), run_time=0.8)
            calls.add(co)
            self.wait(0.5)

        below = VGroup(
            t("어디에:  target modules  (Wq, Wk, Wv, Wo, FFN …)", 26, FG),
            t("어떻게 학습:  학습률 η  ·  옵티마이저 AdamW", 26, POS),
        ).arrange(DOWN, buff=0.25, aligned_edge=LEFT).to_edge(DOWN, buff=0.9)
        for b in below:
            self.play(FadeIn(b, shift=UP * 0.1), run_time=0.6)
        self.wait(1.2)

        order = t("순서:  B·A 분해  →  r  →  α · target  →  학습률  →  옵티마이저", 26, ACCENT).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(order))
        self.wait(2.2)
