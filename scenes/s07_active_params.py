"""씬 7. 활성 파라미터(MoE) vs LoRA: 학습 때 줄이기 vs 추론 때 줄이기.

렌더: ./render.sh s07_active_params ActiveParams
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from manim import *

from common.style import ACCENT, FG, FROZEN, LORA, MUTED, POS, t

N_EXPERTS = 8
TOP_K = 2


def cap(s):
    return t(s, 36).to_edge(UP, buff=0.35)


class ActiveParams(Scene):
    def construct(self):
        caption = cap("헷갈리는 개념: 활성 파라미터")
        self.play(FadeIn(caption, shift=DOWN * 0.2))

        # ---------- 1) MoE 구조 ----------
        experts = VGroup(*[
            VGroup(
                RoundedRectangle(corner_radius=0.12, width=1.15, height=0.8, stroke_color=FROZEN, stroke_width=2)
                .set_fill(FROZEN, 0.35),
                t(f"E{i + 1}", 24, MUTED),
            )
            for i in range(N_EXPERTS)
        ]).arrange(RIGHT, buff=0.28).shift(DOWN * 0.4)
        for e in experts:
            e[1].move_to(e[0])

        router = VGroup(
            RoundedRectangle(corner_radius=0.15, width=2.2, height=0.75, stroke_color=ACCENT, stroke_width=2.5)
            .set_fill(ACCENT, 0.12),
            t("라우터", 26, ACCENT),
        ).move_to(UP * 1.6)
        router[1].move_to(router[0])
        exp_lab = t("전문가(Expert) 8개 · 전부 메모리에 올라가 있음", 22, MUTED).next_to(experts, DOWN, buff=0.3)

        self.play(FadeIn(router), LaggedStart(*[FadeIn(e, shift=UP * 0.1) for e in experts], lag_ratio=0.06))
        self.play(FadeIn(exp_lab))
        wires = VGroup(*[Line(router.get_bottom(), e.get_top(), color="#2A2E38", stroke_width=1.5) for e in experts])
        self.play(Create(wires), run_time=0.6)

        counter = VGroup(
            t("총 약 47B", 26, MUTED),
            t("토큰당 계산 약 13B", 26, LORA),
        ).arrange(DOWN, aligned_edge=RIGHT, buff=0.1).to_corner(DR, buff=0.4)
        mix = t("예: Mixtral 8x7B", 20, MUTED).next_to(counter, UP, aligned_edge=RIGHT, buff=0.12)

        self.play(Transform(caption, cap("토큰마다 라우터가 2개만 고른다 (top-2)")))
        rng = np.random.default_rng(4)
        tokens = ["캐릭", "터가", "웃는다"]
        for k, word in enumerate(tokens):
            tok = VGroup(
                RoundedRectangle(corner_radius=0.12, width=1.4, height=0.6, stroke_width=0).set_fill(POS, 0.9),
                t(word, 24, "#0F1115", weight="BOLD"),
            ).move_to(UP * 2.75)
            tok[1].move_to(tok[0])
            picks = rng.choice(N_EXPERTS, TOP_K, replace=False)
            self.play(FadeIn(tok, shift=DOWN * 0.2), run_time=0.4)
            self.play(tok.animate.move_to(router).scale(0.7).set_opacity(0.3), run_time=0.4)
            hot = [wires[i].copy().set_stroke(LORA, 4) for i in picks]
            self.play(
                *[Create(h) for h in hot],
                *[experts[i][0].animate.set_stroke(LORA, 3).set_fill(LORA, 0.35) for i in picks],
                *[experts[i][1].animate.set_color(FG) for i in picks],
                run_time=0.6,
            )
            if k == 0:
                self.play(FadeIn(mix), FadeIn(counter))
            self.wait(0.45)
            self.play(
                *[FadeOut(h) for h in hot], FadeOut(tok),
                *[experts[i][0].animate.set_stroke(FROZEN, 2).set_fill(FROZEN, 0.35) for i in picks],
                *[experts[i][1].animate.set_color(MUTED) for i in picks],
                run_time=0.4,
            )
        note = t("나머지 6개는 이 토큰에선 계산 안 함", 24, FG).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(note))
        self.wait(1.0)

        # 백엔드 비유
        self.play(Transform(caption, cap("백엔드로 보면: 요청마다 라우팅되는 서비스")),
                  Transform(note, t("서버는 다 떠 있지만, 요청 하나는 두 곳만 거친다", 24, FG).to_edge(DOWN, buff=0.35)))
        self.wait(1.6)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not caption])

        # ---------- 2) LoRA vs MoE 표 ----------
        self.play(Transform(caption, cap("둘 다 '전부 안 써도 된다', 그런데")))
        head = [t("", 26), t("LoRA", 30, LORA, weight="BOLD"), t("활성 파라미터 (MoE)", 30, ACCENT, weight="BOLD")]
        rows = [
            ("줄이는 것", "학습할 숫자", "계산할 숫자"),
            ("언제", "파인튜닝 때", "매 토큰 추론 때"),
            ("질문", "뭘 고칠까?", "뭘 돌릴까?"),
        ]
        xs = [-4.6, -1.0, 3.2]
        grid = VGroup()
        for c, x in zip(head, xs):
            c.move_to([x, 1.5, 0])
            grid.add(c)
        for k, (a, b, c) in enumerate(rows):
            y = 0.5 - k * 0.95
            cells = [t(a, 26, MUTED), t(b, 28, FG), t(c, 28, FG)]
            for cell, x in zip(cells, xs):
                cell.move_to([x, y, 0])
                grid.add(cell)
        lines = VGroup(*[Line([-6, 1.0 - k * 0.95, 0], [6, 1.0 - k * 0.95, 0], stroke_color="#2A2E38", stroke_width=1)
                         for k in range(3)])
        self.play(FadeIn(grid[:3]), Create(lines))
        for k in range(3):
            self.play(FadeIn(grid[3 + 3 * k: 6 + 3 * k], shift=RIGHT * 0.15), run_time=0.6)
        punch = t("하나는 학습, 하나는 추론", 34, ACCENT, weight="BOLD").to_edge(DOWN, buff=0.6)
        self.play(FadeIn(punch, scale=1.15))
        self.wait(2.5)
