#!/usr/bin/env python3
"""RETL hero banner renderer.

Renders a seamless looping animation (1200x400 logical px) with Pillow + NumPy.
  python render_hero.py frames   -> PNG frames in ./frames (then build GIF with ffmpeg, see build_gif.sh)
  python render_hero.py still    -> ../assets/hero-fallback.png (2400x800)
Requires: Pillow, numpy. Fonts: Inter + DejaVu Sans Mono (edit the paths below if needed).
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1200, 400
FRAMES, FPS = 96, 20

INTER = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

BLUE, VIOLET, CYAN = (59, 130, 246), (139, 92, 246), (34, 211, 238)
LIGHT, MUTED, GREEN = (226, 232, 245), (125, 140, 172), (74, 222, 128)
PANEL = (10, 14, 30)

TAU = 2 * math.pi
clip = lambda v, a=0.0, b=1.0: max(a, min(b, v))


class Renderer:
    def __init__(self, S):
        self.S = S
        self.fonts = {}
        rs = np.random.RandomState(7)
        self.parts = [(rs.uniform(0, W), rs.uniform(0, H), rs.uniform(0.8, 2.2),
                       [BLUE, VIOLET, CYAN][rs.randint(3)], rs.uniform(0, 1),
                       rs.randint(1, 3), rs.uniform(0.35, 0.9)) for _ in range(38)]
        self._static()

    # ---------- helpers ----------
    def f(self, name, size):
        k = (name, size)
        if k not in self.fonts:
            path = MONO if name == "mono" else INTER.format(name)
            self.fonts[k] = ImageFont.truetype(path, int(round(size * self.S)))
        return self.fonts[k]

    def P(self, v):
        return int(round(v * self.S))

    def text_tracked(self, d, x, y, s, font, fill, track=0.0, anchor="l"):
        """Draw text with letter spacing. x,y in 1x units; anchor l|m (horizontal), vertically middle."""
        S = self.S
        widths = [font.getlength(c) for c in s]
        total = sum(widths) + track * S * (len(s) - 1)
        cx = x * S - (total / 2 if anchor == "m" else 0)
        for c, w in zip(s, widths):
            d.text((cx, y * S), c, font=font, fill=fill, anchor="lm")
            cx += w + track * S
        return total / S

    # ---------- static layers ----------
    def _static(self):
        S = self.S
        w, h = W * S, H * S
        yy = np.linspace(0, 1, h)[:, None]
        xx = np.linspace(0, 1, w)[None, :]
        bg = np.zeros((h, w, 3), np.float32)
        top, bot = np.array([4, 6, 14], np.float32), np.array([9, 14, 32], np.float32)
        bg[:] = top + (bot - top) * yy[:, :, None]

        def glow(cx, cy, rx, ry, col, amt):
            g = np.exp(-(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2))
            bg[:] += g[:, :, None] * np.array(col, np.float32) * amt

        glow(0.14, 0.25, 0.22, 0.6, VIOLET, 0.16)
        glow(0.88, 0.80, 0.24, 0.6, BLUE, 0.17)
        glow(0.50, 0.46, 0.28, 0.55, (70, 70, 235), 0.14)
        self.bg = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8), "RGB")

        # grid fade mask (stronger towards bottom, softer at edges)
        fade = (0.25 + 0.75 * yy) * np.clip(1.15 - 1.1 * np.abs(xx - 0.5), 0, 1)
        self.gridfade = fade.astype(np.float32)

        # RETL logo (real brand asset) + glow
        here = os.path.dirname(os.path.abspath(__file__))
        assets = os.path.join(here, "..", "assets")
        logo = Image.open(os.path.join(assets, "logo-horizontal.png")).convert("RGBA")
        lw = self.P(350)
        logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
        self.logo_rgb = np.asarray(logo.convert("RGB"), np.float32)
        self.logo_a = logo.getchannel("A")
        self.logo_pos = (self.P(600) - lw // 2, self.P(166) - logo.height // 2)
        self.logo_w = lw
        gl = Image.new("L", (w, h), 0)
        gl.paste(self.logo_a, self.logo_pos)
        self.title_glow_np = np.asarray(gl.filter(ImageFilter.GaussianBlur(24 * S)), np.float32) / 255.0
        av = Image.open(os.path.join(assets, "me-avatar.png")).convert("RGBA")
        self.avatar = av.resize((self.P(80), self.P(80)), Image.LANCZOS)

    # ---------- primitives ----------
    def panel(self, d, x, y, w, h, title, accent, a=1.0):
        P = self.P
        for i, al in ((7, 10), (4, 14), (2, 18)):  # soft shadow
            d.rounded_rectangle([P(x - i), P(y - i + 4), P(x + w + i), P(y + h + i + 4)],
                                radius=P(10 + i), fill=(0, 0, 0, int(al * a)))
        d.rounded_rectangle([P(x), P(y), P(x + w), P(y + h)], radius=P(10),
                            fill=PANEL + (int(228 * a),), outline=accent + (int(105 * a),), width=max(1, P(1)))
        d.line([P(x + 1), P(y + 24), P(x + w - 1), P(y + 24)], fill=accent + (int(45 * a),), width=max(1, P(1)))
        for i, c in enumerate(((255, 95, 109), (255, 189, 68), (61, 220, 132))):
            d.ellipse([P(x + 11 + i * 12 - 3), P(y + 12 - 3), P(x + 11 + i * 12 + 3), P(y + 12 + 3)],
                      fill=c + (int(170 * a),))
        d.text((P(x + w - 12), P(y + 12)), title, font=self.f("mono", 9.5), fill=MUTED + (int(230 * a),), anchor="rm")

    def typed(self, d, lines, x, y, lh, nchars, font, a, u, hl=False, hlbox=None):
        """Draw segmented lines revealed up to nchars; blinking cursor at the end."""
        P, left, cur = self.P, nchars, (x, y)
        for li, segs in enumerate(lines):
            cx, cy = x, y + li * lh
            cur = (cx, cy)
            for text, col in segs:
                if left <= 0:
                    break
                part = text[:left]
                left -= len(text)
                d.text((P(cx), P(cy)), part, font=font, fill=col + (int(255 * a),), anchor="lm")
                cx += font.getlength(part) / self.S
                cur = (cx, cy)
            if left <= 0:
                break
        if int(u * 12) % 2 == 0 and a > 0.3:
            d.rectangle([P(cur[0] + 1), P(cur[1] - 6), P(cur[0] + 4.5), P(cur[1] + 6)], fill=CYAN + (int(230 * a),))
        return cur

    # ---------- frame ----------
    def frame(self, u):
        S, P = self.S, self.P
        img = self.bg.copy()
        w, h = W * S, H * S

        # moving grid
        sp = 40
        g = Image.new("L", (w, h), 0)
        gd = ImageDraw.Draw(g)
        for k in range(-1, W // sp + 2):
            gd.line([P(k * sp), 0, P(k * sp), h], fill=255, width=max(1, S // 2 + 1))
        off = u * sp
        for k in range(-1, H // sp + 2):
            yv = k * sp + off
            gd.line([0, P(yv), w, P(yv)], fill=255, width=max(1, S // 2 + 1))
        gm = Image.fromarray((np.asarray(g, np.float32) * self.gridfade * 0.13).astype(np.uint8), "L")
        img.paste(Image.new("RGB", (w, h), (80, 120, 255)), (0, 0), gm)

        # title glow (breathing)
        pulse = 0.55 + 0.15 * math.sin(TAU * u)
        gl = Image.fromarray((self.title_glow_np * 255 * pulse).astype(np.uint8), "L")
        img.paste(Image.new("RGB", (w, h), (92, 80, 250)), (0, 0), gl)

        d = ImageDraw.Draw(img, "RGBA")

        # orbit ring + orbiting accents
        cx, cy, rx, ry = 600, 172, 222, 92
        d.ellipse([P(cx - rx), P(cy - ry), P(cx + rx), P(cy + ry)], outline=BLUE + (38,), width=max(1, P(1)))
        d.ellipse([P(cx - rx + 14), P(cy - ry + 10), P(cx + rx - 14), P(cy + ry - 10)], outline=VIOLET + (22,), width=max(1, P(1)))
        ang = u * 360
        d.arc([P(cx - rx), P(cy - ry), P(cx + rx), P(cy + ry)], ang, ang + 42, fill=CYAN + (190,), width=max(2, P(1.6)))
        d.arc([P(cx - rx), P(cy - ry), P(cx + rx), P(cy + ry)], ang + 180, ang + 214, fill=VIOLET + (190,), width=max(2, P(1.6)))
        ox, oy = cx + rx * math.cos(TAU * u), cy + ry * math.sin(TAU * u)
        for r, al in ((7, 30), (4, 70), (2.2, 255)):
            d.ellipse([P(ox - r), P(oy - r), P(ox + r), P(oy + r)], fill=CYAN + (al,))

        # data-flow connectors (panel -> ring) with travelling pulses
        links = [((338, 95), (cx - rx + 4, cy - 14), 0.0), ((338, 285), (cx - rx + 4, cy + 14), 0.5),
                 ((862, 100), (cx + rx - 4, cy - 14), 0.25), ((862, 285), (cx + rx - 4, cy + 14), 0.75)]
        for (x0, y0), (x1, y1), ph in links:
            mx = (x0 + x1) / 2
            pts = []
            for i in range(25):
                t = i / 24
                bx = (1 - t) ** 3 * x0 + 3 * (1 - t) ** 2 * t * mx + 3 * (1 - t) * t ** 2 * mx + t ** 3 * x1
                by = (1 - t) ** 3 * y0 + 3 * (1 - t) ** 2 * t * y0 + 3 * (1 - t) * t ** 2 * y1 + t ** 3 * y1
                pts.append((P(bx), P(by)))
            d.line(pts, fill=BLUE + (34,), width=max(1, P(1)))
            t = (u + ph) % 1
            px, py = pts[int(t * 24)]
            d.ellipse([px - P(2.2), py - P(2.2), px + P(2.2), py + P(2.2)], fill=CYAN + (230,))
            d.ellipse([px - P(6), py - P(6), px + P(6), py + P(6)], fill=CYAN + (28,))

        # particles
        for x0, y0, sz, col, ph, k, al in self.parts:
            y = (y0 - u * H) % H
            x = x0 + 6 * math.sin(TAU * (u + ph))
            tw = 0.55 + 0.45 * math.sin(TAU * (u * k + ph))
            a = al * tw
            d.ellipse([P(x - sz * 3), P(y - sz * 3), P(x + sz * 3), P(y + sz * 3)], fill=col + (int(22 * a),))
            d.ellipse([P(x - sz), P(y - sz), P(x + sz), P(y + sz)], fill=col + (int(255 * a),))

        # content envelope: fade out near loop end, fade in at start
        env = min(1.0, u / 0.04, (1 - u) / 0.07)
        env = clip(env)
        p = clip((u - 0.04) / 0.62)

        mono = self.f("mono", 10.5)

        # --- profile card (left top)
        bx, by = 40 + 2 * math.cos(TAU * (u + .1)), 22 + 5 * math.sin(TAU * u)
        self.panel(d, bx, by, 300, 150, "profile.retl", VIOLET)
        acx, acy = bx + 62, by + 88
        for r, al in ((50, 26), (47, 40)):
            d.ellipse([P(acx - r), P(acy - r), P(acx + r), P(acy + r)], outline=VIOLET + (al,), width=max(1, P(1)))
        ang = u * 360
        box = [P(acx - 47), P(acy - 47), P(acx + 47), P(acy + 47)]
        d.arc(box, ang, ang + 90, fill=CYAN + (230,), width=max(2, P(2)))
        d.arc(box, ang + 180, ang + 250, fill=VIOLET + (230,), width=max(2, P(2)))
        img.paste(self.avatar, (P(acx - 40), P(acy - 40)), self.avatar)
        d = ImageDraw.Draw(img, "RGBA")
        d.ellipse([P(acx + 27), P(acy + 27), P(acx + 39), P(acy + 39)], fill=PANEL + (255,))
        d.ellipse([P(acx + 29.5), P(acy + 29.5), P(acx + 36.5), P(acy + 36.5)], fill=GREEN + (255,))
        self.text_tracked(d, bx + 122, by + 56, "RETL", self.f("Bold", 19), LIGHT + (int(255 * env),), 3, "l")
        d.text((P(bx + 122), P(by + 78)), "Computer Science", font=self.f("Medium", 11.5), fill=LIGHT + (int(235 * env),), anchor="lm")
        d.text((P(bx + 122), P(by + 94)), "USTP · Cagayan de Oro", font=self.f("Regular", 10), fill=MUTED + (int(235 * env),), anchor="lm")
        px = bx + 122
        for lab, c in (("Python", BLUE), ("AI", VIOLET), ("Web", CYAN)):
            wd = self.f("Medium", 9).getlength(lab) / S + 14
            d.rounded_rectangle([P(px), P(by + 112), P(px + wd), P(by + 130)], radius=P(9),
                                fill=(20, 26, 52, int(220 * env)), outline=c + (int(130 * env),), width=max(1, P(1)))
            d.text((P(px + wd / 2), P(by + 121)), lab, font=self.f("Medium", 9), fill=LIGHT + (int(235 * env),), anchor="mm")
            px += wd + 5

        # --- AI panel (left bottom)
        ax, ay = 60 + 2 * math.cos(TAU * (u + .6)), 196 + 5 * math.sin(TAU * (u + .5))
        self.panel(d, ax, ay, 280, 170, "prompt-pilot", VIOLET)
        d.text((P(ax + 14), P(ay + 38)), "PROMPT", font=self.f("mono", 8.5), fill=MUTED + (int(220 * env),), anchor="lm")
        d.rounded_rectangle([P(ax + 14), P(ay + 47), P(ax + 266), P(ay + 69)], radius=P(5),
                            fill=(20, 26, 52, int(230 * env)), outline=VIOLET + (int(70 * env),), width=max(1, P(1)))
        ptxt = "Summarize this paper in 3 bullets"
        n = int(clip(p / 0.8) * len(ptxt))
        d.text((P(ax + 22), P(ay + 58)), ptxt[:n], font=self.f("mono", 9.5), fill=LIGHT + (int(240 * env),), anchor="lm")
        for i, (lab, base, amp, ph, c1) in enumerate((("Prompt A", .55, .08, 0, BLUE), ("Prompt B", .68, .12, 1.7, VIOLET))):
            yy = ay + 90 + i * 22
            d.text((P(ax + 14), P(yy)), lab, font=self.f("mono", 9), fill=MUTED + (int(230 * env),), anchor="lm")
            d.rounded_rectangle([P(ax + 76), P(yy - 3.5), P(ax + 266), P(yy + 3.5)], radius=P(3.5), fill=(30, 38, 70, int(230 * env)))
            fw = 190 * (base + amp * math.sin(TAU * u + ph)) * clip(p / 0.3 + 0.2)
            d.rounded_rectangle([P(ax + 76), P(yy - 3.5), P(ax + 76 + fw), P(yy + 3.5)], radius=P(3.5), fill=c1 + (int(235 * env),))
        for i in range(14):  # tiny usage histogram
            hh = 4 + 11 * (0.5 + 0.5 * math.sin(TAU * (u + i * 0.07) + i * 1.3))
            xx = ax + 14 + i * 18
            d.rounded_rectangle([P(xx), P(ay + 158 - hh), P(xx + 11), P(ay + 158)], radius=P(2),
                                fill=CYAN + (int((70 + 6 * i) * env),))

        # --- code editor (right top)
        ex, ey = 860 + 2 * math.cos(TAU * (u + .3)), 22 + 5 * math.sin(TAU * (u + .35))
        self.panel(d, ex, ey, 300, 160, "markov.py", BLUE)
        code = [[("def ", VIOLET), ("next_state", BLUE), ("(s, P):", LIGHT)],
                [("    # sample next BP state", MUTED)],
                [("    p = ", LIGHT), ("P", CYAN), ("[s]", LIGHT)],
                [("    return ", VIOLET), ("rng.choice(S, p=p)", LIGHT)],
                [("model = ", LIGHT), ("fit_logistic", BLUE), ("(data)", LIGHT)],
                [("app.", LIGHT), ("run", BLUE), ("()", LIGHT)]]
        tot = sum(len(t) for l in code for t, _ in l)
        nshow = int(clip(p / 0.9) * tot)
        cur = self.typed(d, code, ex + 34, ey + 41, 17, nshow, mono, env, u)
        hl_line = int(round((cur[1] - (ey + 41)) / 17))
        d.rectangle([P(ex + 2), P(ey + 41 + hl_line * 17 - 8), P(ex + 298), P(ey + 41 + hl_line * 17 + 8)], fill=BLUE + (int(26 * env),))
        for i in range(len(code)):
            d.text((P(ex + 14), P(ey + 41 + i * 17)), str(i + 1), font=self.f("mono", 9), fill=MUTED + (int(150 * env),), anchor="lm")

        # --- research panel (right bottom)
        rx0, ry0 = 840 + 2 * math.cos(TAU * (u + .8)), 200 + 5 * math.sin(TAU * (u + .8))
        self.panel(d, rx0, ry0, 300, 168, "markov-bp.model", CYAN)
        nodes = [(rx0 + 60, ry0 + 78, "Normal"), (rx0 + 150, ry0 + 52, "Elevated"), (rx0 + 240, ry0 + 78, "High")]
        for (x0, y0, _), (x1, y1, _) in zip(nodes, nodes[1:] + nodes[:1]):
            d.line([P(x0), P(y0), P(x1), P(y1)], fill=CYAN + (int(50 * env),), width=max(1, P(1)))
        t3 = (u * 3) % 3
        leg, lt = int(t3) % 3, t3 - int(t3)
        a_, b_ = nodes[leg], nodes[(leg + 1) % 3]
        dx, dy = a_[0] + (b_[0] - a_[0]) * lt, a_[1] + (b_[1] - a_[1]) * lt
        for i, (x0, y0, lab) in enumerate(nodes):
            near = clip(1 - min(abs(t3 - i), abs(t3 - i - 3), abs(t3 - i + 3)) * 2.2)
            r = 7 + 2 * near
            d.ellipse([P(x0 - r - 5), P(y0 - r - 5), P(x0 + r + 5), P(y0 + r + 5)], fill=VIOLET + (int(40 * near * env),))
            d.ellipse([P(x0 - r), P(y0 - r), P(x0 + r), P(y0 + r)], fill=(16, 22, 48, int(240 * env)),
                      outline=(CYAN if near > .3 else BLUE) + (int(220 * env),), width=max(1, P(1.4)))
            d.text((P(x0), P(y0 + (-19 if i == 1 else 20))), lab, font=self.f("Medium", 9), fill=MUTED + (int(235 * env),), anchor="mm")
        d.ellipse([P(dx - 3), P(dy - 3), P(dx + 3), P(dy + 3)], fill=LIGHT + (int(255 * env),))
        d.ellipse([P(dx - 8), P(dy - 8), P(dx + 8), P(dy + 8)], fill=CYAN + (int(45 * env),))
        # sparkline
        sx0, sx1, sy0, sy1 = rx0 + 16, rx0 + 284, ry0 + 118, ry0 + 156
        pts = []
        for i in range(61):
            q = i / 60
            v = 0.5 + 0.28 * math.sin(TAU * (2 * q - u)) + 0.12 * math.sin(TAU * (5 * q + u))
            pts.append((P(sx0 + (sx1 - sx0) * q), P(sy1 - (sy1 - sy0) * v)))
        d.polygon(pts + [(P(sx1), P(sy1)), (P(sx0), P(sy1))], fill=BLUE + (int(26 * env),))
        d.line(pts, fill=CYAN + (int(220 * env),), width=max(2, P(1.5)), joint="curve")

        # ---- centre identity ----
        # live status line
        blink = 0.5 + 0.5 * math.sin(TAU * u * 2)
        stw = self.text_tracked(d, 612, 48, "RETL.WORKSPACE  ·  ONLINE", self.f("mono", 9.5), MUTED + (225,), 1.6, "m")
        sx = 612 - stw / 2 - 12
        d.ellipse([P(sx - 6), P(48 - 6), P(sx + 6), P(48 + 6)], fill=GREEN + (int(40 + 50 * blink),))
        d.ellipse([P(sx - 2.6), P(48 - 2.6), P(sx + 2.6), P(48 + 2.6)], fill=GREEN + (255,))

        # logo with a travelling light sweep
        lh_, lw_ = self.logo_rgb.shape[:2]
        sweep = u * (lw_ + 2 * 90 * S) - 90 * S
        band = np.exp(-(((np.arange(lw_) - sweep) / (50 * S)) ** 2))[None, :, None] * 70
        lit = np.clip(self.logo_rgb + band, 0, 255).astype(np.uint8)
        img.paste(Image.fromarray(lit, "RGB"), self.logo_pos, self.logo_a)

        d = ImageDraw.Draw(img, "RGBA")
        d.text((P(600), P(247)), "Rheil Evans T. Lunio", font=self.f("Medium", 21), fill=LIGHT + (245,), anchor="mm")
        d.text((P(600), P(275)), "Student Developer  ·  Researcher  ·  Aspiring Software Engineer",
               font=self.f("Regular", 13), fill=MUTED + (245,), anchor="mm")

        # chips
        chips = [("Software", BLUE), ("AI", VIOLET), ("Web", CYAN), ("Research", BLUE), ("UI/UX", VIOLET)]
        cf = self.f("Medium", 10)
        widths = [cf.getlength(n) / S + 26 for n, _ in chips]
        gap, tot = 8, sum(widths) + 8 * (len(chips) - 1)
        cxp = 600 - tot / 2
        for i, ((n, c), wd) in enumerate(zip(chips, widths)):
            yy = 322 + 2.5 * math.sin(TAU * (u + i * 0.13))
            d.rounded_rectangle([P(cxp), P(yy - 11), P(cxp + wd), P(yy + 11)], radius=P(11),
                                fill=(14, 20, 44, 215), outline=c + (120,), width=max(1, P(1)))
            d.ellipse([P(cxp + 9 - 2.5), P(yy - 2.5), P(cxp + 9 + 2.5), P(yy + 2.5)], fill=c + (255,))
            d.text((P(cxp + 17), P(yy)), n, font=cf, fill=LIGHT + (235,), anchor="lm")
            cxp += wd + gap

        out = img if S == 2 else img
        return out


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "frames"
    here = os.path.dirname(os.path.abspath(__file__))
    if mode == "still":
        r = Renderer(2)
        r.frame(0.42).save(os.path.join(here, "..", "assets", "hero-fallback.png"), optimize=True)
        print("saved still")
    else:
        r = Renderer(2)
        outd = os.path.join(here, "frames")
        os.makedirs(outd, exist_ok=True)
        for i in range(FRAMES):
            im = r.frame(i / FRAMES).resize((W, H), Image.LANCZOS)
            im.save(os.path.join(outd, f"f{i:03d}.png"))
        print("frames done")


if __name__ == "__main__":
    main()
