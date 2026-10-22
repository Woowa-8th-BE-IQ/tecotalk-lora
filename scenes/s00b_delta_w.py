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
        c = self.swap(c, cap("입력이 4096개라면?"))
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
        then = MathTex(r"\Rightarrow\ \Delta L \approx -\eta \sum_i \left(\frac{\partial L}{\partial w_i}\right)^2 < 0",
                       font_size=42).next_to(pick, DOWN, buff=0.4)
        self.play(Write(then))
        c = self.swap(c, cap("기울기 반대로 고르면 손실은 반드시 줄어든다", LORA))
        self.wait(1.8)
        self.clear_except(c)

        # ================= 4) 왜 행렬인가 =================
        c = self.swap(c, cap("그런데 신경망에서 w들은 어떻게 생겼나?"))
        xs = VGroup(*[Circle(0.28, color=POS, stroke_width=3).set_fill(BG, 1) for _ in range(3)]).arrange(DOWN, buff=0.55)
        hs = VGroup(*[Circle(0.28, color=ACCENT, stroke_width=3).set_fill(BG, 1) for _ in range(2)]).arrange(DOWN, buff=0.9)
        xs.move_to(LEFT * 4.6 + DOWN * 0.3)
        hs.move_to(LEFT * 1.4 + DOWN * 0.3)
        xl = VGroup(*[MathTex(f"x_{j+1}", font_size=30).move_to(xs[j]) for j in range(3)])
        hl = VGroup(*[MathTex(f"h_{i+1}", font_size=30).move_to(hs[i]) for i in range(2)])
        edges = VGroup()
        for i in range(2):
            for j in range(3):
                edges.add(Line(xs[j].get_center(), hs[i].get_center(), buff=0.3, stroke_color=MUTED, stroke_width=2.5))
        self.play(FadeIn(xs), FadeIn(xl), FadeIn(hs), FadeIn(hl))
        self.play(LaggedStart(*[Create(e) for e in edges], lag_ratio=0.12), run_time=1.2)
        allc = t("모든 입력이 모든 출력에 연결된다  →  선 6개 = 숫자 6개", 26, MUTED).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(allc))

        # 선 → 행렬 칸
        grid = VGroup(*[Square(0.8, stroke_color="#3A3F4B", stroke_width=1.5) for _ in range(6)]).arrange_in_grid(2, 3, buff=0)
        grid.move_to(RIGHT * 3.4 + DOWN * 0.3)
        wl = VGroup(*[MathTex(f"w_{{{i+1}{j+1}}}", font_size=30).move_to(grid[i * 3 + j]) for i in range(2) for j in range(3)])
        rows_l = t("출력 2", 22, ACCENT).next_to(grid, LEFT, buff=0.25)
        cols_l = t("입력 3", 22, POS).next_to(grid, UP, buff=0.2)
        W_lab = MathTex("W", font_size=44).next_to(grid, DOWN, buff=0.3)
        c = self.swap(c, cap("입력 j → 출력 i 선의 숫자를  i행 j열에 놓으면 = 행렬"))
        self.play(Create(grid), FadeIn(rows_l), FadeIn(cols_l))
        for k in range(6):
            self.play(Indicate(edges[k], color=LORA, scale_factor=1.0),
                      TransformFromCopy(edges[k], wl[k]), run_time=0.45)
        self.play(FadeIn(W_lab))
        hx = MathTex(r"h = W x", font_size=48).next_to(W_lab, DOWN, buff=0.25)
        self.play(FadeOut(allc), Write(hx))
        self.wait(0.8)
        sameW = t("그래서 ΔW도 같은 모양의 행렬. 실제로는 4096 × 4096", 26, LORA).to_edge(DOWN, buff=0.45)
        self.play(FadeIn(sameW))
        self.wait(1.6)
        self.clear_except(c)

        # ================= 5) 층이 쌓이면: 연쇄법칙 =================
        c = self.swap(c, cap("층이 쌓이면?  W₁은 L에 직접 닿지 않는다"))

        def node(lbl, col, w=1.1):
            r = RoundedRectangle(corner_radius=0.12, width=w, height=0.8, stroke_color=col, stroke_width=2.5).set_fill(col, 0.12)
            return VGroup(r, MathTex(lbl, font_size=38).move_to(r))

        nx, nh, ny, nL = node("x", POS), node("h", FG), node(r"\hat y", FG), node("L", NEG)
        chain = VGroup(nx, nh, ny, nL).arrange(RIGHT, buff=2.0).shift(UP * 0.8)
        fw = VGroup(*[Arrow(chain[k].get_right(), chain[k + 1].get_left(), buff=0.1, color=POS, stroke_width=3)
                      for k in range(3)])
        w1 = MathTex("W_1", font_size=36, color=ACCENT).next_to(fw[0], UP, buff=0.15)
        w2 = MathTex("W_2", font_size=36, color=ACCENT).next_to(fw[1], UP, buff=0.15)
        self.play(FadeIn(chain), Create(fw), FadeIn(w1), FadeIn(w2))
        self.wait(0.5)

        bw = VGroup(*[CurvedArrow(chain[k + 1].get_bottom() + DOWN * 0.1, chain[k].get_bottom() + DOWN * 0.1,
                                  angle=-TAU / 6, color=TAN, stroke_width=3) for k in (2, 1, 0)])
        dlab = [MathTex(r"\delta_{\hat y} = \frac{\partial L}{\partial \hat y}", font_size=30, color=TAN),
                MathTex(r"\delta_h = W_2^{\top}\,\delta_{\hat y}", font_size=30, color=TAN)]
        dlab[0].next_to(bw[0], DOWN, buff=0.1)
        dlab[1].next_to(bw[1], DOWN, buff=0.1)
        c = self.swap(c, cap("뒤에서부터 신호 δ 를 넘겨받는다  =  연쇄법칙", TAN))
        self.play(Create(bw[0]), FadeIn(dlab[0]))
        self.play(Create(bw[1]), FadeIn(dlab[1]))
        self.wait(0.6)

        grads = VGroup(
            MathTex(r"\frac{\partial L}{\partial W_2}", "=", r"\delta_{\hat y}", r"\cdot", r"h^{\top}", font_size=42),
            MathTex(r"\frac{\partial L}{\partial W_1}", "=", r"\delta_h", r"\cdot", r"x^{\top}", font_size=42),
        ).arrange(RIGHT, buff=1.2).to_edge(DOWN, buff=0.6)
        for g in grads:
            g[0].set_color(ACCENT)
            g[2].set_color(TAN)
            g[4].set_color(POS)
        self.play(Write(grads[0]))
        self.play(Write(grads[1]))
        rule = t("모든 층의 공식이 같다:  뒤에서 온 신호 × 앞에서 온 입력", 26, FG).next_to(grads, UP, buff=0.35)
        self.play(FadeIn(rule))
        self.wait(2.0)
        self.clear_except(c)

        # ================= 6) 신호 열 × 입력 행 = 기울기 행렬 =================
        c = self.swap(c, cap("숫자로: 뒤 신호 열 × 앞 입력 행"))
        d_vals, x_vals = [-2, 1], [1, 2, 3]
        dcol = VGroup(*[num_cell(v, color=TAN) for v in d_vals]).arrange(DOWN, buff=0)
        xrow = VGroup(*[num_cell(v, color=POS) for v in x_vals]).arrange(RIGHT, buff=0)
        G = VGroup(*[num_cell(0, color=None) for _ in range(6)]).arrange_in_grid(2, 3, buff=0)
        for cell in G:
            cell[1].set_opacity(0)
        G.move_to(RIGHT * 1.2 + DOWN * 0.6)
        dcol.next_to(G, LEFT, buff=0.5)
        xrow.next_to(G, UP, buff=0.4)
        dl = MathTex(r"\delta", font_size=36, color=TAN).next_to(dcol, LEFT, buff=0.25)
        xl2 = MathTex(r"x^{\top}", font_size=36, color=POS).next_to(xrow, RIGHT, buff=0.25)
        gl = MathTex(r"\frac{\partial L}{\partial W}", font_size=36, color=ACCENT).next_to(G, RIGHT, buff=0.4)
        self.play(FadeIn(dcol), FadeIn(dl), FadeIn(xrow), FadeIn(xl2), Create(G))
        for i in range(2):
            for j in range(3):
                v = d_vals[i] * x_vals[j]
                newc = num_cell(v, color=ACCENT).move_to(G[i * 3 + j])
                self.play(Indicate(dcol[i], color=TAN, scale_factor=1.08),
                          Indicate(xrow[j], color=POS, scale_factor=1.08),
                          Transform(G[i * 3 + j], newc), run_time=0.45)
        self.play(FadeIn(gl))
        note = t("입력 j → 출력 i 선의 기울기 = (끝 쪽 신호 δᵢ) × (시작 쪽 입력 xⱼ)", 26, MUTED).to_edge(DOWN, buff=0.9)
        self.play(FadeIn(note))
        self.wait(1.2)

        dW = MathTex(r"\Delta W", "=", r"-\eta", r"\cdot", r"\delta", r"\cdot", r"x^{\top}", font_size=46).to_edge(DOWN, buff=0.4)
        dW[0].set_color(LORA)
        dW[4].set_color(TAN)
        dW[6].set_color(POS)
        self.play(FadeOut(note), Write(dW))
        self.wait(1.0)

        # ================= 7) LoRA 로 가는 다리 =================
        c = self.swap(c, cap("열 하나 × 행 하나  →  rank 1 행렬", LORA))
        bl = t("B", 34, LORA, weight="BOLD").next_to(dcol, DOWN, buff=0.25)
        al = t("A", 34, LORA, weight="BOLD").next_to(xrow, UP, buff=0.2)
        self.play(dcol.animate.set_stroke(LORA, 3), xrow.animate.set_stroke(LORA, 3), FadeIn(bl), FadeIn(al))
        hint = VGroup(
            t("LoRA의 B × A 와 같은 모양", 30, LORA),
            t("기울기 업데이트는 원래 몇 개 방향에 몰려 있다 → low-rank로 근사할 수 있다", 24, MUTED),
        ).arrange(DOWN, buff=0.15).to_edge(DOWN, buff=0.3)
        self.play(FadeOut(dW), FadeIn(hint, shift=UP * 0.15))
        self.wait(3.0)
