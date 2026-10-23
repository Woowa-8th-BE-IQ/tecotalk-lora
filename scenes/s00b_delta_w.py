"""씬 0-b. 편미분 식 → 숫자 → Δz.  차원 확장 → ΔW.  왜 행렬?  층이 쌓이면 연쇄법칙.

렌더: ./render.sh s00b_delta_w DeltaW
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from manim import *

from common.style import ACCENT, BG, FG, FROZEN, LORA, MUTED, NEG, POS, t

YCOL = "#B48CFF"
TAN = "#FF5C5C"


def cap(s, color=FG):
    return t(s, 34, color).to_edge(UP, buff=0.35)


def num_cell(v, size=0.75, color=None, fs=26):
    sq = Square(size, stroke_color="#3A3F4B", stroke_width=1.5)
    if color is not None:
        sq.set_fill(color, 0.25)
    lab = t(f"{v:g}", fs, FG).move_to(sq)
    return VGroup(sq, lab)


class DeltaW(Scene):
    def swap(self, old, new):
        self.play(FadeOut(old), FadeIn(new), run_time=0.6)
        return new

    def clear_except(self, *keep):
        self.play(*[FadeOut(m) for m in self.mobjects if m not in keep], run_time=0.6)

    def construct(self):
        # ================= 1) 편미분은 식, 점을 넣으면 숫자 =================
        c = cap("편미분은 '식'이다")
        f_tex = MathTex(r"z = 0.15x^2 + 0.25y^2 + 0.2xy + 0.5", font_size=40, color=MUTED).next_to(c, DOWN, buff=0.4)
        self.play(FadeIn(c), Write(f_tex))

        gx = MathTex(r"\frac{\partial z}{\partial x}", "=", "0.3", "x", "+", "0.2", "y", font_size=46)
        gy = MathTex(r"\frac{\partial z}{\partial y}", "=", "0.2", "x", "+", "0.5", "y", font_size=46)
        gx[0].set_color(ACCENT)
        gy[0].set_color(YCOL)
        VGroup(gx, gy).arrange(DOWN, buff=0.5, aligned_edge=LEFT).shift(LEFT * 1.5 + DOWN * 0.3)
        self.play(Write(gx))
        self.play(Write(gy))
        self.wait(0.6)

        pt = t("점 (x, y) = (1.5, 1) 을 넣으면", 30, ACCENT).to_edge(DOWN, buff=0.9)
        c = self.swap(c, cap("점을 넣으면 '숫자'가 된다"))
        self.play(FadeIn(pt))
        gx2 = MathTex(r"\frac{\partial z}{\partial x}", "=", "0.3", r"(1.5)", "+", "0.2", r"(1)", "=", "0.65", font_size=46)
        gy2 = MathTex(r"\frac{\partial z}{\partial y}", "=", "0.2", r"(1.5)", "+", "0.5", r"(1)", "=", "0.80", font_size=46)
        gx2[0].set_color(ACCENT)
        gy2[0].set_color(YCOL)
        gx2[8].set_color(ACCENT)
        gy2[8].set_color(YCOL)
        gx2.move_to(gx, aligned_edge=LEFT)
        gy2.move_to(gy, aligned_edge=LEFT)
        self.play(TransformMatchingTex(gx, gx2), TransformMatchingTex(gy, gy2), run_time=1.4)
        self.wait(1.0)

        # ================= 2) 숫자 × 변화량 = Δz =================
        c = self.swap(c, cap("기울기 × 작은 변화량  =  z의 변화량"))
        self.play(FadeOut(pt), FadeOut(f_tex), VGroup(gx2, gy2).animate.scale(0.75).to_edge(UP, buff=1.2))
        dz = MathTex(r"\Delta z", r"\approx", r"0.65", r"\cdot", r"\Delta x", "+", r"0.80", r"\cdot", r"\Delta y", font_size=56)
        dz[2].set_color(ACCENT)
        dz[6].set_color(YCOL)
        dz.shift(DOWN * 0.1)
        self.play(Write(dz))
        self.wait(0.6)
        dz2 = MathTex(r"\Delta z", r"\approx", r"0.65", r"\cdot", r"0.1", "+", r"0.80", r"\cdot", r"0.1", "=", r"0.145",
                      font_size=56).move_to(dz)
        dz2[2].set_color(ACCENT)
        dz2[6].set_color(YCOL)
        dz2[10].set_color(LORA)
        ex = t("Δx = 0.1,  Δy = 0.1 만큼 움직이면", 28, MUTED).next_to(dz, DOWN, buff=0.5)
        self.play(FadeIn(ex))
        self.play(TransformMatchingTex(dz, dz2))
        real = t("실제로 계산하면 0.151  ·  작게 움직일수록 정확", 26, MUTED).next_to(ex, DOWN, buff=0.3)
        self.play(FadeIn(real))
        self.wait(1.6)
        self.clear_except(c)

        # ================= 3) 차원 확장 =================
        c = self.swap(c, cap("가중치가 4096개라면?  (높이 z = 손실 L)"))
        map1 = VGroup(
            MathTex(r"z", r"\ \longrightarrow\ ", r"L", font_size=48),
            MathTex(r"(x,\ y)", r"\ \longrightarrow\ ", r"(w_1,\ w_2,\ \dots,\ w_{4096})", font_size=48),
        ).arrange(DOWN, buff=0.45)
        map1[0][2].set_color(NEG)
        map1[1][2].set_color(POS)
        notes = VGroup(t("손실", 24, NEG).next_to(map1[0][2], RIGHT, buff=0.3),
                       t("가중치", 24, POS).next_to(map1[1][2], RIGHT, buff=0.3))
        self.play(Write(map1[0]), FadeIn(notes[0]))
        self.play(Write(map1[1]), FadeIn(notes[1]))
        self.wait(1.0)
        self.play(FadeOut(map1), FadeOut(notes))

        dL = MathTex(r"\Delta L", r"\approx",
                     r"\frac{\partial L}{\partial w_1}\Delta w_1", "+",
                     r"\frac{\partial L}{\partial w_2}\Delta w_2", "+", r"\cdots", "+",
                     r"\frac{\partial L}{\partial w_{4096}}\Delta w_{4096}", font_size=42)
        dL.shift(UP * 0.6)
        self.play(Write(dL), run_time=1.8)
        same = t("2차원과 똑같다: 방향별 델타를 전부 더한다", 26, MUTED).next_to(dL, DOWN, buff=0.5)
        self.play(FadeIn(same))
        self.wait(1.0)

        c = self.swap(c, cap("우리가 찾는 것 = 각 Δw, 즉 ΔW", LORA))
        boxes = VGroup(*[SurroundingRectangle(dL[i], color=LORA, buff=0.06) for i in (2, 4, 8)])
        self.play(Create(boxes))
        self.wait(0.6)

        pick = MathTex(r"\Delta w_i", "=", r"-\eta", r"\frac{\partial L}{\partial w_i}", font_size=50)
        pick[0].set_color(LORA)
        pick[2].set_color(ACCENT)
        pick.next_to(same, DOWN, buff=0.6)
        self.play(FadeOut(same), Write(pick))
        then = t("편미분 수천, 수십억 개도 컴퓨터가 한 번에 계산해 준다", 26, MUTED).next_to(pick, DOWN, buff=0.45)
        self.play(FadeIn(then))
        c = self.swap(c, cap("기울기 반대로 걸으면 손실이 줄어든다", LORA))
        self.wait(1.8)
        self.clear_except(c)

        # ================= 4) 가중치는 표(행렬)로 저장된다 =================
        c = self.swap(c, cap("그런데 LLM의 가중치 w들은 어떻게 저장돼 있을까?"))
        grid = VGroup(*[Square(0.9, stroke_color="#3A3F4B", stroke_width=1.5) for _ in range(9)]).arrange_in_grid(3, 3, buff=0)
        grid.move_to(DOWN * 0.3)
        wl = VGroup(*[MathTex(f"w_{{{i+1}{j+1}}}", font_size=32).move_to(grid[i * 3 + j]) for i in range(3) for j in range(3)])
        self.play(Create(grid), LaggedStart(*[FadeIn(w) for w in wl], lag_ratio=0.08), run_time=1.2)
        W_lab = MathTex("W", font_size=48).next_to(grid, DOWN, buff=0.3)
        c = self.swap(c, cap("숫자들이 줄과 칸으로 묶인 큰 표  =  행렬 W"))
        self.play(FadeIn(W_lab))
        self.wait(0.8)
        dgrid = grid.copy().set_stroke(LORA, 2)
        dl = VGroup(*[MathTex(r"\Delta w_{" + f"{i+1}{j+1}" + "}", font_size=28, color=LORA).move_to(grid[i * 3 + j])
                      for i in range(3) for j in range(3)])
        c = self.swap(c, cap("그래서 고칠 양 ΔW 도 같은 모양의 표", LORA))
        self.play(Transform(grid, dgrid), Transform(wl, dl),
                  Transform(W_lab, MathTex(r"\Delta W", font_size=48, color=LORA).move_to(W_lab)))
        self.wait(1.4)
        self.clear_except(c)

        # ================= 5) 실제 크기 =================
        c = self.swap(c, cap("실제 크기는?  (Llama-2 7B 기준)"))
        big = Square(3.0, stroke_color=MUTED, stroke_width=2).set_fill(LORA, 0.12).move_to(LEFT * 3.6 + UP * 0.1)
        lines = VGroup(*[Line(big.get_corner(UL) + RIGHT * 3.0 * k / 16, big.get_corner(DL) + RIGHT * 3.0 * k / 16,
                              stroke_width=0.5, stroke_color="#2A2E38") for k in range(1, 16)],
                       *[Line(big.get_corner(UL) + DOWN * 3.0 * k / 16, big.get_corner(UR) + DOWN * 3.0 * k / 16,
                              stroke_width=0.5, stroke_color="#2A2E38") for k in range(1, 16)])
        dlab = MathTex(r"\Delta W", font_size=40, color=LORA).next_to(big, UP, buff=0.15)
        dim = t("4096 × 4096", 26, FG).next_to(big, DOWN, buff=0.2)
        cnt = t("= 약 1,677만 칸", 26, ACCENT).next_to(dim, DOWN, buff=0.1)
        self.play(FadeIn(big), Create(lines, lag_ratio=0.01), FadeIn(dlab), FadeIn(dim), FadeIn(cnt), run_time=1.2)
        calc = VGroup(
            t("층 하나에 이런 행렬 7개", 28, FG),
            t("Attention 4개 + FFN 3개", 22, MUTED),
            t("× 32층  + 임베딩", 28, FG),
            t("≈ 70억 칸", 40, ACCENT),
        ).arrange(DOWN, buff=0.25, aligned_edge=LEFT).move_to(RIGHT * 2.8 + DOWN * 0.1)
        for it in calc:
            self.play(FadeIn(it, shift=RIGHT * 0.15), run_time=0.5)
        self.wait(0.8)
        burden = t("ΔW 70억 칸 전부  →  기울기, 옵티마이저 기록까지 함께 들고 있어야 한다", 24, MUTED).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(burden))
        self.wait(1.4)

        # ================= 6) LoRA 로 가는 질문 =================
        q = t("이 큰 ΔW 를, 작은 행렬 두 개로 표현할 수 없을까?", 32, LORA).to_edge(DOWN, buff=0.3)
        self.play(FadeOut(burden), FadeIn(q, shift=UP * 0.1), Indicate(big, color=LORA, scale_factor=1.03))
        self.wait(2.4)
