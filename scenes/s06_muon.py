"""씬 6. Muon: 업데이트 행렬을 직교화 → 모든 방향 같은 세기. + QK-Clip.

렌더: ./render.sh s06_muon Muon
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from manim import *

from common.style import ACCENT, FG, LORA, MUTED, NEG, POS, t


def cap(s):
    return t(s, 36).to_edge(UP, buff=0.35)


def rot(a):
    return np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])


def unit_probe(color, n=8, r=1.0):
    circ = Circle(radius=r, color=color, stroke_width=3)
    arrows = VGroup(*[
        Arrow(ORIGIN, r * np.array([np.cos(a), np.sin(a), 0]), buff=0, color=color,
              stroke_width=3, max_tip_length_to_length_ratio=0.18)
        for a in np.linspace(0, TAU, n, endpoint=False)
    ])
    return VGroup(circ, arrows)


class Muon(Scene):
    def construct(self):
        caption = cap("Adam은 숫자 하나씩, Muon은 행렬 통째로")
        self.play(FadeIn(caption, shift=DOWN * 0.2))

        # ---------- 1) 숫자 하나씩 vs 행렬 통째로 ----------
        def cells(n_rows, n_cols, col, size=0.38):
            g = VGroup(*[Square(size, stroke_color="#22262F", stroke_width=1).set_fill(col, 0.75)
                         for _ in range(n_rows * n_cols)])
            g.arrange_in_grid(n_rows, n_cols, buff=0)
            return g

        left = cells(5, 5, POS).move_to(LEFT * 3.4 + DOWN * 0.3)
        right = cells(5, 5, LORA).move_to(RIGHT * 3.4 + DOWN * 0.3)
        l_t = t("Adam: 칸마다 따로 보폭", 26, POS).next_to(left, DOWN, buff=0.35)
        r_t = t("Muon: 행렬 전체를 한 번에", 26, LORA).next_to(right, DOWN, buff=0.35)
        self.play(FadeIn(left), FadeIn(right), FadeIn(l_t), FadeIn(r_t))
        self.play(LaggedStart(*[Indicate(c, color=ACCENT, scale_factor=1.25) for c in left[::3]], lag_ratio=0.15), run_time=1.6)
        frame = SurroundingRectangle(right, color=ACCENT, buff=0.06, stroke_width=4)
        self.play(Create(frame), right.animate.set_fill(ACCENT, 0.6), run_time=0.8)
        self.play(right.animate.set_fill(LORA, 0.75), FadeOut(frame))
        self.wait(0.5)
        self.play(*[FadeOut(m) for m in [left, right, l_t, r_t]])

        # ---------- 2) 행렬 = 공간을 늘리는 변환 ----------
        self.play(Transform(caption, cap("기울기 행렬 G는 한 방향만 세게 민다")))
        Vt = rot(0.35)
        U = rot(0.9)
        S = np.diag([2.3, 0.45])
        G = U @ S @ Vt
        Q = U @ Vt                     # Muon이 쓰는 직교화 결과

        lc, rc = LEFT * 3.4 + DOWN * 0.5, RIGHT * 3.4 + DOWN * 0.5
        plane_l = NumberPlane(x_range=[-3, 3], y_range=[-2.4, 2.4], x_length=6, y_length=4.8,
                              background_line_style=dict(stroke_color="#262B36", stroke_width=1),
                              axis_config=dict(stroke_color="#3A3F4B")).move_to(lc)
        plane_r = plane_l.copy().move_to(rc)
        pl = unit_probe(MUTED).move_to(lc)
        pr = unit_probe(MUTED).move_to(rc)
        self.play(FadeIn(plane_l), FadeIn(plane_r), Create(pl), Create(pr))
        tl = t("그대로 G", 26, POS).next_to(plane_l, UP, buff=0.1)
        tr = t("Muon: 직교화", 26, LORA).next_to(plane_r, UP, buff=0.1)
        self.play(FadeIn(tl))

        def apply(m, mob, center, color):
            M3 = np.eye(3)
            M3[:2, :2] = m
            return mob.animate.apply_matrix(M3, about_point=center).set_color(color)

        self.play(apply(G, pl, lc, POS), run_time=1.8)
        note = t("한 방향은 2.3배, 다른 방향은 0.45배", 24, POS).to_edge(DOWN, buff=0.4)
        self.play(FadeIn(note))
        self.wait(0.6)

        self.play(Transform(caption, cap("Muon: 방향은 살리고, 세기는 전부 1로")), FadeIn(tr))
        self.play(apply(Q, pr, rc, LORA), run_time=1.8)
        self.play(Transform(note, t("모든 방향을 같은 세기로 → 약한 방향도 학습된다", 24, LORA).to_edge(DOWN, buff=0.4)))
        self.wait(1.2)
        self.play(*[FadeOut(m) for m in [plane_l, plane_r, pl, pr, tl, tr, note]])

        # ---------- 3) 특이값 막대 ----------
        self.play(Transform(caption, cap("특이값으로 보면")))
        sv = [3.0, 1.4, 0.6, 0.25, 0.1, 0.04]
        base_y = -2.2

        def bars(vals, col, x0):
            g = VGroup()
            for k, v in enumerate(vals):
                b = Rectangle(width=0.45, height=max(v * 1.25, 0.02), stroke_width=0).set_fill(col, 0.95)
                b.move_to([x0 + k * 0.65, base_y, 0], aligned_edge=DOWN)
                g.add(b)
            return g

        b_before = bars(sv, POS, -5.4)
        b_after = bars([1.0] * len(sv), LORA, 1.6)
        floor = Line([-6, base_y, 0], [6, base_y, 0], color="#3A3F4B", stroke_width=1.5)
        lb = t("G: 몇 방향만 크다 (사실상 low-rank)", 24, POS).next_to(b_before, UP, buff=0.3)
        la = t("Muon 업데이트: 전부 1 (high-rank)", 24, LORA).next_to(b_after, UP, buff=0.3).shift(UP * 2.4)
        self.play(Create(floor), LaggedStart(*[GrowFromEdge(b, DOWN) for b in b_before], lag_ratio=0.1), FadeIn(lb))
        self.play(TransformFromCopy(b_before, b_after), run_time=1.3)
        la.next_to(b_after, UP, buff=0.3)
        self.play(FadeIn(la))
        ns = t("Newton–Schulz 반복 몇 번으로 근사 · SVD 없이 빠르게", 22, MUTED).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(ns))
        self.wait(1.6)
        self.play(*[FadeOut(m) for m in [b_before, b_after, floor, lb, la, ns]])

        # ---------- 4) QK-Clip ----------
        self.play(Transform(caption, cap("1조 파라미터로 키우니: logit 폭발")))
        ax = Axes(x_range=[0, 10, 1], y_range=[0, 10, 2], x_length=9, y_length=4.2,
                  axis_config=dict(color=MUTED, stroke_width=1.5, include_ticks=False), tips=False).shift(DOWN * 0.5)
        xl = t("학습 step", 22, MUTED).next_to(ax, DOWN, buff=0.15)
        yl = t("attention logit 최댓값", 22, MUTED).rotate(PI / 2).next_to(ax, LEFT, buff=0.2)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl))
        boom = ax.plot(lambda x: min(1 + 0.08 * np.exp(0.5 * x), 10), x_range=[0, 9.6], color=NEG, stroke_width=4)
        spike = t("학습 스파이크 → 실패", 24, NEG).next_to(ax.c2p(8.6, 9.5), LEFT, buff=0.2)
        self.play(Create(boom), run_time=1.6)
        self.play(FadeIn(spike))
        self.wait(0.4)

        tau = 4.5
        thr = DashedLine(ax.c2p(0, tau), ax.c2p(10, tau), color=ACCENT, stroke_width=2)
        thr_l = t("임계값 τ", 22, ACCENT).next_to(thr, RIGHT, buff=0.1)
        clipped = ax.plot(lambda x: min(1 + 0.08 * np.exp(0.5 * x), tau - 0.15 * np.exp(-(x - 6.5) ** 2)),
                          x_range=[0, 10], color=LORA, stroke_width=4)
        self.play(Transform(caption, cap("QK-Clip: 넘을 것 같으면 Wq, Wk를 줄인다")),
                  Create(thr), FadeIn(thr_l))
        self.play(Create(clipped), run_time=1.6)
        self.wait(0.5)

        result = VGroup(
            t("MuonClip = Muon + QK-Clip", 28, LORA),
            t("Kimi K2: 15.5T 토큰 사전학습, 스파이크 0번", 24, FG),
        ).arrange(DOWN, buff=0.12).to_edge(DOWN, buff=0.3)
        self.play(FadeOut(xl), FadeIn(result, shift=UP * 0.1))
        self.wait(2.5)
