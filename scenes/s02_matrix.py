"""씬 2. 큰 행렬 ΔW = 가는 B × 납작한 A. 파라미터 수 비교.

렌더: ./render.sh s02_matrix LowRankSplit
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from manim import *

from common.style import ACCENT, BG, FG, FROZEN, LORA, MUTED, NEG, POS, t

N = 16          # 화면에 그리는 칸 수 (실제 d=4096을 축소해서 표현)
CELL = 0.2
D_REAL = 4096
R_MAX = 8


def cell_color(v, vmax):
    a = min(1.0, abs(v) / vmax)
    return interpolate_color(ManimColor(BG), ManimColor(POS if v >= 0 else NEG), 0.15 + 0.85 * a)


def grid(M, cell=CELL, vmax=None, stroke="#22262F"):
    M = np.atleast_2d(M)
    vmax = vmax or (np.abs(M).max() + 1e-9)
    rows, cols = M.shape
    g = VGroup()
    for i in range(rows):
        for j in range(cols):
            sq = Square(cell, stroke_width=0.6, stroke_color=stroke)
            sq.set_fill(cell_color(M[i, j], vmax), 1)
            sq.move_to([(j - (cols - 1) / 2) * cell, -(i - (rows - 1) / 2) * cell, 0])
            g.add(sq)
    g.shape = (rows, cols)
    return g


def cell_at(g, i, j):
    return g[i * g.shape[1] + j]


def fmt(n):
    return f"{n:,}"


class LowRankSplit(Scene):
    def construct(self):
        rng = np.random.default_rng(5)
        Bfull = rng.normal(0, 1, (N, R_MAX))
        Afull = rng.normal(0, 1, (R_MAX, N))

        def dW(r):
            return Bfull[:, :r] @ Afull[:r] / np.sqrt(r)

        def cap(s):
            return t(s, 36).to_edge(UP, buff=0.35)

        caption = cap("가중치 W = 큰 행렬 하나")

        # 1) W
        W = grid(rng.normal(0, 1, (N, N)))
        W_dim = t(f"{D_REAL} × {D_REAL}", 26, MUTED).next_to(W, DOWN, buff=0.25)
        W_cnt = t(f"{fmt(D_REAL * D_REAL)}개", 34, ACCENT).next_to(W_dim, DOWN, buff=0.2)
        self.play(FadeIn(caption, shift=DOWN * 0.2))
        self.play(LaggedStart(*[FadeIn(c) for c in W], lag_ratio=0.003), run_time=1.4)
        self.play(FadeIn(W_dim), FadeIn(W_cnt, shift=UP * 0.1))
        self.wait(1.0)

        # 2) 파인튜닝 = W + ΔW
        W_grp = VGroup(W, W_dim, W_cnt)
        dW8 = grid(dW(R_MAX))
        plus = MathTex("+", font_size=60, color=FG)
        W_frozen_target = VGroup(W.copy(), W_dim.copy())
        lhs = VGroup(W, plus, dW8).arrange(RIGHT, buff=0.5)
        self.play(
            Transform(caption, cap("파인튜닝 = W에 ΔW를 더하는 것")),
            FadeOut(W_cnt), FadeOut(W_dim),
            W.animate.move_to(lhs[0]),
        )
        lab_W = MathTex("W", font_size=44, color=MUTED).next_to(W, DOWN, buff=0.25)
        lab_dW = MathTex(r"\Delta W", font_size=44, color=FG).next_to(dW8, DOWN, buff=0.25)
        plus.move_to(lhs[1])
        dW8.move_to(lhs[2])
        self.play(FadeIn(plus), LaggedStart(*[FadeIn(c) for c in dW8], lag_ratio=0.003), run_time=1.2)
        self.play(FadeIn(lab_W), FadeIn(lab_dW))
        self.play(*[c.animate.set_fill(interpolate_color(c.get_fill_color(), ManimColor(FROZEN), 0.75)) for c in W])
        self.wait(0.8)

        # 3) ΔW만 남기고 왼쪽으로
        self.play(
            Transform(caption, cap("LoRA의 가설: ΔW는 생각보다 단순하다")),
            FadeOut(W), FadeOut(plus), FadeOut(lab_W),
            VGroup(dW8, lab_dW).animate.move_to(LEFT * 3.6),
        )
        self.wait(0.6)

        # 4) ΔW = B × A
        r = 2
        dWr = grid(dW(r)).move_to(dW8)
        B = grid(Bfull[:, :r])
        A = grid(Afull[:r])
        eq = MathTex("=", font_size=60)
        times = MathTex(r"\times", font_size=50)
        rhs = VGroup(eq, B, times, A).arrange(RIGHT, buff=0.45).next_to(dW8, RIGHT, buff=0.55)
        lab_B = MathTex("B", font_size=44, color=LORA).next_to(B, DOWN, buff=0.25)
        lab_A = MathTex("A", font_size=44, color=LORA).next_to(A, DOWN, buff=0.25)
        dim_B = t("4096 × r", 22, MUTED).next_to(lab_B, DOWN, buff=0.12)
        dim_A = t("r × 4096", 22, MUTED).next_to(lab_A, DOWN, buff=0.12)

        self.play(Transform(dW8, dWr), Transform(caption, cap("큰 행렬 = 가는 B × 납작한 A")))
        self.play(
            FadeIn(eq), FadeIn(times),
            TransformFromCopy(dW8, B), TransformFromCopy(dW8, A),
            run_time=1.4,
        )
        self.play(FadeIn(lab_B), FadeIn(lab_A), FadeIn(dim_B), FadeIn(dim_A))
        self.wait(0.8)

        # 5) 칸 하나 = B의 행 · A의 열
        i, j = 4, 11
        hl = dict(stroke_color=ACCENT, stroke_width=4)
        rowB = VGroup(*[cell_at(B, i, k) for k in range(r)])
        colA = VGroup(*[cell_at(A, k, j) for k in range(r)])
        target = cell_at(dW8, i, j)
        boxes = VGroup(
            SurroundingRectangle(rowB, buff=0.02, **hl),
            SurroundingRectangle(colA, buff=0.02, **hl),
            SurroundingRectangle(target, buff=0.02, **hl),
        )
        self.play(Transform(caption, cap("칸 하나 = B의 행 · A의 열")))
        self.play(Create(boxes[0]), Create(boxes[1]))
        self.play(TransformFromCopy(VGroup(boxes[0], boxes[1]), boxes[2]), run_time=0.9)
        self.wait(0.8)
        sweeps = [(1, 3), (9, 6), (13, 14)]
        for (ii, jj) in sweeps:
            nb = VGroup(
                SurroundingRectangle(VGroup(*[cell_at(B, ii, k) for k in range(r)]), buff=0.02, **hl),
                SurroundingRectangle(VGroup(*[cell_at(A, k, jj) for k in range(r)]), buff=0.02, **hl),
                SurroundingRectangle(cell_at(dW8, ii, jj), buff=0.02, **hl),
            )
            self.play(Transform(boxes, nb), run_time=0.45)
        self.play(FadeOut(boxes))
        self.wait(0.3)

        # 6) r 다이얼
        def lora_cnt(rr):
            return 2 * D_REAL * rr

        r_lab = t(f"r = {r}", 32, LORA).to_corner(UR, buff=0.5).shift(DOWN * 0.7)
        cnt = t(f"학습: {fmt(lora_cnt(r))}개", 28, FG).next_to(r_lab, DOWN, aligned_edge=RIGHT, buff=0.15)
        self.play(Transform(caption, cap("r = 표현력 다이얼")), FadeIn(r_lab), FadeIn(cnt))
        for rr in [1, 4, 8]:
            nB = grid(Bfull[:, :rr])
            nA = grid(Afull[:rr])
            nrhs = VGroup(eq.copy(), nB, times.copy(), nA).arrange(RIGHT, buff=0.45).next_to(dW8, RIGHT, buff=0.55)
            self.play(
                Transform(B, nB), Transform(A, nA),
                eq.animate.move_to(nrhs[0]), times.animate.move_to(nrhs[2]),
                Transform(dW8, grid(dW(rr)).move_to(dW8)),
                lab_B.animate.next_to(nB, DOWN, buff=0.25), lab_A.animate.next_to(nA, DOWN, buff=0.25),
                dim_B.animate.next_to(lab_B.copy().next_to(nB, DOWN, buff=0.25), DOWN, buff=0.12),
                dim_A.animate.next_to(lab_A.copy().next_to(nA, DOWN, buff=0.25), DOWN, buff=0.12),
                Transform(r_lab, t(f"r = {rr}", 32, LORA).move_to(r_lab, aligned_edge=RIGHT)),
                Transform(cnt, t(f"학습: {fmt(lora_cnt(rr))}개", 28, FG).move_to(cnt, aligned_edge=RIGHT)),
                run_time=1.0,
            )
            self.wait(0.6)

        # 7) 막대 비교 (r = 8)
        full_n = D_REAL * D_REAL
        lora_n = lora_cnt(R_MAX)
        everything = VGroup(dW8, lab_dW, eq, B, times, A, lab_B, lab_A, dim_B, dim_A, r_lab, cnt)
        self.play(
            Transform(caption, cap("r = 8일 때, 얼마나 작을까?")),
            everything.animate.scale(0.7).shift(UP * 0.6),
        )
        bar_w = 10.0
        x0 = -bar_w / 2
        y_full, y_lora = -2.0, -2.9
        full_bar = Rectangle(width=bar_w, height=0.45, stroke_width=0).set_fill(MUTED, 0.9)
        full_bar.move_to([0, y_full, 0])
        lora_bar = Rectangle(width=max(bar_w * lora_n / full_n, 0.04), height=0.45, stroke_width=0).set_fill(LORA, 1)
        lora_bar.move_to([x0, y_lora, 0], aligned_edge=LEFT)
        full_txt = t(f"풀 파인튜닝  {fmt(full_n)}", 24, FG).next_to(full_bar, UP, aligned_edge=LEFT, buff=0.1)
        lora_txt = t(f"LoRA  {fmt(lora_n)}", 24, LORA).next_to(lora_bar, RIGHT, buff=0.2)
        self.play(GrowFromEdge(full_bar, LEFT), FadeIn(full_txt), run_time=1.0)
        self.play(GrowFromEdge(lora_bar, LEFT), FadeIn(lora_txt), run_time=0.8)
        pct = t(f"{100 * lora_n / full_n:.2f}%", 64, LORA, weight="BOLD").move_to([3.2, y_lora - 0.05, 0])
        self.play(FadeIn(pct, scale=1.4))
        self.wait(2.5)
