"""씬 2-c. 작은 행렬 두 개로 큰 행렬을 어떻게 표현하나.

구구단표(rank 1) → 패턴 겹치기(rank 2) → B×A = 패턴 r개 → 실제 ΔW는 패턴 몇 개에 몰려 있다
→ B=0 에서 시작해 B, A만 경사하강으로 학습 → 숫자 비교, W+BA 로 합치기.
렌더: ./render.sh s02c_lora_matrix LoRAMatrix
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from manim import *

from common.style import ACCENT, BG, FG, LORA, MUTED, NEG, POS, t

N = 12
CELL = 0.22


def cap(s, color=FG):
    return t(s, 34, color).to_edge(UP, buff=0.3)


def ccol(v, vmax):
    a = min(1.0, abs(v) / vmax)
    return interpolate_color(ManimColor(BG), ManimColor(POS if v >= 0 else NEG), 0.12 + 0.88 * a)


def heat(M, vmax, cell=CELL):
    M = np.atleast_2d(M)
    rows, cols = M.shape
    g = VGroup()
    for i in range(rows):
        for j in range(cols):
            g.add(Square(cell, stroke_width=0.5, stroke_color="#22262F").set_fill(ccol(M[i, j], vmax), 1)
                  .move_to([(j - (cols - 1) / 2) * cell, -(i - (rows - 1) / 2) * cell, 0]))
    g.shape = (rows, cols)
    return g


def recolor(g, M, vmax):
    M = np.atleast_2d(M)
    rows, cols = M.shape
    return [g[i * cols + j].animate.set_fill(ccol(M[i, j], vmax), 1) for i in range(rows) for j in range(cols)]


def num_cell(v, size=0.62, color=None, fs=24, txt_color=FG):
    sq = Square(size, stroke_color="#3A3F4B", stroke_width=1.5)
    if color is not None:
        sq.set_fill(color, 0.25)
    return VGroup(sq, t(f"{v:g}", fs, txt_color).move_to(sq))


class LoRAMatrix(Scene):
    def swap(self, old, new):
        self.play(FadeOut(old), FadeIn(new), run_time=0.5)
        return new

    def clear(self, keep):
        self.play(*[FadeOut(m) for m in self.mobjects if m is not keep], run_time=0.6)

    def construct(self):
        # ================= 0) 질문 =================
        c = cap("작은 행렬 두 개로, 큰 행렬을 어떻게 표현할까?")
        self.play(FadeIn(c))
        self.wait(0.8)

        # ================= 1) 구구단표 = rank 1 =================
        c = self.swap(c, cap("구구단표를 떠올려 보자"))
        u = [1, 2, 3, 4, 5]
        v = [1, 2, 3, 4, 5]
        G = VGroup(*[num_cell(0) for _ in range(25)]).arrange_in_grid(5, 5, buff=0).move_to(RIGHT * 0.6 + DOWN * 0.45)
        for cl in G:
            cl[1].set_opacity(0)
        col = VGroup(*[num_cell(x, color=ACCENT, txt_color=ACCENT) for x in u]).arrange(DOWN, buff=0).next_to(G, LEFT, buff=0.35)
        row = VGroup(*[num_cell(x, color=POS, txt_color=POS) for x in v]).arrange(RIGHT, buff=0).next_to(G, UP, buff=0.3)
        times = MathTex(r"\times", font_size=40, color=MUTED).next_to(col, UP, buff=0.3).shift(RIGHT * 0.15)
        self.play(FadeIn(col), FadeIn(row), FadeIn(times), Create(G))
        cells = []
        for i in range(5):
            for j in range(5):
                nc = num_cell(u[i] * v[j]).move_to(G[i * 5 + j])
                cells.append(Transform(G[i * 5 + j], nc))
        self.play(LaggedStart(*cells, lag_ratio=0.04), run_time=2.0)
        c = self.swap(c, cap("25칸인데, 실제로 필요한 숫자는 10개뿐"))
        cnt = VGroup(t("열 5개 + 행 5개 = 10개", 26, ACCENT), t("→ 25칸 전부 만들어진다", 26, FG)).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        cnt.next_to(G, RIGHT, buff=0.6)
        self.play(FadeIn(cnt))
        self.wait(1.2)

        hl = SurroundingRectangle(VGroup(*[G[2 * 5 + j] for j in range(5)]), color=LORA, buff=0.04)
        hl2 = SurroundingRectangle(VGroup(*[G[4 * 5 + j] for j in range(5)]), color=LORA, buff=0.04)
        c = self.swap(c, cap("모든 행이 같은 모양, 크기만 다르다", LORA))
        r3 = t("3 × (1, 2, 3, 4, 5)", 24, LORA).next_to(hl, RIGHT, buff=0.3)
        self.play(FadeOut(cnt), Create(hl), FadeIn(r3))
        self.play(Transform(hl, hl2), r3.animate.become(t("5 × (1, 2, 3, 4, 5)", 24, LORA).next_to(hl2, RIGHT, buff=0.3)))
        rk = t("패턴이 하나뿐  =  rank 1", 30, LORA).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(rk))
        self.wait(1.4)
        self.clear(c)

        # ================= 2) 패턴 겹치기 = rank 2 =================
        rng = np.random.default_rng(3)
        u1, v1 = rng.normal(0, 1, N), rng.normal(0, 1, N)
        u2, v2 = rng.normal(0, 1, N), rng.normal(0, 1, N)
        P1, P2 = np.outer(u1, v1), np.outer(u2, v2)
        vm = np.abs(P1 + P2).max()

        c = self.swap(c, cap("색으로 보면: 열 하나 × 행 하나 = 패턴 하나"))
        h1 = heat(P1, vm).move_to(LEFT * 3.6 + DOWN * 0.5)
        cu1 = heat(u1[:, None], np.abs(u1).max()).next_to(h1, LEFT, buff=0.25)
        rv1 = heat(v1[None, :], np.abs(v1).max()).next_to(h1, UP, buff=0.2)
        self.play(FadeIn(cu1), FadeIn(rv1))
        self.play(LaggedStart(*[FadeIn(sq) for sq in h1], lag_ratio=0.004), run_time=1.0)
        l1 = t("패턴 1", 24, FG).next_to(h1, DOWN, buff=0.2)
        self.play(FadeIn(l1))
        self.wait(0.5)

        h2 = heat(P2, vm).move_to(RIGHT * 0.2 + DOWN * 0.5)
        cu2 = heat(u2[:, None], np.abs(u2).max()).next_to(h2, LEFT, buff=0.25)
        rv2 = heat(v2[None, :], np.abs(v2).max()).next_to(h2, UP, buff=0.2)
        plus = MathTex("+", font_size=54).move_to((h1.get_right() + cu2.get_left()) / 2)
        l2 = t("패턴 2", 24, FG).next_to(h2, DOWN, buff=0.2)
        self.play(FadeIn(cu2), FadeIn(rv2), FadeIn(plus))
        self.play(LaggedStart(*[FadeIn(sq) for sq in h2], lag_ratio=0.004), FadeIn(l2), run_time=1.0)

        hs = heat(P1 + P2, vm).move_to(RIGHT * 4.6 + DOWN * 0.5)
        eq = MathTex("=", font_size=54).move_to((h2.get_right() + hs.get_left()) / 2)
        ls = t("겹친 결과", 24, LORA).next_to(hs, DOWN, buff=0.2)
        c = self.swap(c, cap("패턴 두 개를 겹치면  =  rank 2", LORA))
        self.play(FadeIn(eq), TransformFromCopy(VGroup(h1, h2), hs), FadeIn(ls), run_time=1.2)
        self.wait(1.0)

        # B, A 로 묶기
        c = self.swap(c, cap("열들을 모으면 B,  행들을 모으면 A"))
        Bm = np.stack([u1, u2], axis=1)
        Am = np.stack([v1, v2], axis=0)
        form = MathTex(r"B", r"\times", r"A", "=", r"u_1 v_1^{\top}", "+", r"u_2 v_2^{\top}", font_size=46)
        form[0].set_color(ACCENT)
        form[2].set_color(POS)
        form.to_edge(DOWN, buff=0.35)
        hs_target = RIGHT * 0.6 + DOWN * 0.7
        Bh = heat(Bm, np.abs(Bm).max()).next_to(hs.copy().move_to(hs_target), LEFT, buff=0.25)
        Ah = heat(Am, np.abs(Am).max()).next_to(hs.copy().move_to(hs_target), UP, buff=0.25)
        self.play(FadeOut(l1), FadeOut(l2), FadeOut(plus), FadeOut(eq), FadeOut(h1), FadeOut(h2),
                  hs.animate.move_to(hs_target), ls.animate.next_to(hs.copy().move_to(hs_target), RIGHT, buff=0.3),
                  ReplacementTransform(VGroup(cu1, cu2), Bh), ReplacementTransform(VGroup(rv1, rv2), Ah), run_time=1.4)
        bl = t("B", 30, ACCENT, weight="BOLD").next_to(Bh, LEFT, buff=0.2)
        al = t("A", 30, POS, weight="BOLD").next_to(Ah, LEFT, buff=0.2)
        bd = t("12 × 2", 20, MUTED).next_to(bl, DOWN, buff=0.08)
        ad = t("2 × 12", 20, MUTED).next_to(al, DOWN, buff=0.08)
        self.play(FadeIn(bl), FadeIn(al), FadeIn(bd), FadeIn(ad), Write(form))
        rr = t("r = 겹치는 패턴 개수 = B의 열 수 = A의 행 수", 24, LORA).next_to(form, UP, buff=0.25)
        self.play(FadeIn(rr))
        self.wait(1.8)
        self.clear(c)

        # ================= 3) 실제 ΔW 는 패턴 몇 개에 몰려 있다 =================
        rng = np.random.default_rng(21)
        U = rng.normal(0, 1, (N, 3))
        V = rng.normal(0, 1, (3, N))
        T = U @ np.diag([3.0, 1.6, 0.9]) @ V / np.sqrt(N) + rng.normal(0, 0.06, (N, N))
        vt_max = np.abs(T).max()
        uu, ss, vvt = np.linalg.svd(T)

        c = self.swap(c, cap("파인튜닝에 필요한 변화 ΔW (예시)"))
        Th = heat(T, vt_max).move_to(LEFT * 4.2 + DOWN * 0.3)
        tl = MathTex(r"\Delta W", font_size=40).next_to(Th, DOWN, buff=0.2)
        self.play(LaggedStart(*[FadeIn(sq) for sq in Th], lag_ratio=0.003), FadeIn(tl), run_time=1.0)

        c = self.swap(c, cap("패턴으로 쪼개 보면: 센 패턴은 3개뿐"))
        ax = Axes(x_range=[0, N, 1], y_range=[0, 8, 2], x_length=6.2, y_length=3.2,
                  axis_config=dict(color=MUTED, stroke_width=1.5, include_ticks=False), tips=False).move_to(RIGHT * 2.4 + DOWN * 0.3)
        bars = VGroup()
        for k, sv in enumerate(ss):
            b = Rectangle(width=0.32, height=max(sv / 8 * 3.2, 0.02), stroke_width=0).set_fill(LORA if k < 3 else MUTED, 0.9)
            b.move_to(ax.c2p(k + 0.5, 0), aligned_edge=DOWN)
            bars.add(b)
        xl = t("패턴 (센 순서)", 20, MUTED).next_to(ax, DOWN, buff=0.15)
        yl = t("세기", 20, MUTED).next_to(ax, UP, buff=0.05).align_to(ax, LEFT)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl))
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.08), run_time=1.2)
        note = t("나머지는 거의 0  →  이게 LoRA가 믿는 가정 (low-rank)", 24, LORA).to_edge(DOWN, buff=0.4)
        self.play(FadeIn(note))
        self.wait(1.4)
        self.play(*[FadeOut(m) for m in [ax, bars, xl, yl, note]])

        # 근사 r = 1, 2, 3
        c = self.swap(c, cap("센 패턴부터 r개만 겹쳐 보면"))
        apps = VGroup()
        for i, r in enumerate([1, 2, 3]):
            Ar = uu[:, :r] @ np.diag(ss[:r]) @ vvt[:r]
            err = 100 * np.linalg.norm(T - Ar) / np.linalg.norm(T)
            h = heat(Ar, vt_max).move_to(LEFT * 1.2 + RIGHT * i * 3.1 + DOWN * 0.3)
            lab = VGroup(t(f"r = {r}", 26, LORA), t(f"오차 {err:.0f}%", 22, NEG if err > 10 else LORA)).arrange(DOWN, buff=0.08)
            lab.next_to(h, DOWN, buff=0.2)
            apps.add(VGroup(h, lab))
        for a in apps:
            self.play(LaggedStart(*[FadeIn(sq) for sq in a[0]], lag_ratio=0.002), FadeIn(a[1]), run_time=0.9)
            self.wait(0.4)
        c = self.swap(c, cap("r = 3 이면 원래 ΔW 와 거의 같다", LORA))
        cnt = t("144칸  ←  12×3 + 3×12 = 72개", 26, ACCENT).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(cnt))
        self.wait(1.6)
        self.clear(c)

        # ================= 4) 학습: B = 0 에서 시작, B, A 만 고친다 =================
        r = 3
        rng2 = np.random.default_rng(5)
        B = np.zeros((N, r))
        A = rng2.normal(0, 0.3, (r, N))
        LR = 0.05

        c = self.swap(c, cap("학습은?  B = 0, A = 랜덤으로 시작"))
        bvm, avm = 1.6, 1.2
        Bh = heat(B, bvm).move_to(LEFT * 5.7 + DOWN * 0.4)
        Ah = heat(A, avm).move_to(LEFT * 2.8 + UP * 1.4)
        BAh = heat(B @ A, vt_max).move_to(LEFT * 2.8 + DOWN * 0.4)
        Th = heat(T, vt_max).move_to(RIGHT * 3.6 + DOWN * 0.4)
        lb = t("B", 28, ACCENT, weight="BOLD").next_to(Bh, DOWN, buff=0.15)
        la = t("A", 28, POS, weight="BOLD").next_to(Ah, LEFT, buff=0.2)
        lba = MathTex(r"B \times A", font_size=36, color=LORA).next_to(BAh, DOWN, buff=0.15)
        lt = VGroup(t("목표 ΔW", 24, FG), t("(정답은 모름, 손실로만 안다)", 18, MUTED)).arrange(DOWN, buff=0.06).next_to(Th, DOWN, buff=0.15)
        vs = t("≈ ?", 40, MUTED).move_to((BAh.get_right() + Th.get_left()) / 2)
        frames = VGroup(*[SurroundingRectangle(m, color=MUTED, buff=0.03, stroke_width=1.5) for m in (Bh, Ah, BAh, Th)])
        self.play(FadeIn(Bh), FadeIn(Ah), FadeIn(BAh), FadeIn(lb), FadeIn(la), FadeIn(lba), FadeIn(Th), FadeIn(lt), FadeIn(vs),
                  Create(frames))
        z = t("B = 0 이라  B×A = 0  →  처음엔 원본 모델 그대로", 24, MUTED).to_edge(DOWN, buff=0.9)
        self.play(FadeIn(z))
        self.wait(1.2)

        err_box = VGroup(t("목표와의 차이", 20, MUTED), t("100%", 34, NEG)).arrange(DOWN, buff=0.1).to_corner(UR, buff=0.4).shift(DOWN * 0.7)
        step_l = t("step 0", 20, MUTED).next_to(err_box, DOWN, buff=0.15)
        c = self.swap(c, cap("경사하강으로 B, A 만 조금씩 고친다  (W 는 고정)", LORA))
        self.play(FadeOut(z), FadeIn(err_box), FadeIn(step_l))
        shown = [2, 5, 10, 18, 30, 50, 80, 120]
        k = 0
        for target_step in shown:
            while k < target_step:
                E = B @ A - T
                gB, gA = E @ A.T, B.T @ E
                B -= LR * gB
                A -= LR * gA
                k += 1
            err = 100 * np.linalg.norm(B @ A - T) / np.linalg.norm(T)
            self.play(*recolor(Bh, B, bvm), *recolor(Ah, A, avm), *recolor(BAh, B @ A, vt_max),
                      Transform(err_box[1], t(f"{err:.0f}%", 34, NEG if err > 15 else LORA).move_to(err_box[1])),
                      Transform(step_l, t(f"step {k}", 20, MUTED).move_to(step_l)), run_time=0.55)
        self.play(Transform(vs, t("≈", 44, LORA).move_to(vs)))
        self.wait(1.2)
        self.clear(c)

        # ================= 5) 정리 =================
        c = self.swap(c, cap("정리"))
        rows = VGroup(
            VGroup(t("큰 행렬", 28, FG), t("= 패턴 여러 개를 겹친 것", 28, MUTED)),
            VGroup(t("B × A", 28, LORA), t("= 패턴 r 개만 겹쳐서 표현", 28, MUTED)),
            VGroup(t("4096 × 4096", 28, FG), t("1,677만 칸  →  r = 8 이면 65,536개 (0.39%)", 28, ACCENT)),
            VGroup(t("학습 후", 28, FG), t("W + B×A 로 합친다  →  추론 속도 그대로", 28, MUTED)),
        )
        for rw in rows:
            rw.arrange(RIGHT, buff=0.5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.45).move_to(DOWN * 0.1)
        for rw in rows:
            self.play(FadeIn(rw, shift=RIGHT * 0.15), run_time=0.6)
        self.wait(2.6)
