"""씬 0-d. 실제 학습: 문장 묶음(배치)마다 평균 손실로 한 걸음 → 울퉁불퉁하게 내려가는 로스 곡선.

렌더: ./render.sh s00d_curve TrainingCurve
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from manim import *

from common.style import ACCENT, FG, LORA, MUTED, POS, t

ERR = "#FF5C5C"
N = 200


def cap(s, color=FG):
    return t(s, 34, color).to_edge(UP, buff=0.3)


class TrainingCurve(Scene):
    def construct(self):
        rng = np.random.default_rng(4)
        k = np.arange(N)
        smooth = 2.6 * np.exp(-k / 45) + 0.55
        noisy = smooth + rng.normal(0, 0.18, N) * (0.4 + smooth / 3)
        noisy = np.clip(noisy, 0.2, 4.0)

        # ---------- 1) 배치 ----------
        c = cap("한 걸음 = 문장 묶음(배치)의 평균 손실로")
        self.play(FadeIn(c))
        cards = VGroup(*[RoundedRectangle(corner_radius=0.08, width=1.1, height=0.55, stroke_color=MUTED, stroke_width=1.5)
                         .set_fill(MUTED, 0.12) for _ in range(24)]).arrange_in_grid(4, 6, buff=0.12)
        cards.move_to(LEFT * 3.2 + DOWN * 0.3)
        lab = t("학습 데이터: 문장 수천 개", 22, MUTED).next_to(cards, DOWN, buff=0.25)
        self.play(LaggedStart(*[FadeIn(cd) for cd in cards], lag_ratio=0.02), FadeIn(lab))
        batches = [[0, 7, 13, 20], [3, 9, 16, 22], [1, 11, 14, 19]]
        bl = [2.71, 2.44, 2.58]
        out = t("", 30).move_to(RIGHT * 3.0)
        self.add(out)
        for b, l in zip(batches, bl):
            self.play(*[cards[i].animate.set_stroke(ACCENT, 3).set_fill(ACCENT, 0.3) for i in b], run_time=0.4)
            new = VGroup(t("이 묶음의 평균 손실", 22, MUTED), t(f"{l:.2f}", 40, ERR),
                         t("→ 기울기 → 한 걸음", 22, LORA)).arrange(DOWN, buff=0.15).move_to(RIGHT * 3.0)
            self.play(Transform(out, new), run_time=0.5)
            self.play(*[cards[i].animate.set_stroke(MUTED, 1.5).set_fill(MUTED, 0.12) for i in b], run_time=0.3)
        note = t("묶음마다 문장이 달라서, 걸음마다 방향이 조금씩 흔들린다", 24, MUTED).to_edge(DOWN, buff=0.4)
        self.play(FadeIn(note))
        self.wait(1.0)
        self.play(*[FadeOut(m) for m in [cards, lab, out, note]])

        # ---------- 2) 로스 곡선 ----------
        c2 = cap("그래서 로스 곡선은 울퉁불퉁하게 내려간다")
        self.play(FadeOut(c), FadeIn(c2))
        c = c2
        ax = Axes(x_range=[0, N, 50], y_range=[0, 4, 1], x_length=10, y_length=4.6,
                  axis_config=dict(color=MUTED, stroke_width=1.5, include_ticks=False), tips=False).shift(DOWN * 0.4)
        xl = t("걸음 (step)", 22, MUTED).next_to(ax, DOWN, buff=0.15)
        yl = t("손실", 22, MUTED).next_to(ax, UP, buff=0.05).align_to(ax, LEFT)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl))
        pts = [ax.c2p(i, v) for i, v in enumerate(noisy)]
        raw = VMobject(stroke_color=ERR, stroke_width=2, stroke_opacity=0.55).set_points_as_corners(pts)
        self.play(Create(raw), run_time=3.5, rate_func=linear)
        sm = VMobject(stroke_color=ERR, stroke_width=4).set_points_smoothly([ax.c2p(i, v) for i, v in zip(k[::5], smooth[::5])])
        smlab = t("추세", 22, ERR).next_to(sm.get_end(), UP, buff=0.15)
        self.play(Create(sm), FadeIn(smlab), run_time=1.2)
        ex = t("예시 곡선", 18, MUTED).to_corner(DR, buff=0.4)
        self.play(FadeIn(ex))
        self.wait(0.8)

        hook = VGroup(
            t("얼마나 빠르고, 얼마나 안정적으로 내려갈지", 26, FG),
            t("= 학습률과 옵티마이저가 정한다  (뒤에서)", 26, ACCENT),
        ).arrange(DOWN, buff=0.15).to_edge(DOWN, buff=0.25)
        self.play(FadeOut(xl), FadeIn(hook, shift=UP * 0.1))
        self.wait(2.2)
