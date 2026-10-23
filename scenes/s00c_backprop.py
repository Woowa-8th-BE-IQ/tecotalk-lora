"""씬 0-c. 역전파 (연쇄법칙 없이), LLM 다음 단어 버전.

정답 '김밥' 확률이 낮다 → 손실 → 차이를 뒤로 → 선마다 책임 몫(기울기) → 책임만큼 반대로 고친다 → 반복.
작은 신경망을 실제로 계산한다 (softmax + 크로스 엔트로피, 손실/기울기 모두 진짜 값).
렌더: ./render.sh s00c_backprop Backprop
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from manim import *

from common.style import ACCENT, BG, FG, LORA, MUTED, NEG, POS, t, weight_color, weight_width

LAYERS = [4, 6, 6, 4]
XS = [-5.4, -2.6, 0.2, 2.6]
Y_GAP = 0.66
Y_CENTER = 0.15
NODE_R = 0.17
LR = 0.3
SEED = 15
X_IN = np.array([0.9, -0.4, 0.6, 0.2])
TOKENS = ["김밥", "라면", "피자", "국밥"]
TGT = 0
ERR = "#FF5C5C"


def run(W):
    h1 = np.tanh(W[0] @ X_IN)
    h2 = np.tanh(W[1] @ h1)
    z = W[2] @ h2
    p = np.exp(z - z.max())
    p /= p.sum()
    loss = float(-np.log(p[TGT]))
    e = p.copy()
    e[TGT] -= 1
    g3 = np.outer(e, h2)
    d2 = (W[2].T @ e) * (1 - h2 ** 2)
    g2 = np.outer(d2, h1)
    d1 = (W[1].T @ d2) * (1 - h1 ** 2)
    g1 = np.outer(d1, X_IN)
    return p, loss, [g1, g2, g3]


def cap(s, color=FG):
    return t(s, 34, color).to_edge(UP, buff=0.3)


class Backprop(Scene):
    def construct(self):
        rng = np.random.default_rng(SEED)
        W = [rng.normal(0, 0.7, (LAYERS[k + 1], LAYERS[k])) for k in range(3)]

        layers = []
        for n, x in zip(LAYERS, XS):
            ys = [Y_CENTER + (i - (n - 1) / 2) * Y_GAP for i in range(n)][::-1]
            layers.append(VGroup(*[Circle(NODE_R, color=FG, stroke_width=2).set_fill(BG, 1).move_to([x, y, 0]) for y in ys]))

        edges = [[[Line(layers[k][j].get_center(), layers[k + 1][i].get_center(), buff=NODE_R)
                   for j in range(LAYERS[k])] for i in range(LAYERS[k + 1])] for k in range(3)]
        flat = VGroup(*[e for ek in edges for row in ek for e in row])

        def w_style(w):
            return dict(color=weight_color(w), width=weight_width(w) * 0.8, opacity=0.3 + 0.6 * min(abs(w), 1))

        for k in range(3):
            for i in range(LAYERS[k + 1]):
                for j in range(LAYERS[k]):
                    edges[k][i][j].set_stroke(**w_style(W[k][i, j]))

        def restyle(Wc):
            return [edges[k][i][j].animate.set_stroke(**w_style(Wc[k][i, j]))
                    for k in range(3) for i in range(LAYERS[k + 1]) for j in range(LAYERS[k])]

        out = layers[3]
        inp_lab = t("입력: 나는 오늘 점심에", 22, MUTED).next_to(layers[0], UP, buff=0.3)
        tok_labs = VGroup(*[t(tok, 24, LORA if i == TGT else FG).next_to(out[i], RIGHT, buff=0.25)
                            for i, tok in enumerate(TOKENS)])
        BAR_X = out[0].get_x() + 1.35
        BAR_W = 2.4

        def prob_bars(p):
            g = VGroup()
            for i, pi in enumerate(p):
                y = out[i].get_y()
                col = LORA if i == TGT else MUTED
                b = Rectangle(width=max(pi * BAR_W, 0.03), height=0.28, stroke_width=0).set_fill(col, 0.9 if i == TGT else 0.5)
                b.move_to([BAR_X, y, 0], aligned_edge=LEFT)
                lab = t(f"{pi * 100:.0f}%", 20, FG).next_to(b, RIGHT, buff=0.1)
                g.add(VGroup(b, lab))
            return g

        loss_box = VGroup(t("손실  −log p(김밥)", 20, MUTED), t("0.00", 34, ERR).set_opacity(0)).arrange(DOWN, buff=0.18)
        loss_box.to_corner(UR, buff=0.35).shift(DOWN * 0.75)

        def loss_val(v):
            return t(f"{v:.2f}", 34, ERR).move_to(loss_box[1])

        def fwd_flash():
            for k in range(3):
                self.play(*[ShowPassingFlash(e.copy().set_stroke(POS, 3, 1), time_width=0.6) for row in edges[k] for e in row],
                          run_time=0.4)

        def back_flash():
            for k in (2, 1, 0):
                self.play(*[ShowPassingFlash(Line(e.get_end(), e.get_start()).set_stroke(ERR, 3.5, 1), time_width=0.6)
                            for row in edges[k] for e in row], run_time=0.5)

        # ---------- 1) 앞으로 계산 ----------
        c = cap("앞으로 계산  →  다음 단어 확률")
        self.play(FadeIn(c))
        self.play(LaggedStart(*[FadeIn(L, scale=0.6) for L in layers], lag_ratio=0.15),
                  Create(flat, lag_ratio=0.003), FadeIn(inp_lab), FadeIn(tok_labs), run_time=1.5)
        self.add_foreground_mobjects(*layers)
        p, loss, G = run(W)
        fwd_flash()
        bars = prob_bars(p)
        self.play(LaggedStart(*[GrowFromEdge(b[0], LEFT) for b in bars], lag_ratio=0.1), *[FadeIn(b[1]) for b in bars])
        self.wait(0.5)

        # ---------- 2) 손실 ----------
        c2 = cap("정답은 김밥인데 5%  →  손실이 크다", ERR)
        mark = SurroundingRectangle(VGroup(tok_labs[TGT], bars[TGT]), color=LORA, buff=0.1)
        self.play(FadeOut(c), FadeIn(c2), Create(mark), FadeIn(loss_box))
        c = c2
        self.play(Transform(loss_box[1], loss_val(loss)))
        self.wait(0.8)

        # ---------- 3) 뒤로 ----------
        c2 = cap("이 차이를 뒤로 보낸다", ERR)
        self.play(FadeOut(c), FadeIn(c2))
        c = c2
        back_flash()

        # ---------- 4) 책임 몫 ----------
        gmax = max(np.abs(g).max() for g in G)
        c2 = cap("선마다 책임 몫  =  기울기", ERR)
        blame = [edges[k][i][j].animate.set_stroke(ERR, 0.4 + 5.0 * abs(G[k][i, j]) / gmax,
                                                    0.12 + 0.88 * abs(G[k][i, j]) / gmax)
                 for k in range(3) for i in range(LAYERS[k + 1]) for j in range(LAYERS[k])]
        self.play(FadeOut(c), FadeIn(c2), *blame, run_time=1.2)
        c = c2
        note = t("굵은 선 = 건드리면 손실이 크게 변하는 가중치", 24, MUTED).to_edge(DOWN, buff=0.4)
        self.play(FadeIn(note))
        self.wait(1.6)

        # ---------- 5) 고친다 ----------
        c2 = cap("책임만큼, 반대 방향으로 조금 고친다", LORA)
        W = [w - LR * g for w, g in zip(W, G)]
        p, loss, G = run(W)
        self.play(FadeOut(c), FadeIn(c2), FadeOut(note), *restyle(W), run_time=1.2)
        c = c2
        fwd_flash()
        self.play(Transform(bars, prob_bars(p)), Transform(loss_box[1], loss_val(loss)),
                  mark.animate.become(SurroundingRectangle(VGroup(tok_labs[TGT], prob_bars(p)[TGT]), color=LORA, buff=0.1)))
        self.wait(0.8)

        # ---------- 6) 반복 ----------
        c2 = cap("반복할수록 김밥 확률↑  손실↓", LORA)
        self.play(FadeOut(c), FadeIn(c2))
        c = c2
        it_lab = t("반복 1", 22, MUTED).next_to(loss_box, DOWN, buff=0.25)
        self.play(FadeIn(it_lab))
        for it in (2, 3):
            back_flash()
            W = [w - LR * g for w, g in zip(W, G)]
            p, loss, G = run(W)
            self.play(*restyle(W), run_time=0.6)
            fwd_flash()
            nb = prob_bars(p)
            self.play(Transform(bars, nb), Transform(loss_box[1], loss_val(loss)),
                      mark.animate.become(SurroundingRectangle(VGroup(tok_labs[TGT], nb[TGT]), color=LORA, buff=0.1)),
                      Transform(it_lab, t(f"반복 {it}", 22, MUTED).move_to(it_lab)), run_time=0.7)
        self.wait(0.8)

        # ---------- 7) 마무리 ----------
        end = VGroup(
            t("차이를 뒤로 보내 책임을 나누고, 책임만큼 고친다  =  역전파 + 경사하강", 26, FG),
            t("그런데 이 선이 70억 개라면?", 32, ACCENT),
        ).arrange(DOWN, buff=0.22).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(end[0], shift=UP * 0.1))
        self.wait(1.2)
        self.play(FadeIn(end[1], shift=UP * 0.1))
        self.wait(2.0)
