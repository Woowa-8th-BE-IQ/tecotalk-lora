"""씬 0-e. 좌: 가중치 평면 (w1, w2)  /  우: 손실 지형 L(w1, w2).
점 = 가중치 값, 공 = 그때의 손실. 편미분 두 개 → 가장 빨리 내려가는 방향 → 한 걸음씩 굴러 내려간다.
출발점이 다르면 다른 골짜기에 멈출 수 있다.

렌더: ./render.sh s00e_ball BallDescent
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from manim import *

from common.style import ACCENT, BG, FG, LORA, MUTED, NEG, POS, t

THETA = -55 * DEGREES
PHI = 62 * DEGREES
ZOOM = 0.7
SHIFT = 3.35         # 화면 오른쪽으로 보낼 거리 (화면 단위)
LR = 0.25
YCOL = "#B48CFF"
START1 = (2.5, 1.9)
START2 = (-2.4, 2.5)


def L(x, y):
    return (0.16 * (x * x + y * y) - 1.3 * np.exp(-((x - 1.1) ** 2 + (y + 0.9) ** 2) / 0.9)
            - 0.8 * np.exp(-((x + 1.4) ** 2 + (y - 1.2) ** 2) / 0.6) + 0.12 * np.sin(2.1 * x) * np.cos(1.7 * y) + 1.5)


def grad(x, y, h=1e-4):
    return np.array([(L(x + h, y) - L(x - h, y)) / (2 * h), (L(x, y + h) - L(x, y - h)) / (2 * h)])


def path_from(start, n):
    p = np.array(start, float)
    out = [p.copy()]
    for _ in range(n):
        p = p - LR * grad(*p)
        out.append(p.copy())
    return out


class BallDescent(ThreeDScene):
    def fixed(self, m):
        self.add_fixed_in_frame_mobjects(m)
        self.remove(m)
        return m

    def cap(self, s, color=FG):
        return self.fixed(t(s, 32, color).to_edge(UP, buff=0.25))

    def swap(self, old, new):
        self.play(FadeOut(old), FadeIn(new), run_time=0.5)
        return new

    def construct(self):
        self.set_camera_orientation(phi=PHI, theta=THETA, zoom=ZOOM)
        d = SHIFT / ZOOM
        right_vec = np.array([-np.sin(THETA), np.cos(THETA), 0.0])
        OFFSET = d * right_vec + np.array([0, 0, -1.4])

        # ---------- 오른쪽: 손실 지형 ----------
        ax = ThreeDAxes(x_range=[-3, 3, 1], y_range=[-3, 3, 1], z_range=[0, 4.5, 1],
                        x_length=6, y_length=6, z_length=3.2,
                        axis_config=dict(color=MUTED, stroke_width=1.2, include_ticks=False), tips=False).shift(OFFSET)
        surf = Surface(lambda u, v: ax.c2p(u, v, L(u, v)), u_range=[-3, 3], v_range=[-3, 3], resolution=(36, 36),
                       fill_opacity=0.75, stroke_width=0.3, stroke_color="#5A6274")
        surf.set_fill_by_value(axes=ax, colorscale=[("#1F3A68", 0.5), ("#2E6FB0", 1.5), ("#2BD9A0", 2.6), (ACCENT, 4.3)], axis=2)
        floor = NumberPlane(x_range=[-3, 3, 1], y_range=[-3, 3, 1], x_length=6, y_length=6,
                            background_line_style=dict(stroke_color="#2A2E38", stroke_width=1),
                            axis_config=dict(stroke_color="#3A3F4B")).move_to(ax.c2p(0, 0, 0))
        lw1 = MathTex("w_1", font_size=36).move_to(ax.c2p(3.5, 0, 0))
        lw2 = MathTex("w_2", font_size=36).move_to(ax.c2p(0, 3.5, 0))
        lL = MathTex("L", font_size=36).move_to(ax.c2p(-0.3, 0, 4.7))
        self.add_fixed_orientation_mobjects(lw1, lw2, lL)
        self.remove(lw1, lw2, lL)

        # ---------- 왼쪽: 가중치 평면 ----------
        plane = NumberPlane(x_range=[-3, 3, 1], y_range=[-3, 3, 1], x_length=5.0, y_length=5.0,
                            background_line_style=dict(stroke_color="#2A3446", stroke_width=1.2),
                            axis_config=dict(stroke_color=MUTED)).move_to(LEFT * 3.7 + DOWN * 0.35)
        pw1 = MathTex("w_1", font_size=32).next_to(plane, RIGHT, buff=0.1).shift(DOWN * 0.05)
        pw2 = MathTex("w_2", font_size=32).next_to(plane.c2p(0, 3), UP, buff=0.08)
        left_t = t("가중치 (w₁, w₂)", 24, POS).next_to(plane, UP, buff=0.35).align_to(plane, LEFT)
        right_t = t("손실 L(w₁, w₂)", 24, ACCENT).move_to(RIGHT * 3.6 + UP * 2.85)
        left = VGroup(plane, pw1, pw2, left_t, right_t)
        self.fixed(left)

        px, py = ValueTracker(START1[0]), ValueTracker(START1[1])

        dot = Dot(radius=0.1, color=ACCENT)
        dot.add_updater(lambda m: m.move_to(plane.c2p(px.get_value(), py.get_value())))
        self.fixed(dot)
        ball = Dot3D(radius=0.13, color=ACCENT)
        ball.add_updater(lambda m: m.move_to(ax.c2p(px.get_value(), py.get_value(), L(px.get_value(), py.get_value()) + 0.06)))
        drop = always_redraw(lambda: DashedLine(ax.c2p(px.get_value(), py.get_value(), 0),
                                                ax.c2p(px.get_value(), py.get_value(), L(px.get_value(), py.get_value())),
                                                color=ACCENT, stroke_width=2, dash_length=0.08))
        shadow = Dot(radius=0.06, color=ACCENT)
        shadow.add_updater(lambda m: m.move_to(ax.c2p(px.get_value(), py.get_value(), 0)))

        lossbox = self.fixed(VGroup(t("손실", 20, MUTED), t("0.00", 32, ACCENT)).arrange(RIGHT, buff=0.2)
                             .to_corner(DR, buff=0.4))

        def loss_text(col=ACCENT):
            v = L(px.get_value(), py.get_value())
            return t(f"{v:.2f}", 32, col).move_to(lossbox[1])

        # ================= 1) 두 화면 =================
        c = self.cap("가중치 2개의 손실을, 지형으로 그리면")
        self.play(FadeIn(c), FadeIn(left))
        self.play(Create(floor), Create(surf), FadeIn(lw1), FadeIn(lw2), run_time=2.0)
        self.add(dot, ball, drop, shadow)
        self.play(FadeIn(dot), FadeIn(ball), FadeIn(lossbox))
        self.play(Transform(lossbox[1], loss_text()))
        self.wait(0.4)

        # ================= 2) 연동 =================
        c = self.swap(c, self.cap("왼쪽 점 = 가중치 값,   오른쪽 공 = 그때의 손실"))
        lossbox[1].add_updater(lambda m: m.become(loss_text()))
        for tx, ty in [(0.2, 2.4), (-1.6, 0.4), (0.6, -1.8), START1]:
            self.play(px.animate.set_value(tx), py.animate.set_value(ty), run_time=1.0)
        self.wait(0.4)

        # ================= 3) 어느 방향으로? =================
        c = self.swap(c, self.cap("어느 방향으로 가면 손실이 가장 빨리 줄어들까?"))
        x0, y0 = START1
        g0 = grad(x0, y0)
        center = plane.c2p(x0, y0)
        arrows = VGroup()
        for k in range(8):
            a = k * TAU / 8
            dvec = np.array([np.cos(a), np.sin(a)])
            arrows.add(Arrow(center, center + 0.8 * np.array([dvec[0], dvec[1], 0]), buff=0.12,
                             color=MUTED, stroke_width=4, max_tip_length_to_length_ratio=0.3))
        self.fixed(arrows)
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.08))
        self.wait(0.6)

        # 편미분 두 개
        c = self.swap(c, self.cap("편미분 두 개로 계산할 수 있다", ACCENT))
        pd = self.fixed(VGroup(
            MathTex(r"\frac{\partial L}{\partial w_1} = " + f"{g0[0]:.2f}", font_size=34, color=ACCENT),
            MathTex(r"\frac{\partial L}{\partial w_2} = " + f"{g0[1]:.2f}", font_size=34, color=YCOL),
        ).arrange(DOWN, buff=0.2, aligned_edge=LEFT).move_to(plane.c2p(-1.7, 1.9)))
        bg = self.fixed(BackgroundRectangle(pd, color=BG, fill_opacity=0.85, buff=0.12))
        self.play(FadeIn(bg), FadeIn(pd))
        self.wait(0.6)

        # 8방향 각각 얼마나 변하나 → 색
        slopes = []
        for k in range(8):
            a = k * TAU / 8
            slopes.append(g0[0] * np.cos(a) + g0[1] * np.sin(a))
        smax = max(abs(s) for s in slopes)
        c = self.swap(c, self.cap("방향마다 변화량 = w₁ 몫 + w₂ 몫  (초록: 내려감, 빨강: 올라감)"))
        self.play(*[arrows[k].animate.set_color(interpolate_color(ManimColor(BG), ManimColor(LORA if s < 0 else NEG),
                                                                   0.35 + 0.65 * abs(s) / smax))
                    for k, s in enumerate(slopes)], run_time=1.0)
        self.wait(0.8)

        dn = -g0 / np.linalg.norm(g0)
        best = Arrow(center, center + 1.35 * np.array([dn[0], dn[1], 0]), buff=0.12, color=LORA, stroke_width=8,
                     max_tip_length_to_length_ratio=0.25)
        self.fixed(best)
        c = self.swap(c, self.cap("두 편미분을 모아 반대로  →  가장 빨리 내려가는 방향", LORA))
        self.play(GrowArrow(best), arrows.animate.set_opacity(0.25))
        name = self.fixed(t("(두 편미분을 모은 화살표 = 기울기,  그 반대로 간다)", 20, MUTED)
                          .next_to(plane, DOWN, buff=0.15))
        self.play(FadeIn(name))
        self.wait(1.4)
        self.play(FadeOut(arrows), FadeOut(best), FadeOut(pd), FadeOut(bg), FadeOut(name))

        # ================= 4) 굴러 내려가기 =================
        c = self.swap(c, self.cap("그 방향으로 한 걸음  →  다시 편미분  →  또 한 걸음"))
        P1 = path_from(START1, 24)
        trail2d = VMobject(stroke_color=ACCENT, stroke_width=3)
        trail2d.set_points_as_corners([plane.c2p(*P1[0]), plane.c2p(*P1[0])])
        self.fixed(trail2d)
        self.add(trail2d)
        trail3d = VGroup()
        self.add(trail3d)
        for k in range(1, len(P1)):
            a, b = P1[k - 1], P1[k]
            seg2 = Line(plane.c2p(*a), plane.c2p(*b), color=ACCENT, stroke_width=3)
            self.fixed(seg2)
            seg3 = Line(ax.c2p(a[0], a[1], L(*a) + 0.04), ax.c2p(b[0], b[1], L(*b) + 0.04), color=ACCENT, stroke_width=4)
            rt = 0.45 if k < 6 else (0.3 if k < 14 else 0.18)
            self.play(px.animate.set_value(b[0]), py.animate.set_value(b[1]), FadeIn(seg2), Create(seg3), run_time=rt)
            trail3d.add(seg3)
            if k == 8:
                note = self.fixed(t("바닥에 가까울수록 경사가 완만  →  걸음이 저절로 작아진다", 22, MUTED).to_edge(DOWN, buff=0.35))
                self.play(FadeIn(note), run_time=0.4)
        self.wait(0.8)
        self.play(FadeOut(note))

        # ================= 5) 다른 출발점 =================
        lossbox[1].clear_updaters()
        first_loss = L(*P1[-1])
        keep = self.fixed(t(f"첫 번째 공: 손실 {first_loss:.2f}", 22, ACCENT).next_to(lossbox, UP, buff=0.2).align_to(lossbox, RIGHT))
        self.play(FadeIn(keep))
        c = self.swap(c, self.cap("출발점이 다르면?"))
        qx, qy = ValueTracker(START2[0]), ValueTracker(START2[1])
        dot2 = Dot(radius=0.1, color=POS)
        dot2.add_updater(lambda m: m.move_to(plane.c2p(qx.get_value(), qy.get_value())))
        self.fixed(dot2)
        ball2 = Dot3D(radius=0.13, color=POS)
        ball2.add_updater(lambda m: m.move_to(ax.c2p(qx.get_value(), qy.get_value(), L(qx.get_value(), qy.get_value()) + 0.06)))
        lossbox2 = self.fixed(VGroup(t("두 번째 공: 손실", 22, POS), t(f"{L(*START2):.2f}", 26, POS)).arrange(RIGHT, buff=0.15)
                              .next_to(keep, UP, buff=0.15).align_to(lossbox, RIGHT))
        self.add(dot2, ball2)
        self.play(FadeIn(dot2), FadeIn(ball2), FadeIn(lossbox2))
        P2 = path_from(START2, 18)
        for k in range(1, len(P2)):
            a, b = P2[k - 1], P2[k]
            seg2 = Line(plane.c2p(*a), plane.c2p(*b), color=POS, stroke_width=3)
            self.fixed(seg2)
            seg3 = Line(ax.c2p(a[0], a[1], L(*a) + 0.04), ax.c2p(b[0], b[1], L(*b) + 0.04), color=POS, stroke_width=4)
            self.play(qx.animate.set_value(b[0]), qy.animate.set_value(b[1]), FadeIn(seg2), Create(seg3),
                      Transform(lossbox2[1], t(f"{L(*b):.2f}", 26, POS).move_to(lossbox2[1])),
                      run_time=0.4 if k < 5 else 0.2)
        c = self.swap(c, self.cap("더 깊은 골짜기가 있어도, 근처 골짜기에 멈출 수 있다 (지역 최솟값)", POS))
        self.wait(1.8)

        # ================= 6) 마무리 =================
        end = self.fixed(VGroup(
            t("가중치가 70억 개여도 똑같다", 30, FG),
            t("편미분 70억 개  →  모아서 반대로  →  한 걸음", 28, LORA),
        ).arrange(DOWN, buff=0.15))
        ebg = self.fixed(BackgroundRectangle(end, color=BG, fill_opacity=0.9, buff=0.25))
        VGroup(ebg, end).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(ebg), FadeIn(end, shift=UP * 0.1))
        self.wait(2.6)
