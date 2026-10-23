"""씬 0. 편미분 = 하나만 남기고 고정 → 그 방향의 델타. 방향별 델타를 모으면 기울기.

렌더: ./render.sh s00_partial PartialDerivative
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from manim import *

from common.style import ACCENT, BG, FG, LORA, MUTED, NEG, POS, t

X0, Y0 = 1.5, 1.0
ZMAX = 6.0
TAN = "#FF5C5C"
YCOL = "#B48CFF"     # y 방향 색


def f(x, y):
    return 0.15 * x * x + 0.25 * y * y + 0.2 * x * y + 0.5


def fx(x, y):
    return 0.3 * x + 0.2 * y


def fy(x, y):
    return 0.5 * y + 0.2 * x


class PartialDerivative(ThreeDScene):
    # ---------- 화면 고정 텍스트 헬퍼 ----------
    def fixed(self, m):
        self.add_fixed_in_frame_mobjects(m)
        self.remove(m)
        return m

    def cap(self, s, color=FG):
        return self.fixed(t(s, 32, color).to_edge(UP, buff=0.3))

    def swap(self, old, new, **kw):
        anims = [FadeIn(new)]
        if old is not None:
            anims.insert(0, FadeOut(old))
        self.play(*anims, run_time=0.6, **kw)
        return new

    def construct(self):
        self.set_camera_orientation(phi=68 * DEGREES, theta=-50 * DEGREES, zoom=0.72, frame_center=[0, 0, 0.6])

        ax = ThreeDAxes(x_range=[-3, 3, 1], y_range=[-3, 3, 1], z_range=[0, ZMAX, 1],
                        x_length=6, y_length=6, z_length=3.6,
                        axis_config=dict(color=MUTED, stroke_width=1.5, include_ticks=False),
                        tips=False)
        lx = MathTex("x", color=FG).move_to(ax.c2p(3.4, 0, 0))
        ly = MathTex("y", color=FG).move_to(ax.c2p(0, 3.4, 0))
        lz = MathTex("z", color=FG).move_to(ax.c2p(-0.35, 0, ZMAX - 0.3))
        self.add_fixed_orientation_mobjects(lx, ly, lz)
        self.remove(lx, ly, lz)

        surf = Surface(lambda u, v: ax.c2p(u, v, f(u, v)),
                       u_range=[-3, 3], v_range=[-3, 3], resolution=(24, 24),
                       fill_opacity=0.6, stroke_width=0.4, stroke_color="#5A6274")
        surf.set_fill_by_value(axes=ax, colorscale=[("#1F3A68", 0), ("#2E6FB0", 2), ("#2BD9A0", 4.5), (ACCENT, 6)], axis=2)

        # ---------- 1) 곡면 ----------
        cap = self.cap("z = f(x, y)  :  변수 2개, 출력 1개")
        formula = self.fixed(MathTex(r"z = 0.15x^2 + 0.25y^2 + 0.2xy + 0.5", font_size=34, color=MUTED)
                             .to_corner(DL, buff=0.4))
        self.play(FadeIn(cap), Create(ax), FadeIn(lx), FadeIn(ly), FadeIn(lz))
        self.play(Create(surf), FadeIn(formula), run_time=2.2)
        self.begin_ambient_camera_rotation(rate=0.06)
        self.wait(1.0)
        cap = self.swap(cap, self.cap("x, y = 가중치,   z = 손실  이라고 생각하자", ACCENT))
        self.wait(1.4)
        self.stop_ambient_camera_rotation()

        # ---------- 2) 한 점, 방향마다 다른 기울기 ----------
        P = ax.c2p(X0, Y0, f(X0, Y0))
        dot = Dot3D(P, radius=0.09, color=FG)
        cap = self.swap(cap, self.cap("이 점에서 기울기는?  방향마다 다르다"))
        self.play(FadeIn(dot, scale=0.5))

        ang = ValueTracker(0.0)

        def dir_line():
            a = ang.get_value()
            c, s = np.cos(a), np.sin(a)
            slope = fx(X0, Y0) * c + fy(X0, Y0) * s
            d = 1.3
            return Line(ax.c2p(X0 - d * c, Y0 - d * s, f(X0, Y0) - d * slope),
                        ax.c2p(X0 + d * c, Y0 + d * s, f(X0, Y0) + d * slope),
                        color=TAN, stroke_width=5)

        spin = always_redraw(dir_line)
        self.add(spin)
        self.play(ang.animate.set_value(TAU), run_time=4, rate_func=linear)
        self.remove(spin)
        self.wait(0.3)

        # ---------- 3) y 고정 → 단면 ----------
        yv = ValueTracker(Y0)

        def y_plane():
            y0 = yv.get_value()
            return Polygon(ax.c2p(-3, y0, 0), ax.c2p(3, y0, 0), ax.c2p(3, y0, ZMAX), ax.c2p(-3, y0, ZMAX),
                           stroke_color=ACCENT, stroke_width=1.5, fill_color=ACCENT, fill_opacity=0.15)

        def y_curve():
            y0 = yv.get_value()
            return ParametricFunction(lambda s: ax.c2p(s, y0, min(f(s, y0), ZMAX)), t_range=[-3, 3],
                                      color=ACCENT, stroke_width=6)

        def y_tan():
            y0 = yv.get_value()
            z0, k, d = f(X0, y0), fx(X0, y0), 1.4
            return Line(ax.c2p(X0 - d, y0, z0 - d * k), ax.c2p(X0 + d, y0, z0 + d * k), color=TAN, stroke_width=5)

        def y_dot():
            y0 = yv.get_value()
            return Dot3D(ax.c2p(X0, y0, f(X0, y0)), radius=0.09, color=FG)

        cap = self.swap(cap, self.cap("y = 1 로 고정하면?", ACCENT))
        plane = always_redraw(y_plane)
        self.play(FadeIn(plane))
        curve = always_redraw(y_curve)
        self.play(Create(curve), run_time=1.2)
        cap = self.swap(cap, self.cap("곡면이 곡선 하나로 잘린다  →  x만 남은 1변수 함수", ACCENT))
        self.wait(0.6)

        # 옆에서 보기
        self.play(surf.animate.set_fill(opacity=0.12).set_stroke(opacity=0.15), run_time=0.8)
        self.move_camera(phi=90 * DEGREES, theta=-90 * DEGREES, zoom=0.85, frame_center=[0, 0, 0.8], run_time=2.2)
        self.remove(dot)
        ydot = always_redraw(y_dot)
        self.add(ydot)
        tan = always_redraw(y_tan)
        self.play(Create(tan))
        cap = self.swap(cap, self.cap("이 곡선을 x로 미분  =  편미분 ∂z/∂x", ACCENT))
        rd = self.fixed(MathTex(r"\frac{\partial z}{\partial x}\Big|_{(1.5,\,1)} = 0.65",
                                font_size=40, color=TAN).to_corner(UR, buff=0.5).shift(DOWN * 0.6))
        self.play(FadeIn(rd))

        # Δx 삼각형
        dx = 1.0
        z0 = f(X0, Y0)
        A_ = ax.c2p(X0, Y0, z0)
        B_ = ax.c2p(X0 + dx, Y0, z0)
        C_ = ax.c2p(X0 + dx, Y0, z0 + fx(X0, Y0) * dx)
        run_l = Line(A_, B_, color=FG, stroke_width=3)
        rise_l = Line(B_, C_, color=TAN, stroke_width=5)
        lab_dx = MathTex(r"\Delta x", font_size=34, color=FG).move_to(ax.c2p(X0 + dx / 2, Y0, z0 - 0.45))
        lab_dz = MathTex(r"\Delta z \approx 0.65\,\Delta x", font_size=34, color=TAN).move_to(ax.c2p(X0 + dx + 1.6, Y0, z0 + 0.25))
        self.add_fixed_orientation_mobjects(lab_dx, lab_dz)
        self.remove(lab_dx, lab_dz)
        self.play(Create(run_l), FadeIn(lab_dx))
        self.play(Create(rise_l), FadeIn(lab_dz))
        cap = self.swap(cap, self.cap("x 방향으로만 Δx 가면, z는 약 0.65 × Δx 변한다", ACCENT))
        self.wait(1.6)
        self.play(*[FadeOut(m) for m in [run_l, rise_l, lab_dx, lab_dz]])

        # ---------- 4) 다른 y → 다른 단면, 같은 방법 ----------
        self.move_camera(phi=68 * DEGREES, theta=-50 * DEGREES, zoom=0.72, frame_center=[0, 0, 0.6], run_time=2.0)
        self.play(surf.animate.set_fill(opacity=0.45).set_stroke(opacity=0.5), run_time=0.6)
        cap = self.swap(cap, self.cap("y 값이 다르면?  단면도, 기울기도 다르다", ACCENT))
        for yy in [-2.0, 0.0, 2.0, Y0]:
            k = fx(X0, yy)
            new_rd = self.fixed(MathTex(r"\frac{\partial z}{\partial x}\Big|_{y=" + f"{yy:g}" + r"} = " + f"{k:.2f}",
                                        font_size=40, color=TAN).to_corner(UR, buff=0.5).shift(DOWN * 0.6))
            self.play(yv.animate.set_value(yy), FadeOut(rd), FadeIn(new_rd), run_time=1.4)
            rd = new_rd
            self.wait(0.5)
        cap = self.swap(cap, self.cap("그래도 방법은 같다:  자르고 → 1변수로 미분", ACCENT))
        self.wait(1.2)

        # 고정 값 상태로 정지
        y_static = VGroup(y_plane(), y_curve(), y_tan())
        self.remove(plane, curve, tan, ydot)
        self.add(y_static, dot)
        self.play(y_static[0].animate.set_fill(opacity=0.04).set_stroke(opacity=0.3), FadeOut(rd))

        # ---------- 5) x 고정 → y 방향의 델타 ----------
        xplane = Polygon(ax.c2p(X0, -3, 0), ax.c2p(X0, 3, 0), ax.c2p(X0, 3, ZMAX), ax.c2p(X0, -3, ZMAX),
                         stroke_color=YCOL, stroke_width=1.5, fill_color=YCOL, fill_opacity=0.15)
        xcurve = ParametricFunction(lambda s: ax.c2p(X0, s, min(f(X0, s), ZMAX)), t_range=[-3, 3],
                                    color=YCOL, stroke_width=6)
        d = 1.4
        xtan = Line(ax.c2p(X0, Y0 - d, z0 - d * fy(X0, Y0)), ax.c2p(X0, Y0 + d, z0 + d * fy(X0, Y0)),
                    color=TAN, stroke_width=5)
        cap = self.swap(cap, self.cap("이번엔 x = 1.5 로 고정  →  y 방향의 델타", YCOL))
        self.play(FadeIn(xplane))
        self.play(Create(xcurve), run_time=1.0)
        self.play(Create(xtan))
        rd2 = self.fixed(MathTex(r"\frac{\partial z}{\partial y} = 0.80", font_size=40, color=YCOL)
                         .to_corner(UR, buff=0.5).shift(DOWN * 0.6))
        rd1 = self.fixed(MathTex(r"\frac{\partial z}{\partial x} = 0.65", font_size=40, color=ACCENT)
                         .next_to(rd2, DOWN, buff=0.25, aligned_edge=RIGHT))
        self.play(FadeIn(rd2), FadeIn(rd1))
        self.wait(1.0)

        # ---------- 6) 델타를 더한다: 접평면 ----------
        self.play(FadeOut(xplane), FadeOut(y_static), FadeOut(xcurve), FadeOut(xtan), FadeOut(formula))
        cap = self.swap(cap, self.cap("점 근처를 확대하면  →  곡면 ≈ 평평한 판"))
        h = 1.4
        gx, gy = fx(X0, Y0), fy(X0, Y0)
        tplane = Polygon(*[ax.c2p(X0 + a, Y0 + b, z0 + gx * a + gy * b) for a, b in [(-h, -h), (h, -h), (h, h), (-h, h)]],
                         stroke_color=FG, stroke_width=2, fill_color=FG, fill_opacity=0.22)
        self.play(FadeIn(tplane), surf.animate.set_fill(opacity=0.12).set_stroke(opacity=0.12))
        self.move_camera(phi=62 * DEGREES, theta=-30 * DEGREES, zoom=1.9, frame_center=ax.c2p(X0 + 0.5, Y0 + 0.5, z0 + 0.4), run_time=2.0)

        D = 1.1
        p0 = np.array([X0, Y0, z0])
        p1 = p0 + np.array([D, 0, gx * D])
        p2 = p1 + np.array([0, D, gy * D])
        s1 = Line(ax.c2p(*p0), ax.c2p(*p1), color=ACCENT, stroke_width=9)
        s2 = Line(ax.c2p(*p1), ax.c2p(*p2), color=YCOL, stroke_width=9)
        diag = DashedLine(ax.c2p(*p0), ax.c2p(*p2), color=FG, stroke_width=6, dash_length=0.12)
        cap = self.swap(cap, self.cap("x로 한 칸 → y로 한 칸  =  대각선으로 한 번"))
        self.play(Create(s1), run_time=0.9)
        self.play(Create(s2), run_time=0.9)
        self.play(Create(diag), run_time=0.9)

        total = self.fixed(MathTex(r"\Delta z", r"\approx", r"\frac{\partial z}{\partial x}\Delta x", "+",
                                   r"\frac{\partial z}{\partial y}\Delta y", font_size=44)
                           .to_edge(DOWN, buff=0.5))
        total[2].set_color(ACCENT)
        total[4].set_color(YCOL)
        self.play(FadeIn(total))
        cap = self.swap(cap, self.cap("방향별 델타를 더하면  =  어느 방향이든 변화량"))
        self.wait(2.0)

        # ---------- 7) 반대로 가면 반드시 내려간다 ----------
        self.play(*[FadeOut(m) for m in [s1, s2, diag, tplane]])
        self.play(surf.animate.set_fill(opacity=0.07).set_stroke(opacity=0.08), dot.animate.set_opacity(1))
        self.move_camera(phi=35 * DEGREES, theta=-70 * DEGREES, zoom=1.1, frame_center=ax.c2p(X0, Y0, 0.5), run_time=2.0)
        base = np.array([X0, Y0, 0])
        k = 2.0
        gxv = Arrow3D(ax.c2p(*base), ax.c2p(X0 + gx * k, Y0, 0), color=ACCENT, thickness=0.03)
        gyv = Arrow3D(ax.c2p(*base), ax.c2p(X0, Y0 + gy * k, 0), color=YCOL, thickness=0.03)
        grad = Arrow3D(ax.c2p(*base), ax.c2p(X0 + gx * k, Y0 + gy * k, 0), color=FG, thickness=0.04)
        down = Arrow3D(ax.c2p(*base), ax.c2p(X0 - gx * k, Y0 - gy * k, 0), color=LORA, thickness=0.045)
        drop = DashedLine(ax.c2p(X0, Y0, z0), ax.c2p(*base), color=MUTED, stroke_width=2)

        def lab3d(txt, col, pos):
            m = t(txt, 22, col).move_to(pos)
            self.add_fixed_orientation_mobjects(m)
            self.remove(m)
            return m

        l_gx = lab3d("x 방향 0.65", ACCENT, ax.c2p(X0 + gx * k + 0.55, Y0 - 0.35, 0))
        l_gy = lab3d("y 방향 0.80", YCOL, ax.c2p(X0 - 0.55, Y0 + gy * k + 0.25, 0))
        l_g = lab3d("기울기 ∇z (오르막)", FG, ax.c2p(X0 + gx * k + 0.9, Y0 + gy * k + 0.3, 0))
        l_d = lab3d("−∇z (내리막)", LORA, ax.c2p(X0 - gx * k - 1.0, Y0 - gy * k + 0.45, 0))

        def panel(*mobs):
            body = VGroup(*mobs).arrange(DOWN, buff=0.18)
            bg = BackgroundRectangle(body, color=BG, fill_opacity=0.88, buff=0.22)
            return self.fixed(VGroup(bg, body).to_edge(DOWN, buff=0.9))

        cap = self.swap(cap, self.cap("방향별 기울기를 모은 화살표  =  기울기 ∇z"))
        self.play(Create(drop), FadeIn(gxv), FadeIn(gyv), FadeIn(l_gx), FadeIn(l_gy))
        self.play(FadeIn(grad), FadeIn(l_g))
        p_now = panel(MathTex(r"\nabla z = \left(\frac{\partial z}{\partial x},\ \frac{\partial z}{\partial y}\right) = (0.65,\ 0.80)",
                              font_size=36))
        self.play(FadeOut(total), FadeIn(p_now))
        self.wait(1.2)

        # 반대 방향
        cap = self.swap(cap, self.cap("기울기는 오르막을 가리킨다  →  반대로 가면 내리막", LORA))
        self.play(FadeIn(down), FadeIn(l_d))
        self.wait(0.8)

        # (1) 기울기 × 거리 = 높이
        cap = self.swap(cap, self.cap("기울기 × 움직인 거리  =  올라간 높이"))
        nxt = panel(
            MathTex(r"\Delta z", r"\approx", r"0.65", r"\cdot\Delta x", "+", r"0.80", r"\cdot\Delta y", font_size=40),
            t("x로 Δx 걸으면 0.65·Δx 오르고, y로 Δy 걸으면 0.80·Δy 오른다  →  더한다", 24, MUTED),
        )
        nxt[1][0][2].set_color(ACCENT)
        nxt[1][0][5].set_color(YCOL)
        self.play(FadeOut(p_now), FadeIn(nxt))
        p_now = nxt
        self.wait(2.2)

        # (2) 걸음 = 기울기 × 상수(−η)
        cap = self.swap(cap, self.cap("걸음은 어떻게 정할까?  기울기에 같은 상수를 곱한다", ACCENT))
        nxt = panel(
            MathTex(r"\Delta x = ", r"-\eta", r"\times 0.65 \qquad \Delta y = ", r"-\eta", r"\times 0.80", font_size=40),
            t("η (에타) = 모든 방향에 똑같이 곱하는 상수 = 학습률", 26, ACCENT),
            t("−  :  기울기 반대(내리막)로   ·   가파른 방향일수록 더 많이 걷는다", 24, MUTED),
        )
        nxt[1][0][1].set_color(ACCENT)
        nxt[1][0][3].set_color(ACCENT)
        self.play(FadeOut(p_now), FadeIn(nxt))
        p_now = nxt
        self.wait(2.8)

        # 숫자 예시
        cap = self.swap(cap, self.cap("η = 0.1 로 걸어보면", ACCENT))
        nxt = panel(
            MathTex(r"\Delta x = -0.065 \qquad \Delta y = -0.080", font_size=38),
            MathTex(r"\Delta z \approx 0.65\times(-0.065) + 0.80\times(-0.080) = -0.106", font_size=36),
        )
        nxt[1][1].set_color(LORA)
        self.play(FadeOut(p_now), FadeIn(nxt))
        p_now = nxt
        self.play(dot.animate.move_to(ax.c2p(X0 - 0.065 * 6, Y0 - 0.08 * 6, f(X0 - 0.39, Y0 - 0.48))), run_time=1.0)
        cap = self.swap(cap, self.cap("z가 줄었다  →  내려갔다", LORA))
        self.wait(1.6)

        self.wait(0.6)
        self.play(FadeOut(l_gx), FadeOut(l_gy), FadeOut(l_g), FadeOut(l_d))

        # ---------- 8) 일반화 ----------
        self.play(*[FadeOut(m) for m in self.mobjects if m not in (cap,)], run_time=0.8)
        cap = self.swap(cap, self.cap("가중치가 늘어나면?"))
        rows = VGroup(
            VGroup(t("가중치 2개", 30, FG), t("하나 고정  →  단면은 곡선", 30, MUTED)),
            VGroup(t("가중치 3개", 30, FG), t("둘 고정  →  역시 곡선 (그림만 못 그림)", 30, MUTED)),
            VGroup(t("가중치 70억 개", 30, ACCENT), t("나머지 전부 고정  →  하나씩 델타", 30, MUTED)),
        )
        for r in rows:
            r.arrange(RIGHT, buff=0.6)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.5).shift(UP * 0.3)
        self.fixed(rows)
        for r in rows:
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.7)
        end = self.fixed(VGroup(
            t("방향별 델타 70억 개를 모은 것 = 기울기", 32, LORA),
            t("70억 개도 컴퓨터가 한 번에 계산해 준다", 28, FG),
        ).arrange(DOWN, buff=0.2).to_edge(DOWN, buff=0.6))
        self.play(FadeIn(end, shift=UP * 0.15))
        self.wait(3.0)
