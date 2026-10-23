"""씬 0-e. 좌: 나침반 (공이 선 자리에서 방향마다 손실이 얼마나 변하나)  /  우: 손실 지형 위를 굴러가는 공.

나침반 둘레 = 360° 모든 방향. 초록 = 내려감, 빨강 = 올라감. 바늘 = 가장 빨리 내려가는 방향 (경사가 셀수록 길다).
편미분 두 개(w1 몫, w2 몫)면 모든 방향을 계산할 수 있다 → 바늘 방향으로 한 걸음씩 → 바닥에선 나침반이 회색.
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
ZOOM = 0.72
SHIFT = 3.0
LR = 0.25
YCOL = "#B48CFF"
START1 = (2.5, 1.9)
START2 = (-2.4, 2.5)
N_ARC = 48
C_CENTER = LEFT * 3.75 + DOWN * 0.05
R = 1.55
GRAY = "#3A3F4B"


def L(x, y):
    return (0.16 * (x * x + y * y) - 1.3 * np.exp(-((x - 1.1) ** 2 + (y + 0.9) ** 2) / 0.9)
            - 0.8 * np.exp(-((x + 1.4) ** 2 + (y - 1.2) ** 2) / 0.6) + 0.12 * np.sin(2.1 * x) * np.cos(1.7 * y) + 1.5)


def grad(x, y, h=1e-4):
    return np.array([(L(x + h, y) - L(x - h, y)) / (2 * h), (L(x, y + h) - L(x, y - h)) / (2 * h)])


G_REF = float(np.linalg.norm(grad(*START1)))


def path_from(start, n):
    p = np.array(start, float)
    out = [p.copy()]
    for _ in range(n):
        p = p - LR * grad(*p)
        out.append(p.copy())
    return out


def arc_color(g, k):
    a = (k + 0.5) * TAU / N_ARC
    s = (g[0] * np.cos(a) + g[1] * np.sin(a)) / G_REF
    s = float(np.clip(s, -1, 1))
    return interpolate_color(ManimColor(GRAY), ManimColor(LORA if s < 0 else NEG), min(1.0, abs(s) * 1.15))


def needle_for(g):
    v = -g / G_REF
    n = np.linalg.norm(v)
    if n < 1e-6:
        v, n = np.array([1e-3, 0.0]), 1e-3
    length = float(np.clip(n, 0.1, 1.0)) * R * 0.9
    d = v / n
    end = C_CENTER + length * np.array([d[0], d[1], 0])
    return Arrow(C_CENTER, end, buff=0, color=LORA, stroke_width=7, max_tip_length_to_length_ratio=0.3,
                 max_stroke_width_to_length_ratio=12)


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
        self.add_fixed_orientation_mobjects(lw1, lw2)
        self.remove(lw1, lw2)
        right_t = self.fixed(t("손실 지형", 24, ACCENT).move_to(RIGHT * 3.4 + UP * 2.85))

        # ---------- 왼쪽: 나침반 ----------
        arcs = VGroup(*[Arc(radius=R, start_angle=k * TAU / N_ARC + 0.01, angle=TAU / N_ARC - 0.02,
                            arc_center=C_CENTER, stroke_width=18, color=GRAY) for k in range(N_ARC)])
        cross = VGroup(DashedLine(C_CENTER + LEFT * R * 0.85, C_CENTER + RIGHT * R * 0.85, stroke_width=1, color=GRAY),
                       DashedLine(C_CENTER + DOWN * R * 0.85, C_CENTER + UP * R * 0.85, stroke_width=1, color=GRAY))
        hub = Dot(C_CENTER, radius=0.07, color=FG)
        dirs = VGroup(
            t("w₁ 늘리기", 20, MUTED).next_to(C_CENTER + RIGHT * R, RIGHT, buff=0.22),
            t("w₁ 줄이기", 20, MUTED).next_to(C_CENTER + LEFT * R, LEFT, buff=0.22),
            t("w₂ 늘리기", 20, MUTED).next_to(C_CENTER + UP * R, UP, buff=0.22),
            t("w₂ 줄이기", 20, MUTED).next_to(C_CENTER + DOWN * R, DOWN, buff=0.22),
        )
        left_t = t("나침반: 이 자리에서 어느 쪽이 내리막?", 22, FG).move_to(C_CENTER + UP * (R + 0.9))
        legend = t("초록 = 내려감   빨강 = 올라감", 18, MUTED).move_to(C_CENTER + DOWN * (R + 0.8))
        SLOT = C_CENTER + DOWN * (R + 1.35)
        compass = VGroup(cross, arcs, hub, dirs, left_t, legend)
        self.fixed(compass)

        px, py = ValueTracker(START1[0]), ValueTracker(START1[1])
        qx, qy = ValueTracker(START2[0]), ValueTracker(START2[1])
        src = {"t": (px, py)}

        def cur_grad():
            a, b = src["t"]
            return grad(a.get_value(), b.get_value())

        def bind_arcs():
            for k, arc in enumerate(arcs):
                arc.add_updater(lambda m, k=k: m.set_stroke(color=arc_color(cur_grad(), k)))

        needle = self.fixed(needle_for(grad(*START1)))

        ball = Dot3D(radius=0.13, color=ACCENT)
        ball.add_updater(lambda m: m.move_to(ax.c2p(px.get_value(), py.get_value(), L(px.get_value(), py.get_value()) + 0.06)))
        drop = always_redraw(lambda: DashedLine(ax.c2p(px.get_value(), py.get_value(), 0),
                                                ax.c2p(px.get_value(), py.get_value(), L(px.get_value(), py.get_value())),
                                                color=ACCENT, stroke_width=2, dash_length=0.08))

        lossbox = self.fixed(VGroup(t("손실", 20, MUTED), t("0.00", 32, ACCENT)).arrange(RIGHT, buff=0.2)
                             .to_corner(DR, buff=0.4))

        def loss_text():
            return t(f"{L(px.get_value(), py.get_value()):.2f}", 32, ACCENT).move_to(lossbox[1])

        # ================= 1) 지형과 공 =================
        c = self.cap("가중치에 따라 손실이 달라진다  →  손실 지형")
        self.play(FadeIn(c), FadeIn(right_t))
        self.play(Create(floor), Create(surf), FadeIn(lw1), FadeIn(lw2), run_time=2.0)
        self.add(ball, drop)
        self.play(FadeIn(ball), FadeIn(lossbox))
        self.play(Transform(lossbox[1], loss_text()))
        c = self.swap(c, self.cap("공 = 지금 가중치에서의 손실.  목표: 가장 낮은 곳"))
        self.wait(1.0)

        # ================= 2) 나침반 =================
        c = self.swap(c, self.cap("공이 선 자리에서, 방향마다 손실이 얼마나 변할까?"))
        self.play(FadeIn(compass))
        self.wait(0.4)
        g0 = grad(*START1)
        self.play(LaggedStart(*[arc.animate.set_stroke(color=arc_color(g0, k)) for k, arc in enumerate(arcs)],
                             lag_ratio=0.03), run_time=1.8)
        self.wait(0.6)

        # 편미분 두 개
        c = self.swap(c, self.cap("편미분 두 개만 알면, 모든 방향을 계산할 수 있다", ACCENT))
        pd = self.fixed(MathTex(r"\frac{\partial L}{\partial w_1} = " + f"{g0[0]:.2f}", r"\qquad",
                                r"\frac{\partial L}{\partial w_2} = " + f"{g0[1]:.2f}", font_size=30).move_to(SLOT))
        pd[0].set_color(ACCENT)
        pd[2].set_color(YCOL)
        self.play(FadeIn(pd[0]), arcs[0].animate.set_stroke(width=30), arcs[-1].animate.set_stroke(width=30))
        self.play(arcs[0].animate.set_stroke(width=18), arcs[-1].animate.set_stroke(width=18), run_time=0.4)
        q = N_ARC // 4
        self.play(FadeIn(pd[2]), arcs[q].animate.set_stroke(width=30), arcs[q - 1].animate.set_stroke(width=30))
        self.play(arcs[q].animate.set_stroke(width=18), arcs[q - 1].animate.set_stroke(width=18), run_time=0.4)
        c = self.swap(c, self.cap("어느 방향이든  =  w₁ 몫 + w₂ 몫", ACCENT))
        self.wait(1.0)

        # 바늘
        c = self.swap(c, self.cap("가장 진한 초록  =  가장 빨리 내려가는 방향", LORA))
        self.play(GrowArrow(needle))
        name = self.fixed(t("바늘 = 두 편미분을 모아 반대로 (기울기의 반대)", 20, LORA).move_to(SLOT))
        self.play(FadeOut(pd), FadeIn(name))
        self.wait(1.2)

        # 실시간 연동
        bind_arcs()
        needle.add_updater(lambda m: m.become(needle_for(cur_grad())))
        lossbox[1].add_updater(lambda m: m.become(loss_text()))
        c = self.swap(c, self.cap("공이 움직이면 나침반도 바뀐다"))
        for tx, ty in [(0.4, 2.3), (-1.0, -0.3), START1]:
            self.play(px.animate.set_value(tx), py.animate.set_value(ty), run_time=1.1)
        self.play(FadeOut(name))

        # ================= 3) 굴러 내려가기 =================
        c = self.swap(c, self.cap("바늘 방향으로 한 걸음  →  다시 재고  →  또 한 걸음"))
        P1 = path_from(START1, 24)
        note = None
        for k in range(1, len(P1)):
            a, b = P1[k - 1], P1[k]
            seg3 = Line(ax.c2p(a[0], a[1], L(*a) + 0.04), ax.c2p(b[0], b[1], L(*b) + 0.04), color=ACCENT, stroke_width=4)
            shd = Line(ax.c2p(a[0], a[1], 0), ax.c2p(b[0], b[1], 0), color=ACCENT, stroke_width=2, stroke_opacity=0.5)
            rt = 0.5 if k < 6 else (0.32 if k < 14 else 0.2)
            self.play(px.animate.set_value(b[0]), py.animate.set_value(b[1]), Create(seg3), Create(shd), run_time=rt)
            if k == 7:
                note = self.fixed(t("경사가 약해질수록 바늘이 짧아진다  →  걸음도 작아진다", 20, MUTED).move_to(SLOT))
                self.play(FadeIn(note), run_time=0.4)
        c = self.swap(c, self.cap("바닥: 어느 쪽으로 가도 거의 안 변한다  →  멈춘다", LORA))
        self.play(FadeOut(note))
        self.wait(1.2)

        # ================= 4) 다른 출발점 =================
        for arc in arcs:
            arc.clear_updaters()
        needle.clear_updaters()
        lossbox[1].clear_updaters()
        first = L(*P1[-1])
        keep = self.fixed(t(f"첫 번째 공: 손실 {first:.2f}", 22, ACCENT).next_to(lossbox, UP, buff=0.2).align_to(lossbox, RIGHT))
        self.play(FadeIn(keep), FadeOut(lossbox))
        c = self.swap(c, self.cap("출발점이 다르면?"))
        src["t"] = (qx, qy)
        ball2 = Dot3D(radius=0.13, color=POS)
        ball2.add_updater(lambda m: m.move_to(ax.c2p(qx.get_value(), qy.get_value(), L(qx.get_value(), qy.get_value()) + 0.06)))
        lb2 = self.fixed(VGroup(t("두 번째 공: 손실", 22, POS), t(f"{L(*START2):.2f}", 26, POS)).arrange(RIGHT, buff=0.15)
                         .next_to(keep, UP, buff=0.15).align_to(keep, RIGHT))
        self.add(ball2)
        g2 = grad(*START2)
        self.play(FadeIn(ball2), FadeIn(lb2),
                  *[arc.animate.set_stroke(color=arc_color(g2, k)) for k, arc in enumerate(arcs)],
                  needle.animate.become(needle_for(g2)))
        bind_arcs()
        needle.add_updater(lambda m: m.become(needle_for(cur_grad())))
        P2 = path_from(START2, 18)
        for k in range(1, len(P2)):
            a, b = P2[k - 1], P2[k]
            seg3 = Line(ax.c2p(a[0], a[1], L(*a) + 0.04), ax.c2p(b[0], b[1], L(*b) + 0.04), color=POS, stroke_width=4)
            shd = Line(ax.c2p(a[0], a[1], 0), ax.c2p(b[0], b[1], 0), color=POS, stroke_width=2, stroke_opacity=0.5)
            self.play(qx.animate.set_value(b[0]), qy.animate.set_value(b[1]), Create(seg3), Create(shd),
                      Transform(lb2[1], t(f"{L(*b):.2f}", 26, POS).move_to(lb2[1])), run_time=0.4 if k < 5 else 0.2)
        c = self.swap(c, self.cap("더 낮은 곳이 있어도, 근처 골짜기에 멈출 수 있다", POS))
        sub = self.fixed(t("(지역 최솟값)", 22, POS).next_to(c, DOWN, buff=0.1))
        self.play(FadeIn(sub))
        self.wait(1.8)

        # ================= 5) 마무리 =================
        for arc in arcs:
            arc.clear_updaters()
        needle.clear_updaters()
        self.play(FadeOut(keep), FadeOut(lb2), FadeOut(sub))
        end = VGroup(
            t("가중치가 70억 개여도 똑같다", 30, FG),
            t("편미분 70억 개로 나침반을 만들고  →  바늘 방향으로 한 걸음", 26, LORA),
        ).arrange(DOWN, buff=0.15)
        ebg = BackgroundRectangle(end, color=BG, fill_opacity=0.9, buff=0.25)
        grp = VGroup(ebg, end).to_edge(DOWN, buff=0.3)
        self.fixed(grp)
        self.play(FadeIn(grp, shift=UP * 0.1))
        self.wait(2.6)
