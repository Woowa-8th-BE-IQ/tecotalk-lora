"""씬 1-c. 문제 체감: 전부 고치면 얼마나 비싼가 (GPT-3 175B, LoRA 논문 수치).
씬 7-b. 회수: LoRA 논문의 결과.

출처: Hu et al., 2021, "LoRA: Low-Rank Adaptation of Large Language Models", §4.2, §7.2
렌더: ./render.sh s01c_problem ProblemScale
      ./render.sh s01c_problem PaperResult
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from manim import *

from common.style import ACCENT, BG, FG, FROZEN, LORA, MUTED, NEG, POS, t

ERR = "#FF5C5C"
SRC = "출처: Hu et al., 2021, LoRA 논문 (GPT-3 175B 실험)"


def cap(s, color=FG):
    return t(s, 34, color).to_edge(UP, buff=0.3)


def block(label, color, w=2.2, h=0.62, fill=0.85):
    r = RoundedRectangle(corner_radius=0.08, width=w, height=h, stroke_width=0).set_fill(color, fill)
    return VGroup(r, t(label, 22, BG if fill > 0.5 else FG).move_to(r))


class ProblemScale(Scene):
    def construct(self):
        # ---------- 1) 가중치 하나를 고치려면 ----------
        c = cap("가중치 하나를 고치려면, 같이 들고 있어야 하는 것들")
        self.play(FadeIn(c))
        stack = VGroup(
            block("가중치", POS),
            block("기울기", ERR),
            block("Adam 기록 1", ACCENT),
            block("Adam 기록 2", ACCENT),
        ).arrange(UP, buff=0.08).move_to(LEFT * 3.2 + DOWN * 0.2)
        notes = VGroup(
            t("고칠 대상", 22, MUTED), t("어느 쪽으로 얼마나", 22, MUTED),
            t("최근 기울기 평균", 22, MUTED), t("최근 기울기 크기", 22, MUTED),
        )
        for n, b in zip(notes, stack):
            n.next_to(b, RIGHT, buff=0.3)
        for b, n in zip(stack, notes):
            self.play(FadeIn(b, shift=UP * 0.15), FadeIn(n), run_time=0.5)
        mult = t("가중치 1개 ≈ 짐 4개 (+ 계산 중간값)", 28, ACCENT).to_edge(DOWN, buff=1.0)
        self.play(FadeIn(mult))
        self.wait(1.2)
        self.play(*[FadeOut(m) for m in [stack, notes, mult]])

        # ---------- 2) GPT-3 175B ----------
        c2 = cap("GPT-3 175B 를 통째로 파인튜닝하면")
        self.play(FadeOut(c), FadeIn(c2))
        c = c2
        unit = 4.5 / 1.2   # 1.2TB = 4.5 화면 단위
        rows = [
            ("학습 중 GPU 메모리", 1.2, "1.2 TB", ERR),
            ("과제 하나당 저장할 모델", 0.35, "350 GB", ACCENT),
        ]
        g = VGroup()
        for k, (name, v, txt, col) in enumerate(rows):
            y = 1.0 - k * 1.5
            nm = t(name, 26, FG).move_to([-4.0, y, 0], aligned_edge=LEFT).shift(LEFT * 1.6)
            bar = Rectangle(width=v * unit, height=0.55, stroke_width=0).set_fill(col, 0.85)
            bar.move_to([-1.2, y, 0], aligned_edge=LEFT)
            val = t(txt, 30, col).next_to(bar, RIGHT, buff=0.2)
            g.add(VGroup(nm, bar, val))
        for r in g:
            self.play(FadeIn(r[0]), GrowFromEdge(r[1], LEFT), FadeIn(r[2]), run_time=0.9)
        gpu = t("GPU 80GB 짜리로 15장 이상", 24, MUTED).next_to(g[0][1], DOWN, buff=0.12).align_to(g[0][1], LEFT)
        self.play(FadeIn(gpu))
        self.wait(0.8)

        many = t("캐릭터·말투·도메인마다 하나씩?  과제 100개면 350GB × 100 = 35TB", 26, ERR).to_edge(DOWN, buff=1.0)
        self.play(FadeIn(many))
        src = t(SRC, 18, MUTED).to_corner(DR, buff=0.25)
        self.play(FadeIn(src))
        self.wait(1.6)

        q = t("전부 고치지 말고, 고칠 부분만 작게 만들 수 없을까?", 32, LORA).to_edge(DOWN, buff=0.75)
        self.play(FadeOut(many), FadeIn(q, shift=UP * 0.1))
        self.wait(2.2)


class PaperResult(Scene):
    def construct(self):
        c = cap("LoRA 논문의 결과  (GPT-3 175B)")
        self.play(FadeIn(c))

        # ---------- 1) 메모리 ----------
        unit = 4.5 / 1.2
        rows = [("풀 파인튜닝", 1.2, "1.2 TB", ERR), ("LoRA", 0.35, "350 GB", LORA)]
        g = VGroup()
        for k, (name, v, txt, col) in enumerate(rows):
            y = 1.6 - k * 0.9
            nm = t(name, 26, col).move_to([-5.6, y, 0], aligned_edge=LEFT)
            bar = Rectangle(width=v * unit, height=0.5, stroke_width=0).set_fill(col, 0.85).move_to([-3.0, y, 0], aligned_edge=LEFT)
            val = t(txt, 26, col).next_to(bar, RIGHT, buff=0.2)
            g.add(VGroup(nm, bar, val))
        head1 = t("학습 중 GPU 메모리", 22, MUTED).next_to(g, UP, buff=0.25).align_to(g, LEFT)
        self.play(FadeIn(head1), *[FadeIn(r[0]) for r in g], *[GrowFromEdge(r[1], LEFT) for r in g], *[FadeIn(r[2]) for r in g])
        x3 = t("약 3배 감소", 28, LORA).next_to(g[1][2], RIGHT, buff=0.5)
        self.play(FadeIn(x3))
        self.wait(0.8)

        # ---------- 2) 저장 크기 ----------
        big = Square(2.4, stroke_width=0).set_fill(ERR, 0.8).move_to([-3.2, -1.9, 0])
        tiny = Square(0.024, stroke_width=0).set_fill(LORA, 1).move_to([1.2, -1.9, 0])
        ring = Circle(0.25, color=LORA, stroke_width=3).move_to(tiny)
        bl = t("350 GB", 26, ERR).next_to(big, RIGHT, buff=0.2).align_to(big, DOWN)
        tl = t("35 MB", 26, LORA).next_to(ring, RIGHT, buff=0.2)
        head2 = t("과제 하나당 저장 크기  (넓이 비율)", 22, MUTED).move_to([-1.0, -0.45, 0])
        self.play(FadeIn(head2), FadeIn(big), FadeIn(bl))
        self.play(FadeIn(tiny), Create(ring), FadeIn(tl))
        x1 = t("약 1만 배 감소", 28, LORA).next_to(tl, RIGHT, buff=0.5)
        cond = t("r = 4, Wq·Wv 에만 적용", 20, MUTED).next_to(x1, DOWN, buff=0.12).align_to(x1, LEFT)
        self.play(FadeIn(x1), FadeIn(cond))
        self.wait(1.4)

        # ---------- 3) 요약 ----------
        self.play(*[FadeOut(m) for m in self.mobjects if m is not c])
        items = VGroup(
            t("학습할 숫자  약 1만 배 감소", 30, LORA),
            t("학습 중 메모리  약 3배 감소", 30, LORA),
            t("학습 속도  약 25% 빨라짐", 30, LORA),
            t("추론 속도  손해 없음  (W + BA 로 합칠 수 있어서)", 30, FG),
            t("r = 1 로도 충분했던 경우가 있었다  (Wq, Wv 둘 다 적용 시)", 26, MUTED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.35).shift(DOWN * 0.1)
        for it in items:
            self.play(FadeIn(it, shift=RIGHT * 0.15), run_time=0.55)
        src = t(SRC, 18, MUTED).to_corner(DR, buff=0.25)
        self.play(FadeIn(src))
        self.wait(2.5)
