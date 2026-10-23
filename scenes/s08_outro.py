"""씬 8. 마무리: 넓게 배우고 좁게 고치기 + 요약.

렌더: ./render.sh s08_outro Outro
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from manim import *

from common.style import ACCENT, BG, FG, LORA, MUTED, NEG, POS, t


def cap(s):
    return t(s, 36).to_edge(UP, buff=0.35)


def heat(M, cell=0.17):
    vmax = np.abs(M).max() + 1e-9
    rows, cols = M.shape
    g = VGroup()
    for i in range(rows):
        for j in range(cols):
            v = M[i, j]
            c = interpolate_color(ManimColor(BG), ManimColor(POS if v >= 0 else NEG), 0.15 + 0.85 * min(1, abs(v) / vmax))
            g.add(Square(cell, stroke_width=0.5, stroke_color="#22262F").set_fill(c, 1)
                  .move_to([(j - (cols - 1) / 2) * cell, -(i - (rows - 1) / 2) * cell, 0]))
    return g


class Outro(Scene):
    def construct(self):
        rng = np.random.default_rng(9)
        caption = cap("두 방향의 '랭크'")
        self.play(FadeIn(caption, shift=DOWN * 0.2))

        # ---------- 1) high-rank vs low-rank ----------
        N = 14
        full = heat(rng.normal(0, 1, (N, N))).move_to(LEFT * 3.3 + DOWN * 0.2)
        Bm, Am = rng.normal(0, 1, (N, 1)), rng.normal(0, 1, (1, N))
        low = heat(Bm @ Am).move_to(RIGHT * 3.3 + DOWN * 0.2)
        lt = VGroup(t("사전학습", 28, POS), t("모든 방향을 넓게 (high-rank)", 22, MUTED)).arrange(DOWN, buff=0.08)
        rt = VGroup(t("파인튜닝 · LoRA", 28, LORA), t("필요한 방향만 좁게 (low-rank)", 22, MUTED)).arrange(DOWN, buff=0.08)
        lt.next_to(full, DOWN, buff=0.3)
        rt.next_to(low, DOWN, buff=0.3)
        self.play(LaggedStart(*[FadeIn(c) for c in full], lag_ratio=0.002), FadeIn(lt), run_time=1.2)
        self.play(LaggedStart(*[FadeIn(c) for c in low], lag_ratio=0.002), FadeIn(rt), run_time=1.2)
        self.wait(0.4)
        punch = t("넓게 배우고, 좁게 고친다", 40, ACCENT, weight="BOLD").to_edge(DOWN, buff=0.45)
        self.play(FadeIn(punch, scale=1.15))
        self.wait(1.8)
        self.play(*[FadeOut(m) for m in [full, low, lt, rt, punch]])

        # ---------- 2) 요약 ----------
        self.play(Transform(caption, cap("오늘 본 것")))
        items = [
            ("무엇을", "LoRA: 원본은 얼리고 B·A만 학습", LORA),
            ("얼마나", "r = 표현력, α = 볼륨", LORA),
            ("어떻게", "학습률 = 보폭, AdamW = 방향별 보폭", ACCENT),
            ("구분", "활성 파라미터 = 추론,  LoRA = 학습", POS),
        ]
        rows = VGroup()
        for k, (q, a, col) in enumerate(items):
            num = VGroup(Circle(0.26, color=col, stroke_width=2.5), t(str(k + 1), 24, col))
            num[1].move_to(num[0])
            row = VGroup(num, t(q, 28, col, weight="BOLD"), t(a, 28, FG)).arrange(RIGHT, buff=0.35)
            rows.add(row)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.45).move_to(DOWN * 0.2)
        for r in rows:
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.6)
        self.wait(1.8)
        self.play(FadeOut(rows), FadeOut(caption))

        # ---------- 3) 엔딩 ----------
        line1 = t("main 브랜치는 그대로,", 40, MUTED)
        line2 = t("패치만 갈아끼운다", 46, LORA, weight="BOLD")
        end = VGroup(line1, line2).arrange(DOWN, buff=0.3).shift(UP * 0.6)
        self.play(FadeIn(line1, shift=UP * 0.15))
        self.play(FadeIn(line2, shift=UP * 0.15))
        self.wait(1.2)
        title = t("LoRA로 보는 파인튜닝과 학습의 원리", 28, FG).next_to(end, DOWN, buff=1.0)
        thanks = t("감사합니다", 34, ACCENT).next_to(title, DOWN, buff=0.35)
        self.play(FadeIn(title), FadeIn(thanks))
        self.wait(3.0)
