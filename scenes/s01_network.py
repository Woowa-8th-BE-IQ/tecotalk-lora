"""씬 1. 신경망 = 가중치로 이어진 선 → 풀 파인튜닝 vs LoRA 우회로.

렌더: ./render.sh s01_network NetworkToLoRA
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from manim import *

from common.style import (
    ACCENT, FG, FROZEN, LORA, MUTED, t, weight_color, weight_width,
)

LAYERS = [4, 6, 6, 3]
XS = [-4.5, -1.5, 1.5, 4.5]
Y_GAP = 0.7
Y_CENTER = 0.75
NODE_R = 0.16
TARGET = 1          # LoRA를 붙일 연결: 층1 → 층2 (6×6)
RANK = 2


def edge_style(w):
    return dict(color=weight_color(w), width=weight_width(w), opacity=0.35 + 0.65 * min(abs(w), 1))


class NetworkToLoRA(Scene):
    def construct(self):
        rng = np.random.default_rng(3)

        # ---------- 노드 ----------
        layers = []
        for n, x in zip(LAYERS, XS):
            ys = [Y_CENTER + (i - (n - 1) / 2) * Y_GAP for i in range(n)][::-1]
            col = VGroup(*[
                Circle(NODE_R, color=FG, stroke_width=2).set_fill(BLACK, 1).move_to([x, y, 0])
                for y in ys
            ])
            layers.append(col)

        # ---------- 엣지 ----------
        edges, weights = [], []          # edges[k] = 층k→k+1의 (i,j) 엣지 리스트
        for k in range(len(LAYERS) - 1):
            ek, wk = [], []
            for a in layers[k]:
                for b in layers[k + 1]:
                    w = rng.normal(0, 0.55)
                    s = edge_style(w)
                    ln = Line(a.get_center(), b.get_center(), buff=NODE_R)
                    ln.set_stroke(s["color"], s["width"], s["opacity"])
                    ek.append(ln)
                    wk.append(w)
            edges.append(ek)
            weights.append(wk)
        all_edges = VGroup(*[e for ek in edges for e in ek])
        n_params = len(all_edges)

        caption = t("신경망 = 숫자로 이어진 선", 36).to_edge(UP, buff=0.35)

        # 1) 등장
        self.play(FadeIn(caption, shift=DOWN * 0.2))
        self.play(LaggedStart(*[FadeIn(c, scale=0.6) for c in layers], lag_ratio=0.2), run_time=1.0)
        self.play(LaggedStart(*[Create(e) for e in all_edges], lag_ratio=0.004), run_time=1.6)
        self.add_foreground_mobjects(*layers)
        self.wait(0.5)

        # 2) 선 하나 = 숫자 하나
        k_pick = int(np.argmax(np.abs(weights[1])))
        pick = edges[1][k_pick]
        w_val = weights[1][k_pick]
        tag = t(f"w = {w_val:+.2f}", 28, ACCENT).next_to(pick.get_center(), UP, buff=0.35)
        self.play(
            all_edges.animate.set_stroke(opacity=0.12),
            pick.animate.set_stroke(ACCENT, 5, 1),
            FadeIn(tag, shift=UP * 0.1),
            Transform(caption, t("선 하나 = 숫자 하나 (가중치)", 36).to_edge(UP, buff=0.35)),
        )
        self.wait(1.2)
        self.play(
            FadeOut(tag),
            *[e.animate.set_stroke(**edge_style(w)) for ek, wk in zip(edges, weights) for e, w in zip(ek, wk)],
        )

        # 3) 순전파
        self.play(Transform(caption, t("입력이 흐르며 곱해지고 더해진다", 36).to_edge(UP, buff=0.35)))
        for ek in edges:
            self.play(*[ShowPassingFlash(e.copy().set_stroke(ACCENT, 3, 1), time_width=0.6) for e in ek], run_time=0.7)
        self.wait(0.3)

        # 4) 풀 파인튜닝
        counter = t(f"학습: {n_params}개 전부", 30, ACCENT).to_corner(DR, buff=0.5)
        self.play(
            Transform(caption, t("풀 파인튜닝: 모든 선을 다시 학습", 36).to_edge(UP, buff=0.35)),
            FadeIn(counter),
        )
        original = [list(wk) for wk in weights]
        for _ in range(3):
            anims = []
            for ek, wk in zip(edges, weights):
                for i, e in enumerate(ek):
                    wk[i] += rng.normal(0, 0.45)
                    anims.append(e.animate.set_stroke(**edge_style(wk[i])))
            self.play(*anims, run_time=0.8)
        self.wait(0.6)

        # 5) LoRA: 얼리기
        frozen_label = t("W  고정", 26, MUTED).next_to(
            VGroup(layers[1], layers[2]), UP, buff=0.15)
        self.play(
            Transform(caption, t("LoRA: 원본은 그대로 얼리고", 36).to_edge(UP, buff=0.35)),
            FadeOut(counter),
            *[e.animate.set_stroke(FROZEN, 1.4, 1) for e in all_edges],
            run_time=1.2,
        )
        self.play(FadeIn(frozen_label))
        self.wait(0.5)

        # 6) 우회로 붙이기
        mid_x = (XS[TARGET] + XS[TARGET + 1]) / 2
        low_y = layers[TARGET].get_bottom()[1] - 1.1
        bott = VGroup(*[
            Circle(NODE_R * 0.9, color=LORA, stroke_width=2.5).set_fill(BLACK, 1)
            .move_to([mid_x + (i - (RANK - 1) / 2) * 0.55, low_y, 0])
            for i in range(RANK)
        ])
        rng2 = np.random.default_rng(11)
        a_edges = [Line(s.get_center(), b.get_center(), buff=NODE_R) for s in layers[TARGET] for b in bott]
        b_edges = [Line(b.get_center(), d.get_center(), buff=NODE_R) for b in bott for d in layers[TARGET + 1]]
        for e in a_edges + b_edges:
            e.set_stroke(LORA, 1.6, 0.85)
        A = VGroup(*a_edges)
        B = VGroup(*b_edges)

        lab_A = t("A", 30, LORA, weight="BOLD").move_to([mid_x - 1.25, low_y - 0.1, 0])
        lab_B = t("B", 30, LORA, weight="BOLD").move_to([mid_x + 1.25, low_y - 0.1, 0])
        lab_r = t(f"r = {RANK}", 24, LORA).next_to(bott, DOWN, buff=0.2)

        self.play(Transform(caption, t("옆에 작은 우회로를 붙인다", 36).to_edge(UP, buff=0.35)))
        self.play(FadeIn(bott, scale=0.5))
        self.add_foreground_mobjects(bott)
        self.play(Create(A), Create(B), run_time=1.2)
        self.play(FadeIn(lab_A), FadeIn(lab_B), FadeIn(lab_r))
        self.wait(0.6)

        # 7) 우회로만 학습
        n_lora = len(a_edges) + len(b_edges)
        counter2 = VGroup(
            t(f"학습: {n_lora}개", 30, LORA),
            t(f"원본 {n_params}개 고정", 24, MUTED),
        ).arrange(DOWN, aligned_edge=RIGHT, buff=0.12).to_corner(DR, buff=0.5)
        self.play(
            Transform(caption, t("우회로만 학습한다", 36).to_edge(UP, buff=0.35)),
            FadeIn(counter2),
        )
        for _ in range(3):
            anims = [e.animate.set_stroke(LORA, 0.8 + 3.2 * rng2.random(), 0.35 + 0.65 * rng2.random())
                     for e in a_edges + b_edges]
            self.play(*anims, run_time=0.8)
        self.wait(0.6)

        # 8) 식
        formula = MathTex(r"h", r"=", r"W", r"x", r"+", r"B", r"A", r"x", font_size=54)
        formula[2].set_color(MUTED)
        formula[5:7].set_color(LORA)
        formula.to_edge(UP, buff=0.3)
        cap_w = t("원본", 20, MUTED).next_to(formula[2], DOWN, buff=0.1)
        cap_p = t("패치", 20, LORA).next_to(formula[5:7], DOWN, buff=0.1)
        self.play(FadeOut(caption, shift=UP * 0.2), FadeOut(frozen_label), Write(formula))
        self.play(FadeIn(cap_w), FadeIn(cap_p))
        self.wait(2.5)
