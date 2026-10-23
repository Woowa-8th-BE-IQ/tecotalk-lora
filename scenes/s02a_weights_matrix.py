"""씬 2-a. 왜 가중치는 행렬인가: 연결선 → 행렬 칸. ΔW도 같은 모양. 4096 × 4096, 층마다 7개 × 32층 ≈ 70억.

렌더: ./render.sh s02a_weights_matrix WeightsAreMatrix
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from manim import *

from common.style import ACCENT, BG, FG, LORA, MUTED, NEG, POS, t


def cap(s, color=FG):
    return t(s, 34, color).to_edge(UP, buff=0.3)


class WeightsAreMatrix(Scene):
    def construct(self):
        c = cap("한 층 = 모든 입력이 모든 출력에 연결")
        self.play(FadeIn(c))
        xs = VGroup(*[Circle(0.28, color=POS, stroke_width=3).set_fill(BG, 1) for _ in range(3)]).arrange(DOWN, buff=0.55)
        hs = VGroup(*[Circle(0.28, color=ACCENT, stroke_width=3).set_fill(BG, 1) for _ in range(2)]).arrange(DOWN, buff=0.9)
        xs.move_to(LEFT * 4.6 + DOWN * 0.2)
        hs.move_to(LEFT * 1.4 + DOWN * 0.2)
        xl = VGroup(*[MathTex(f"x_{j+1}", font_size=30).move_to(xs[j]) for j in range(3)])
        hl = VGroup(*[MathTex(f"h_{i+1}", font_size=30).move_to(hs[i]) for i in range(2)])
        edges = VGroup()
        for i in range(2):
            for j in range(3):
                edges.add(Line(xs[j].get_center(), hs[i].get_center(), buff=0.3, stroke_color=MUTED, stroke_width=2.5))
        self.play(FadeIn(xs), FadeIn(xl), FadeIn(hs), FadeIn(hl))
        self.play(LaggedStart(*[Create(e) for e in edges], lag_ratio=0.12), run_time=1.2)
        n6 = t("선 6개 = 가중치 6개", 26, MUTED).to_edge(DOWN, buff=0.6)
        self.play(FadeIn(n6))

        grid = VGroup(*[Square(0.8, stroke_color="#3A3F4B", stroke_width=1.5) for _ in range(6)]).arrange_in_grid(2, 3, buff=0)
        grid.move_to(RIGHT * 3.4 + DOWN * 0.2)
        wl = VGroup(*[MathTex(f"w_{{{i+1}{j+1}}}", font_size=30).move_to(grid[i * 3 + j]) for i in range(2) for j in range(3)])
        rows_l = t("출력 2", 22, ACCENT).next_to(grid, LEFT, buff=0.25)
        cols_l = t("입력 3", 22, POS).next_to(grid, UP, buff=0.2)
        c2 = cap("입력 j → 출력 i 선의 숫자를 i행 j열에  =  행렬 W")
        self.play(FadeOut(c), FadeIn(c2), Create(grid), FadeIn(rows_l), FadeIn(cols_l))
        c = c2
        for k in range(6):
            self.play(Indicate(edges[k], color=LORA, scale_factor=1.0), TransformFromCopy(edges[k], wl[k]), run_time=0.4)
        hx = MathTex(r"h = W x", font_size=48).next_to(grid, DOWN, buff=0.35)
        self.play(FadeOut(n6), Write(hx))
        self.wait(0.6)

        c2 = cap("그래서 고칠 양 ΔW 도 같은 모양의 행렬", LORA)
        dgrid = grid.copy().set_stroke(LORA, 2)
        dl = VGroup(*[MathTex(r"\Delta w_{" + f"{i+1}{j+1}" + "}", font_size=26, color=LORA).move_to(grid[i * 3 + j])
                      for i in range(2) for j in range(3)])
        self.play(FadeOut(c), FadeIn(c2), Transform(grid, dgrid), Transform(wl, dl),
                  Transform(hx, MathTex(r"\Delta W", font_size=48, color=LORA).move_to(hx)))
        c = c2
        self.wait(1.2)

        # ---------- 실제 크기 ----------
        self.play(*[FadeOut(m) for m in self.mobjects if m is not c])
        c2 = cap("실제 크기는?  (Llama-2 7B 기준)")
        self.play(FadeOut(c), FadeIn(c2))
        c = c2
        big = Square(3.4, stroke_color=MUTED, stroke_width=2).set_fill(POS, 0.15).move_to(LEFT * 3.6 + DOWN * 0.3)
        lines = VGroup(*[Line(big.get_corner(UL) + RIGHT * 3.4 * k / 16, big.get_corner(DL) + RIGHT * 3.4 * k / 16,
                              stroke_width=0.5, stroke_color="#2A2E38") for k in range(1, 16)],
                       *[Line(big.get_corner(UL) + DOWN * 3.4 * k / 16, big.get_corner(UR) + DOWN * 3.4 * k / 16,
                              stroke_width=0.5, stroke_color="#2A2E38") for k in range(1, 16)])
        dim = t("4096 × 4096", 26, FG).next_to(big, DOWN, buff=0.2)
        cnt = t("= 약 1,677만 칸", 26, ACCENT).next_to(dim, DOWN, buff=0.1)
        self.play(FadeIn(big), Create(lines, lag_ratio=0.01), FadeIn(dim), FadeIn(cnt), run_time=1.2)

        calc = VGroup(
            t("층 하나에 이런 행렬 7개", 28, FG),
            t("Attention 4개 + FFN 3개", 22, MUTED),
            t("≈ 2억 개", 28, ACCENT),
            t("× 32층  + 임베딩", 28, FG),
            t("≈ 70억 개", 40, ACCENT),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT).move_to(RIGHT * 2.8 + DOWN * 0.1)
        for it in calc:
            self.play(FadeIn(it, shift=RIGHT * 0.15), run_time=0.5)
        end = t("4096 = 한 층의 폭,  70억 = 모든 행렬 칸의 합", 26, LORA).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(end))
        self.wait(2.2)
