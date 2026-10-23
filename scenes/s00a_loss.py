"""씬 0-a. 손실 계산: LLM 다음 단어 확률 → 정답 확률 → −log → 손실. 여러 문장의 평균 = 손실 하나.

렌더: ./render.sh s00a_loss LossCalc
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from manim import *

from common.style import ACCENT, BG, FG, LORA, MUTED, NEG, POS, t

TOKENS = ["김밥", "라면", "피자", "국밥"]
P0 = [0.053, 0.37, 0.12, 0.457]      # 학습 전 (씬 0-c 의 실제 계산값과 같음)
P1 = [0.74, 0.07, 0.10, 0.09]        # 학습 후
ERR = "#FF5C5C"


def cap(s, color=FG):
    return t(s, 34, color).to_edge(UP, buff=0.3)


class LossCalc(Scene):
    def construct(self):
        c = cap("LLM은 다음 단어를 맞히는 모델")
        sent = VGroup(t("나는 오늘 점심에", 40, FG),
                      RoundedRectangle(corner_radius=0.1, width=1.6, height=0.7, stroke_color=ACCENT, stroke_width=2.5))
        sent.arrange(RIGHT, buff=0.3).next_to(c, DOWN, buff=0.45)
        q = t("?", 36, ACCENT).move_to(sent[1])
        self.play(FadeIn(c), FadeIn(sent), FadeIn(q))
        self.wait(0.4)

        # ---------- 확률 막대 ----------
        base_y = -2.6
        H = 4.0
        xs = [-5.2, -3.6, -2.0, -0.4]

        def bars(P, hi=None):
            g = VGroup()
            for i, (tok, p) in enumerate(zip(TOKENS, P)):
                col = LORA if i == 0 else MUTED
                b = Rectangle(width=1.0, height=max(p * H, 0.03), stroke_width=0).set_fill(col, 0.9 if i == 0 else 0.55)
                b.move_to([xs[i], base_y, 0], aligned_edge=DOWN)
                pl = t(f"{p * 100:.1f}%" if p < 0.1 else f"{p * 100:.0f}%", 24, FG).next_to(b, UP, buff=0.1)
                tl = t(tok, 26, col).move_to([xs[i], base_y - 0.35, 0])
                g.add(VGroup(b, pl, tl))
            return g

        floor = Line([-6, base_y, 0], [0.4, base_y, 0], color="#3A3F4B", stroke_width=1.5)
        B0 = bars(P0)
        c2 = cap("모델의 답 = 단어마다 확률")
        self.play(FadeOut(c), FadeIn(c2), Create(floor), LaggedStart(*[GrowFromEdge(b[0], DOWN) for b in B0], lag_ratio=0.15))
        self.play(*[FadeIn(b[1]) for b in B0], *[FadeIn(b[2]) for b in B0])
        c = c2
        self.wait(0.6)

        # 정답 표시
        ans = t("정답: 김밥", 28, LORA).next_to(B0[0][2], DOWN, buff=0.2)
        box = SurroundingRectangle(B0[0], color=LORA, buff=0.12)
        c2 = cap("그런데 정답은 '김밥'  →  김밥에 겨우 5.3%", ERR)
        self.play(FadeOut(c), FadeIn(c2), Create(box), FadeIn(ans), Transform(q, t("김밥", 30, LORA).move_to(sent[1])))
        c = c2
        self.wait(0.8)

        # ---------- −log 곡선 ----------
        ax = Axes(x_range=[0, 1, 0.25], y_range=[0, 4, 1], x_length=4.6, y_length=3.6,
                  axis_config=dict(color=MUTED, stroke_width=1.5, include_ticks=False), tips=False)
        ax.move_to([3.9, -0.8, 0])
        curve = ax.plot(lambda p: -np.log(p), x_range=[0.02, 1], color=ERR, stroke_width=3)
        xl = t("정답에 준 확률", 20, MUTED).next_to(ax, DOWN, buff=0.15)
        yl = t("손실", 20, MUTED).next_to(ax, UP, buff=0.05).align_to(ax, LEFT)
        formula = VGroup(MathTex(r"\text{loss} = -\log\,p", font_size=40),
                         t("p = 정답에 준 확률", 22, MUTED)).arrange(DOWN, buff=0.12)
        formula.next_to(ax, UP, buff=0.35)
        c2 = cap("손실 = 정답에 준 확률이 낮을수록 크다")
        self.play(FadeOut(c), FadeIn(c2), Create(ax), Create(curve), FadeIn(xl), FadeIn(yl), Write(formula))
        c = c2

        pv = ValueTracker(P0[0])
        dot = always_redraw(lambda: Dot(ax.c2p(pv.get_value(), -np.log(pv.get_value())), radius=0.1, color=ACCENT))
        guide = always_redraw(lambda: DashedLine(ax.c2p(pv.get_value(), 0), ax.c2p(pv.get_value(), -np.log(pv.get_value())),
                                                 color=ACCENT, stroke_width=2))
        val = always_redraw(lambda: t(f"손실 {-np.log(pv.get_value()):.2f}", 28, ACCENT)
                            .next_to(ax.c2p(pv.get_value(), -np.log(pv.get_value())), RIGHT, buff=0.2))
        self.play(FadeIn(dot), Create(guide), FadeIn(val))
        self.wait(1.2)

        # ---------- 학습 후 ----------
        B1 = bars(P1)
        c2 = cap("학습해서 김밥 확률이 오르면  →  손실이 줄어든다", LORA)
        self.play(FadeOut(c), FadeIn(c2), Transform(B0, B1), box.animate.become(SurroundingRectangle(B1[0], color=LORA, buff=0.12)),
                  pv.animate.set_value(P1[0]), run_time=2.2)
        c = c2
        self.wait(0.8)
        zero = t("100% 를 주면 손실 0", 22, MUTED).move_to(ax.c2p(0.62, 2.6))
        self.play(FadeIn(zero))
        self.wait(1.0)

        # ---------- 여러 문장의 평균 ----------
        self.play(*[FadeOut(m) for m in self.mobjects if m is not c])
        c2 = cap("실제로는 문장 수천 개  →  손실의 평균 하나")
        self.play(FadeOut(c), FadeIn(c2))
        c = c2
        rows = [("나는 오늘 점심에", "김밥", 2.94), ("하늘이 오늘따라", "맑다", 0.41), ("커밋 메시지를", "작성한다", 1.20),
                ("우테코 8기", "크루", 0.73), ("비가 와서 우산을", "챙겼다", 1.85)]
        table = VGroup()
        for s, a, l in rows:
            r = VGroup(t(s, 26, FG), t(a, 26, LORA), t(f"{l:.2f}", 26, ERR)).arrange(RIGHT, buff=0.5)
            table.add(r)
        table.arrange(DOWN, buff=0.28, aligned_edge=LEFT).shift(UP * 0.3 + LEFT * 0.8)
        for r in table:
            r[2].move_to([3.2, r[2].get_y(), 0])
        hdr = VGroup(t("문장", 20, MUTED).move_to([table.get_left()[0] + 0.4, table.get_top()[1] + 0.4, 0]),
                     t("손실", 20, MUTED).move_to([3.2, table.get_top()[1] + 0.4, 0]))
        self.play(FadeIn(hdr), LaggedStart(*[FadeIn(r, shift=RIGHT * 0.15) for r in table], lag_ratio=0.2), run_time=1.6)
        dots = t("⋮", 30, MUTED).next_to(table, DOWN, buff=0.15)
        line = Line([2.2, dots.get_bottom()[1] - 0.15, 0], [4.2, dots.get_bottom()[1] - 0.15, 0], color=MUTED, stroke_width=1.5)
        avg = t("평균 1.43", 32, ERR).next_to(line, DOWN, buff=0.15).align_to(line, RIGHT)
        self.play(FadeIn(dots), Create(line))
        self.play(LaggedStart(*[Indicate(r[2], color=ERR, scale_factor=1.2) for r in table], lag_ratio=0.15), run_time=1.0)
        self.play(FadeIn(avg, shift=DOWN * 0.15))
        self.wait(0.6)

        end = VGroup(
            t("가중치 70억 개를 넣으면  →  손실 숫자 1개가 나오는 함수", 28, FG),
            t("학습 = 이 숫자 하나를 줄이도록 가중치를 고치는 것", 28, ACCENT),
        ).arrange(DOWN, buff=0.2).to_edge(DOWN, buff=0.4)
        self.play(FadeIn(end[0], shift=UP * 0.1))
        self.wait(1.0)
        self.play(FadeIn(end[1], shift=UP * 0.1))
        self.wait(2.2)
