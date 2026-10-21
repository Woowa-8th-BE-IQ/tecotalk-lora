"""씬 5. 길쭉한 3D 손실 골짜기: SGD vs Momentum vs AdamW.

렌더: ./render.sh s05_optimizers Optimizers3D
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from manim import *

from common.style import ACCENT, FG, LORA, MUTED, POS, t

START = np.array([-4.5, 1.6])
STEPS = 45
ZCAP = 4.0


def f(x, y):
    return 0.08 * x * x + 1.2 * y * y      # y 방향이 15배 가파름


def g(p):
    return np.array([0.16 * p[0], 2.4 * p[1]])


def run_sgd(lr=0.75):
    p, out = START.copy(), [START.copy()]
    for _ in range(STEPS):
        p = p - lr * g(p)
        out.append(p.copy())
    return out


def run_momentum(lr=0.12, beta=0.75):
    p, v, out = START.copy(), np.zeros(2), [START.copy()]
    for _ in range(STEPS):
        v = beta * v - lr * g(p)
        p = p + v
        out.append(p.copy())
    return out


def run_adamw(lr=0.2, b1=0.9, b2=0.999, wd=0.01, eps=1e-8):
    p, m, v, out = START.copy(), np.zeros(2), np.zeros(2), [START.copy()]
    for k in range(1, STEPS + 1):
        gr = g(p)
        m = b1 * m + (1 - b1) * gr
        v = b2 * v + (1 - b2) * gr * gr
        mh, vh = m / (1 - b1 ** k), v / (1 - b2 ** k)
        p = p - lr * (mh / (np.sqrt(vh) + eps) + wd * p)
        out.append(p.copy())
    return out


OPTS = [
    ("SGD", run_sgd, POS, "모든 방향에 같은 보폭 → 지그재그"),
    ("Momentum", run_momentum, ACCENT, "관성: 지그재그는 상쇄, 완만한 쪽은 가속"),
    ("AdamW", run_adamw, LORA, "방향마다 보폭을 따로 → 거의 곧장"),
]


class Optimizers3D(ThreeDScene):
    def fixed(self, *mobs):
        self.add_fixed_in_frame_mobjects(*mobs)
        return mobs

    def cap(self, s):
        c = t(s, 34).to_edge(UP, buff=0.35)
        return c

    def construct(self):
        self.set_camera_orientation(phi=62 * DEGREES, theta=-62 * DEGREES, zoom=0.88)

        ax = ThreeDAxes(x_range=[-5, 5, 1], y_range=[-2.2, 2.2, 1], z_range=[0, ZCAP, 1],
                        x_length=10, y_length=4.4, z_length=2.6,
                        axis_config=dict(color=MUTED, stroke_width=1, include_ticks=False),
                        tips=False).shift(IN * 1.1)

        def zc(x, y):
            return min(f(x, y), ZCAP)

        surf = Surface(lambda u, v: ax.c2p(u, v, zc(u, v)),
                       u_range=[-5, 5], v_range=[-2.2, 2.2], resolution=(30, 16),
                       fill_opacity=0.55, stroke_width=0.6, stroke_color="#4A5060", checkerboard_colors=False)
        surf.set_fill("#1B2130", 0.55)

        caption = self.cap("실제 지형: 방향마다 경사가 다르다")
        self.add_fixed_in_frame_mobjects(caption)
        self.play(FadeIn(caption))
        self.play(Create(ax), Create(surf), run_time=2.0)

        lab_x = t("w₁ 방향: 완만", 22, MUTED)
        lab_y = t("w₂ 방향: 15배 가파름", 22, MUTED)
        labs = VGroup(lab_x, lab_y).arrange(DOWN, aligned_edge=LEFT, buff=0.1).to_corner(DL, buff=0.4)
        self.add_fixed_in_frame_mobjects(labs)
        self.play(FadeIn(labs))
        goal = Dot3D(ax.c2p(0, 0, 0), radius=0.08, color=FG)
        self.play(FadeIn(goal))
        self.begin_ambient_camera_rotation(rate=0.04)
        self.wait(1.0)

        legend_items = []
        paths = []
        for k, (name, fn, col, desc) in enumerate(OPTS):
            pts2d = fn()
            pts = [ax.c2p(x, y, zc(x, y) + 0.04) for x, y in pts2d]
            path = VMobject(stroke_color=col, stroke_width=3.5).set_points_as_corners(pts)
            ball = Dot3D(pts[0], radius=0.11, color=col)

            new_cap = self.cap(f"{name}: {desc}")
            self.add_fixed_in_frame_mobjects(new_cap)
            self.remove(new_cap)
            item = VGroup(Dot(color=col, radius=0.08), t(name, 22, col)).arrange(RIGHT, buff=0.12)
            legend_items.append(item)
            leg = VGroup(*legend_items).arrange(DOWN, aligned_edge=LEFT, buff=0.12).to_corner(UR, buff=0.4).shift(DOWN * 0.6)
            self.add_fixed_in_frame_mobjects(item)
            self.remove(item)

            self.play(FadeOut(caption), FadeIn(new_cap), FadeIn(item), FadeIn(ball))
            caption = new_cap
            self.play(Create(path), MoveAlongPath(ball, path), run_time=4.0, rate_func=linear)
            paths.append((path, ball))
            self.wait(0.6)

        # 위에서 보기
        self.stop_ambient_camera_rotation()
        top_cap = self.cap("위에서 보면")
        self.add_fixed_in_frame_mobjects(top_cap)
        self.remove(top_cap)
        self.play(FadeOut(caption), FadeIn(top_cap))
        caption = top_cap
        self.move_camera(phi=0, theta=-90 * DEGREES, zoom=1.05, run_time=2.5)
        self.wait(1.5)

        end = VGroup(
            t("Adam: 기울기 ÷ 최근 기울기 크기 → 축 스케일 차이가 지워진다", 24, FG),
            t("AdamW의 W: 매 걸음 가중치를 0 쪽으로 살짝 당김 (감쇠를 분리)", 22, MUTED),
        ).arrange(DOWN, buff=0.15).to_edge(DOWN, buff=0.35)
        self.add_fixed_in_frame_mobjects(end)
        self.remove(end)
        self.play(FadeOut(labs), FadeIn(end, shift=UP * 0.1))
        self.wait(3.0)
