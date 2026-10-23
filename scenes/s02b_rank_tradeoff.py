"""씬 2-b. r 트레이드오프: r↑ → 비용(학습 숫자) 직선 증가, 성능은 금방 포화 (개념도).

렌더: ./render.sh s02b_rank_tradeoff RankTradeoff
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from manim import *

from common.style import ACCENT, FG, LORA, MUTED, NEG, POS, t

RS = [1, 2, 4, 8, 16, 32, 64]
D = 4096


def cap(s, color=FG):
    return t(s, 34, color).to_edge(UP, buff=0.3)


class RankTradeoff(Scene):
    def construct(self):
        c = cap("r 을 키우면 어떻게 될까?")
        self.play(FadeIn(c))

        # ---------- 1) 비용: 학습 숫자 ----------
        ax1 = Axes(x_range=[0, 6, 1], y_range=[0, 3.2, 1], x_length=5.4, y_length=3.6,
                   axis_config=dict(color=MUTED, stroke_width=1.5, include_ticks=False), tips=False).move_to(LEFT * 3.4 + DOWN * 0.5)
        ax2 = ax1.copy().move_to(RIGHT * 3.4 + DOWN * 0.5)
        for ax in (ax1, ax2):
            for i, r in enumerate(RS):
                ax.add(t(str(r), 18, MUTED).next_to(ax.c2p(i, 0), DOWN, buff=0.12))
        xl1 = t("r", 22, MUTED).next_to(ax1, DOWN, buff=0.45)
        xl2 = t("r", 22, MUTED).next_to(ax2, DOWN, buff=0.45)
        h1 = t("비용: 학습할 숫자", 26, NEG).next_to(ax1, UP, buff=0.25)
        h2 = t("성능", 26, LORA).next_to(ax2, UP, buff=0.25)

        # 학습 숫자 = 2·4096·r (한 행렬).  r=64 → 52만 → y=3 으로 맞춤
        cost = [2 * D * r for r in RS]
        cmax = cost[-1]
        bars = VGroup()
        for i, v in enumerate(cost):
            h = 3.0 * v / cmax
            b = Rectangle(width=0.45, height=max(h * ax1.y_length / 3.2, 0.02), stroke_width=0).set_fill(NEG, 0.85)
            b.move_to(ax1.c2p(i, 0), aligned_edge=DOWN)
            bars.add(b)
        self.play(Create(ax1), FadeIn(xl1), FadeIn(h1))
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.12), run_time=1.2)
        vals = VGroup(t("8,192", 18, NEG).next_to(bars[0], UP, buff=0.08),
                      t("65,536", 18, NEG).next_to(bars[3], UP, buff=0.08),
                      t("524,288", 18, NEG).next_to(bars[6], UP, buff=0.08))
        self.play(FadeIn(vals))
        lin = t("r 두 배 → 비용 두 배", 22, MUTED).next_to(ax1, DOWN, buff=0.85)
        self.play(FadeIn(lin))
        self.wait(0.8)

        # ---------- 2) 성능: 포화 (개념도) ----------
        perf = lambda x: 2.75 * (1 - np.exp(-(x + 0.6) / 0.9))
        self.play(Create(ax2), FadeIn(xl2), FadeIn(h2))
        pc = ax2.plot(perf, x_range=[0, 6], color=LORA, stroke_width=4)
        self.play(Create(pc), run_time=1.6)
        sat = DashedLine(ax2.c2p(0, 2.75), ax2.c2p(6, 2.75), color=LORA, stroke_width=1.5, stroke_opacity=0.5)
        sl = t("금방 평평해진다", 22, LORA).next_to(ax2.c2p(4.5, 2.75), UP, buff=0.12)
        self.play(Create(sat), FadeIn(sl))
        over = ax2.plot(lambda x: perf(x) - 0.06 * max(0, x - 3.5) ** 2, x_range=[3.5, 6], color=ACCENT,
                        stroke_width=2.5).set_stroke(opacity=0.8)
        over = DashedVMobject(over, num_dashes=14)
        ol = t("데이터가 적으면 과적합", 20, ACCENT).next_to(ax2.c2p(5.4, 2.3), DOWN, buff=0.1)
        self.play(Create(over), FadeIn(ol))
        concept = t("개념도 · 실제 곡선은 과제마다 다름", 18, MUTED).next_to(ax2, DOWN, buff=0.85)
        self.play(FadeIn(concept))
        self.wait(0.8)

        # ---------- 3) 결론 ----------
        band1 = Rectangle(width=ax1.c2p(5, 0)[0] - ax1.c2p(3, 0)[0] + 0.5, height=ax1.y_length + 0.2,
                          stroke_width=0).set_fill(LORA, 0.1).move_to([(ax1.c2p(3, 0)[0] + ax1.c2p(5, 0)[0]) / 2, ax1.get_center()[1], 0])
        band2 = band1.copy().move_to([(ax2.c2p(3, 0)[0] + ax2.c2p(5, 0)[0]) / 2, ax2.get_center()[1], 0])
        bl = t("보통 8 ~ 32 에서 시작", 22, LORA).next_to(band2, UP, buff=0.05)
        self.play(FadeIn(band1), FadeIn(band2), FadeOut(sl), FadeOut(h2), FadeIn(bl))
        end = t("작게 시작하고, 부족할 때만 올린다", 32, ACCENT).to_edge(DOWN, buff=0.25)
        self.play(FadeOut(lin), FadeOut(concept), FadeIn(end, shift=UP * 0.1))
        self.wait(2.4)
