"""씬 4. 학습률 = 보폭. 포물선 위 공 4개 + 로스 곡선.

렌더: ./render.sh s04_learning_rate LearningRate
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from manim import *

from common.style import ACCENT, FG, LORA, MUTED, NEG, POS, t

W0 = -2.0
STEPS = 12
LIMIT = 3.0

CASES = [
    (0.05, "너무 작음", POS),
    (0.35, "적당", LORA),
    (0.90, "큼", ACCENT),
    (1.05, "너무 큼", NEG),
]


def loss(w):
    return w * w


def grad(w):
    return 2 * w


def cap(s):
    return t(s, 36).to_edge(UP, buff=0.35)


def make_axes(x_len, y_len):
    return Axes(x_range=[-3, 3, 1], y_range=[0, 9, 3], x_length=x_len, y_length=y_len,
                axis_config=dict(color=MUTED, stroke_width=1.5, include_ticks=False), tips=False)


class LearningRate(Scene):
    def construct(self):
        caption = cap("눈 가리고 산 내려가기")
        self.play(FadeIn(caption, shift=DOWN * 0.2))

        # ---------- 1) 한 개짜리: 기울기만 안다 ----------
        ax = make_axes(8, 4.2).shift(DOWN * 0.6)
        curve = ax.plot(loss, x_range=[-3, 3], color=FG, stroke_width=3)
        x_lab = t("가중치 w", 22, MUTED).next_to(ax, DOWN, buff=0.15)
        y_lab = t("손실", 22, MUTED).next_to(ax, LEFT, buff=0.15).shift(UP * 1.5)
        ball = Dot(ax.c2p(W0, loss(W0)), radius=0.12, color=ACCENT)
        self.play(Create(ax), Create(curve), FadeIn(x_lab), FadeIn(y_lab))
        self.play(FadeIn(ball, scale=0.5))

        tangent = TangentLine(curve, alpha=(W0 + 3) / 6, length=2.4, color=MUTED, stroke_width=2)
        arrow = Arrow(ball.get_center(), ball.get_center() + RIGHT * 1.2 + DOWN * 0.0,
                      buff=0.15, color=ACCENT, stroke_width=5, max_tip_length_to_length_ratio=0.25)
        note = t("발밑의 기울기만 느낄 수 있다", 26, FG).to_edge(DOWN, buff=0.35)
        self.play(Create(tangent), FadeIn(note))
        self.play(GrowArrow(arrow))
        self.wait(0.6)

        rule = MathTex(r"w", r"\leftarrow", r"w", r"-", r"\eta", r"\cdot", r"\nabla L",
                       font_size=50).next_to(caption, DOWN, buff=0.3)
        rule[4].set_color(ACCENT)
        r_eta = t("보폭", 20, ACCENT).next_to(rule[4], DOWN, buff=0.08)
        r_g = t("기울기", 20, MUTED).next_to(rule[6], DOWN, buff=0.08)
        self.play(Transform(caption, cap("학습률 η = 한 걸음 보폭")),
                  Write(rule), FadeIn(r_eta), FadeIn(r_g), FadeOut(note))
        self.wait(0.4)

        # 한 걸음 시연
        w = W0
        for _ in range(3):
            nw = w - 0.3 * grad(w)
            seg = Line(ax.c2p(w, loss(w)), ax.c2p(nw, loss(nw)), color=ACCENT, stroke_width=2.5)
            self.play(ball.animate.move_to(ax.c2p(nw, loss(nw))), Create(seg),
                      FadeOut(tangent), FadeOut(arrow), run_time=0.6)
            tangent = TangentLine(curve, alpha=(nw + 3) / 6, length=2.0, color=MUTED, stroke_width=2)
            self.add(tangent)
            w = nw
        self.wait(0.4)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not caption])

        # ---------- 2) 4개 비교 ----------
        self.play(Transform(caption, cap("보폭에 따라 어떻게 될까?")))
        centers = [np.array([-3.45, 0.75, 0]), np.array([3.45, 0.75, 0]),
                   np.array([-3.45, -2.35, 0]), np.array([3.45, -2.35, 0])]
        panels = []
        for (lr, name, col), c in zip(CASES, centers):
            pax = make_axes(5.2, 2.1).move_to(c)
            pcurve = pax.plot(loss, x_range=[-3, 3], color=MUTED, stroke_width=2)
            title = t(f"η = {lr}  ·  {name}", 24, col).next_to(pax, UP, buff=0.1)
            pball = Dot(pax.c2p(W0, loss(W0)), radius=0.09, color=col)
            panels.append(dict(ax=pax, curve=pcurve, title=title, ball=pball, lr=lr, col=col,
                               w=W0, hist=[loss(W0)], dead=False))
        self.play(*[AnimationGroup(Create(p["ax"]), Create(p["curve"]), FadeIn(p["title"]), FadeIn(p["ball"]))
                    for p in panels], run_time=1.0)

        step_lab = t("step 0", 24, MUTED).to_corner(UR, buff=0.4)
        self.add(step_lab)
        for k in range(1, STEPS + 1):
            anims = []
            for p in panels:
                if p["dead"]:
                    continue
                w = p["w"]
                nw = w - p["lr"] * grad(w)
                if abs(nw) > LIMIT:
                    p["dead"] = True
                    edge = np.sign(nw) * 3.0
                    boom = t("발산!", 26, NEG, weight="BOLD").move_to(p["ax"].c2p(0, 6.5))
                    anims += [p["ball"].animate.move_to(p["ax"].c2p(edge, 9)).set_opacity(0),
                              FadeIn(boom, scale=1.4)]
                    p["hist"].append(None)
                    continue
                seg = Line(p["ax"].c2p(w, loss(w)), p["ax"].c2p(nw, loss(nw)), color=p["col"], stroke_width=2)
                anims += [p["ball"].animate.move_to(p["ax"].c2p(nw, loss(nw))), Create(seg)]
                p["w"] = nw
                p["hist"].append(loss(nw))
            anims.append(Transform(step_lab, t(f"step {k}", 24, MUTED).to_corner(UR, buff=0.4)))
            self.play(*anims, run_time=0.42)
        self.wait(1.0)

        # ---------- 3) 로스 곡선 ----------
        self.play(*[FadeOut(m) for m in self.mobjects if m is not caption])
        self.play(Transform(caption, cap("로스로 보면")))
        lax = Axes(x_range=[0, STEPS, 2], y_range=[0, 6.5, 1], x_length=9.5, y_length=4.8,
                   axis_config=dict(color=MUTED, stroke_width=1.5, include_ticks=False), tips=False).shift(DOWN * 0.4 + LEFT * 0.8)
        lx = t("step", 22, MUTED).next_to(lax, DOWN, buff=0.15)
        ly = t("손실 (로그)", 22, MUTED).rotate(PI / 2).next_to(lax, LEFT, buff=0.2)
        self.play(Create(lax), FadeIn(lx), FadeIn(ly))

        legend = VGroup()
        for p in panels:
            pts = []
            for k, L in enumerate(p["hist"]):
                if L is None:
                    pts.append(lax.c2p(k, 6.5))
                    break
                pts.append(lax.c2p(k, max(np.log10(L), -5) + 5))
            line = VMobject(color=p["col"], stroke_width=4).set_points_as_corners(pts)
            end_lab = t(f"η={p['lr']}", 22, p["col"]).next_to(pts[-1], RIGHT, buff=0.12)
            if p["dead"]:
                end_lab = t(f"η={p['lr']}  발산", 22, p["col"]).next_to(pts[-1], UP, buff=0.12)
            self.play(Create(line), FadeIn(end_lab), run_time=0.9)
        self.wait(0.6)

        msg = VGroup(
            t("작으면 느리고, 크면 출렁이고, 너무 크면 터진다", 26, FG),
        ).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(msg, shift=UP * 0.1))
        self.wait(1.5)

        hook = t("그런데 실제 지형은 방향마다 경사가 다르다 → 3D로", 26, ACCENT).to_edge(DOWN, buff=0.3)
        self.play(Transform(msg, hook))
        self.wait(2.0)

