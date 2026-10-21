"""씬 3. 하이퍼파라미터: α(볼륨), α/r, target modules, 실전 기본값.

렌더: ./render.sh s03_hyperparams Hyperparams
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from manim import *

from common.style import ACCENT, FG, FROZEN, LORA, MUTED, NEG, t


def cap(s):
    return t(s, 36).to_edge(UP, buff=0.35)


class Hyperparams(Scene):
    def construct(self):
        caption = cap("α: 패치의 볼륨")

        # ---------- 1) 식 ----------
        formula = MathTex(r"h", "=", "W", "x", "+", r"\frac{\alpha}{r}", "B", "A", "x", font_size=56)
        formula[2].set_color(MUTED)
        formula[5].set_color(ACCENT)
        formula[6:8].set_color(LORA)
        formula.next_to(caption, DOWN, buff=0.4)
        self.play(FadeIn(caption, shift=DOWN * 0.2), Write(formula))
        self.play(Indicate(formula[5], color=ACCENT, scale_factor=1.3))
        self.wait(0.4)

        # ---------- 2) 볼륨 곡선 ----------
        ax = Axes(x_range=[0, 6.3, 1], y_range=[-3, 3, 1], x_length=9, y_length=3.6,
                  axis_config=dict(color=MUTED, stroke_width=1.5, include_ticks=False),
                  tips=False).shift(DOWN * 1.3)
        base = lambda x: 0.9 * np.sin(x) + 0.25 * np.sin(3 * x)
        patch = lambda x: 0.45 * np.sin(2.3 * x + 1) + 0.25 * np.cos(0.8 * x)

        s = ValueTracker(0.0)
        base_curve = ax.plot(base, color=MUTED, stroke_width=3)
        lora_curve = always_redraw(lambda: ax.plot(
            lambda x: np.clip(base(x) + s.get_value() * patch(x), -3, 3),
            color=LORA, stroke_width=4))
        lab_base = t("원본 모델", 22, MUTED).next_to(ax, LEFT, buff=0.2).shift(UP * 0.4)
        lab_lora = t("원본 + 패치", 22, LORA).next_to(lab_base, DOWN, buff=0.15)

        readout = always_redraw(lambda: t(
            f"α/r = {s.get_value():.1f}", 30,
            NEG if s.get_value() > 3 else ACCENT).next_to(ax, UP, buff=0.1).align_to(ax, RIGHT))

        self.play(Create(ax), Create(base_curve), FadeIn(lab_base))
        self.add(lora_curve, readout)
        self.play(FadeIn(lab_lora))
        self.wait(0.3)

        steps = [
            (0.5, "α 작음 → 원본에서 조금만 벗어남", FG),
            (1.0, "α = r → 패치를 그대로 반영", FG),
            (2.0, "α = 2r → 패치를 두 배로", FG),
            (5.0, "너무 크면 → 원본을 망가뜨린다", NEG),
        ]
        note = t("", 26).to_edge(DOWN, buff=0.35)
        self.add(note)
        for val, msg, col in steps:
            self.play(s.animate.set_value(val),
                      Transform(note, t(msg, 26, col).to_edge(DOWN, buff=0.35)),
                      run_time=1.3)
            self.wait(0.7)
        self.play(s.animate.set_value(2.0), run_time=0.8)
        self.wait(0.3)

        # ---------- 3) 왜 r로 나누나 ----------
        self.play(*[FadeOut(m) for m in [ax, base_curve, lora_curve, lab_base, lab_lora, readout, note]])
        self.play(Transform(caption, cap("왜 r로 나눌까?")))

        def row(r, alpha, raw_bar, scaled_bar):
            lab = t(f"r = {r}", 28, LORA)
            raw = Rectangle(width=raw_bar, height=0.32, stroke_width=0).set_fill(MUTED, 0.9)
            sc = Rectangle(width=scaled_bar, height=0.32, stroke_width=0).set_fill(LORA, 1)
            return lab, raw, sc

        head_raw = t("BA 그대로", 24, MUTED)
        head_sc = t("α/r 곱한 뒤", 24, LORA)
        rows = [row(4, 16, 1.4, 2.4), row(8, 16, 2.6, 2.4), row(16, 16, 5.0, 2.4)]
        y0 = 0.6
        x_lab, x_raw, x_sc = -5.6, -4.3, 1.6
        head_raw.move_to([x_raw, y0 + 0.75, 0], aligned_edge=LEFT)
        head_sc.move_to([x_sc, y0 + 0.75, 0], aligned_edge=LEFT)
        grp = VGroup(head_raw, head_sc)
        for k, (lab, raw, sc) in enumerate(rows):
            y = y0 - k * 0.8
            lab.move_to([x_lab, y, 0], aligned_edge=LEFT)
            raw.move_to([x_raw, y, 0], aligned_edge=LEFT)
            sc.move_to([x_sc, y, 0], aligned_edge=LEFT)
            grp.add(lab, raw, sc)
        self.play(FadeIn(head_raw), FadeIn(head_sc))
        for lab, raw, sc in rows:
            self.play(FadeIn(lab), GrowFromEdge(raw, LEFT), run_time=0.6)
        note2 = t("r이 커지면 더하는 항이 늘어나 출력도 커진다", 26, MUTED).to_edge(DOWN, buff=1.1)
        self.play(FadeIn(note2))
        self.wait(0.6)
        self.play(*[GrowFromEdge(sc, LEFT) for _, _, sc in rows], run_time=0.9)
        note3 = t("α/r로 나누면 r을 바꿔도 세기가 비슷 → 학습률 다시 안 찾아도 됨", 26, LORA).to_edge(DOWN, buff=0.45)
        self.play(FadeIn(note3))
        self.wait(2.0)
        self.play(FadeOut(grp), FadeOut(note2), FadeOut(note3), FadeOut(formula))

        # ---------- 4) target modules ----------
        self.play(Transform(caption, cap("어디에 붙일까? target modules")))

        def block(name, w=1.25, h=0.75):
            r = RoundedRectangle(corner_radius=0.1, width=w, height=h, stroke_color=FROZEN, stroke_width=2)
            r.set_fill(FROZEN, 0.35)
            lab = MathTex(name, font_size=34, color=FG).move_to(r)
            return VGroup(r, lab)

        attn = VGroup(*[block(n) for n in [r"W_q", r"W_k", r"W_v", r"W_o"]]).arrange(RIGHT, buff=0.3)
        ffn = VGroup(*[block(n, w=1.6) for n in [r"W_{up}", r"W_{down}"]]).arrange(RIGHT, buff=0.3)
        attn_box = SurroundingRectangle(attn, buff=0.3, corner_radius=0.15, color=MUTED, stroke_width=1.5)
        ffn_box = SurroundingRectangle(ffn, buff=0.3, corner_radius=0.15, color=MUTED, stroke_width=1.5)
        attn_t = t("Attention", 24, MUTED).next_to(attn_box, LEFT, buff=0.25)
        ffn_t = t("FFN", 24, MUTED).next_to(ffn_box, LEFT, buff=0.25)
        layer = VGroup(VGroup(attn_box, attn, attn_t), VGroup(ffn_box, ffn, ffn_t)).arrange(DOWN, buff=0.6)
        layer.move_to(DOWN * 0.3)
        frozen_note = t("Transformer 층 하나 · 전부 고정", 22, MUTED).next_to(layer, DOWN, buff=0.35)
        self.play(FadeIn(layer, shift=UP * 0.2), FadeIn(frozen_note))
        self.wait(0.4)

        def tag(b):
            pill = RoundedRectangle(corner_radius=0.12, width=0.62, height=0.32, stroke_width=0).set_fill(LORA, 1)
            txt = MathTex("BA", font_size=24, color="#0F1115").move_to(pill)
            return VGroup(pill, txt).next_to(b, UP, buff=-0.12).shift(RIGHT * (b.width / 2 - 0.25))

        cnt = t("", 28).to_corner(DR, buff=0.5)
        self.add(cnt)
        stages = [
            ([attn[0], attn[2]], "q, v만: 원 논문 기본값", "2곳"),
            ([attn[1], attn[3]], "q, k, v, o 전부", "4곳"),
            ([ffn[0], ffn[1]], "+ FFN까지: 요즘 흔한 선택", "6곳"),
        ]
        sub = t("", 26).to_edge(DOWN, buff=0.35)
        self.add(sub)
        for blocks, msg, n in stages:
            tags = [tag(b) for b in blocks]
            self.play(
                *[b[0].animate.set_stroke(LORA, 2.5) for b in blocks],
                *[FadeIn(tg, shift=DOWN * 0.15) for tg in tags],
                Transform(sub, t(msg, 26, FG).to_edge(DOWN, buff=0.35)),
                Transform(cnt, t(f"붙인 곳: {n}", 28, LORA).to_corner(DR, buff=0.5)),
                FadeOut(frozen_note),
                run_time=0.9,
            )
            self.wait(0.9)
        self.play(Transform(sub, t("많이 붙일수록 표현력↑  학습량↑", 26, ACCENT).to_edge(DOWN, buff=0.35)))
        self.wait(1.2)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not caption])

        # ---------- 5) 실전 기본값 카드 ----------
        self.play(Transform(caption, cap("처음 시작한다면")))
        items = [
            ("r", "8 ~ 32", "표현력 다이얼"),
            ("α", "r 또는 2r", "패치 볼륨"),
            ("target", "q, v  →  전부", "붙이는 위치"),
            ("learning rate", "1e-4 근처", "→ 다음 장면"),
        ]
        table = VGroup()
        for k, (name, val, desc) in enumerate(items):
            col = ACCENT if k == 3 else LORA
            r = VGroup(
                t(name, 30, col),
                t(val, 30, FG),
                t(desc, 24, MUTED),
            )
            table.add(r)
        xs = [-4.6, -0.6, 3.4]
        for k, r in enumerate(table):
            y = 1.3 - k * 0.95
            for c, x in zip(r, xs):
                c.move_to([x, y, 0], aligned_edge=LEFT)
        lines = VGroup(*[Line([-4.8, 1.3 - k * 0.95 - 0.47, 0], [5.6, 1.3 - k * 0.95 - 0.47, 0],
                              stroke_color="#2A2E38", stroke_width=1) for k in range(3)])
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in table], lag_ratio=0.25), Create(lines), run_time=1.6)
        hook = t("α를 키우면 = 보폭이 커지는 효과", 28, ACCENT).to_edge(DOWN, buff=0.6)
        self.play(FadeIn(hook, shift=UP * 0.15), Indicate(table[3], color=ACCENT, scale_factor=1.05))
        self.wait(2.5)
