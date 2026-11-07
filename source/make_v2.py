#!/usr/bin/env python3
"""Generates the intro + featured-project SVGs in ../assets  (run: python3 make_v2.py).

Reuses the look and helpers from make_svgs.py. Every SVG is self-contained and animated with
SMIL/CSS only, so GitHub renders it when used as <img src="assets/....svg">.
"""
import base64, io, math, os, random, textwrap
from PIL import Image
import make_svgs as M

BLUE, VIOLET, CYAN, INK, MUTED, LINE = M.BLUE, M.VIOLET, M.CYAN, M.INK, M.MUTED, M.LINE
OUT = M.OUT

EXTRA_CSS = """
.bob{animation:bob 5s ease-in-out infinite}
.bob2{animation:bob 6.5s ease-in-out infinite reverse}
.nudge{animation:nudge 1.8s ease-in-out infinite}
.wave{transform-box:view-box;animation:wave 2.4s ease-in-out infinite}
.orbit{transform-box:view-box;animation:spin 28s linear infinite}
.orbitr{transform-box:view-box;animation:spin 40s linear infinite reverse}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-9px)}}
@keyframes nudge{0%,100%{transform:translateX(0)}50%{transform:translateX(7px)}}
@keyframes wave{0%,60%,100%{transform:rotate(0)}10%{transform:rotate(16deg)}20%{transform:rotate(-8deg)}30%{transform:rotate(14deg)}40%{transform:rotate(-4deg)}50%{transform:rotate(10deg)}}
@media (prefers-reduced-motion: reduce){.bob,.bob2,.nudge,.wave,.orbit,.orbitr{animation:none}}
"""


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def head(w, h, title):
    return [M.svg_open(w, h, title), M.defs(w, h), f"<style>{EXTRA_CSS}</style>"]


def jpeg_uri(name, width, quality=82):
    im = Image.open(os.path.join(OUT, name)).convert("RGB")
    im = im.resize((width, int(im.height * width / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode(), im.size


# ======================================================================= intro banner
def intro():
    w, h = 1200, 170
    o = head(w, h, "Hi, I'm Rheil")
    o.append('<defs><linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="-500" y1="0" x2="0" y2="0" spreadMethod="reflect">'
             f'<stop offset="0" stop-color="{INK}"/><stop offset="0.35" stop-color="{CYAN}"/><stop offset="0.7" stop-color="{VIOLET}"/><stop offset="1" stop-color="{INK}"/>'
             '<animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="1000 0" dur="6s" repeatCount="indefinite"/></linearGradient>'
             '<clipPath id="reveal"><rect x="50" y="0" width="0" height="170"><animate attributeName="width" values="0;640;640" keyTimes="0;0.25;1" dur="1.6s" fill="freeze"/></rect></clipPath></defs>')
    o.append(M.backdrop(w, h, 31, 22, corners=False))
    o.append(f'<text class="m" x="64" y="52" font-size="15" letter-spacing="6" fill="{MUTED}">&gt; HELLO, WORLD</text>')
    o.append(f'<g clip-path="url(#reveal)"><text class="t" x="60" y="124" font-size="68" font-weight="800" fill="url(#shine)" filter="url(#glowsm)">Hi, I\'m Rheil</text></g>')
    o.append(f'<rect x="64" y="140" width="520" height="3" rx="1.5" fill="url(#acc)"><animate attributeName="width" values="0;520;520;0" keyTimes="0;0.2;0.8;1" dur="7s" repeatCount="indefinite"/></rect>')
    # waving hand (vector) - pivots from the wrist with explicit SMIL rotation
    hx, hy = 655, 142
    o.append(f'<g transform="translate({hx},{hy})"><g>'
             '<animateTransform attributeName="transform" type="rotate" values="0;18;-8;16;-4;12;0;0" keyTimes="0;0.08;0.16;0.24;0.32;0.4;0.5;1" dur="3s" repeatCount="indefinite"/>'
             f'<g fill="none" stroke="url(#acc)" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" filter="url(#glowsm)" transform="translate(-40,-101) scale(1.1)">'
             '<path d="M14 62 L4 44 Q1 38 8 36 Q13 35 17 41 L22 48"/>'
             '<path d="M22 48 L16 14 Q15 6 22 6 Q28 6 29 13 L33 44"/>'
             '<path d="M33 44 L36 8 Q37 1 43 2 Q49 3 48 10 L45 44"/>'
             '<path d="M45 44 L52 14 Q54 8 60 10 Q65 12 63 18 L56 48"/>'
             '<path d="M56 48 Q74 54 66 76 Q58 94 36 92 Q18 90 14 62"/></g></g></g>')
    # floating code symbols on the right
    syms = [("&lt;/&gt;", 800, 70, CYAN, 0), ("{ }", 905, 118, VIOLET, 1), ("λ", 1010, 66, BLUE, 2), ("π", 1090, 116, CYAN, 3), ("01", 860, 142, BLUE, 4), ("[ ]", 1145, 62, VIOLET, 5)]
    for s, x, y, col, i in syms:
        o.append(f'<g class="{"bob" if i % 2 else "bob2"}" style="animation-delay:-{i*0.9:.1f}s"><text class="m" x="{x}" y="{y}" font-size="30" font-weight="700" fill="{col}" opacity="0.85" filter="url(#glowsm)">{s}</text></g>')
    o.append('</svg>')
    M.write("intro.svg", "\n".join(o))


# ======================================================================= portrait + orbit
def portrait():
    w, h = 400, 500
    img, (iw, ih) = jpeg_uri("me-portrait.png", 300)
    px, py, pw = 40, 40, 300
    ph = pw * ih / iw
    ph = min(ph, 420)
    o = head(w, h, "Portrait of Rheil Evans T. Lunio")
    o.append(f'<defs><clipPath id="pc"><rect x="{px}" y="{py}" width="{pw}" height="{ph:.0f}" rx="26"/></clipPath>'
             f'<linearGradient id="fadeb" x1="0" y1="0" x2="0" y2="1"><stop offset="0.65" stop-color="#04060e" stop-opacity="0"/><stop offset="1" stop-color="#04060e" stop-opacity="0.75"/></linearGradient></defs>')
    cx, cy = px + pw / 2, py + ph / 2
    # orbiting rings behind
    o.append(f'<g><animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="28s" repeatCount="indefinite"/><ellipse cx="{cx}" cy="{cy}" rx="182" ry="236" fill="none" stroke="{VIOLET}" stroke-opacity="0.5" stroke-width="2" stroke-dasharray="3 14"/>'
             f'<circle cx="{cx}" cy="{cy-236}" r="6" fill="{CYAN}" filter="url(#glowsm)"/><circle cx="{cx+182}" cy="{cy}" r="4" fill="{VIOLET}" filter="url(#glowsm)"/></g>')
    o.append(f'<g><animateTransform attributeName="transform" type="rotate" from="360 {cx} {cy}" to="0 {cx} {cy}" dur="40s" repeatCount="indefinite"/><ellipse cx="{cx}" cy="{cy}" rx="168" ry="222" fill="none" stroke="{CYAN}" stroke-opacity="0.35" stroke-width="2" stroke-dasharray="70 40"/>'
             f'<circle cx="{cx-168}" cy="{cy}" r="5" fill="{BLUE}" filter="url(#glowsm)"/></g>')
    o.append(f'<rect x="{px-6}" y="{py-6}" width="{pw+12}" height="{ph+12:.0f}" rx="31" fill="none" stroke="url(#acc)" stroke-width="3" filter="url(#glowsm)"><animate attributeName="stroke-opacity" values="0.5;1;0.5" dur="3.5s" repeatCount="indefinite"/></rect>')
    o.append(f'<image xlink:href="{img}" x="{px}" y="{py}" width="{pw}" height="{pw*ih/iw:.0f}" clip-path="url(#pc)" preserveAspectRatio="xMidYMid slice"/>')
    o.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph:.0f}" rx="26" fill="url(#fadeb)"/>')
    # scan line over the photo
    o.append(f'<g clip-path="url(#pc)"><rect x="{px}" y="{py-4}" width="{pw}" height="3" fill="{CYAN}" opacity="0.7" filter="url(#glowsm)">'
             f'<animate attributeName="y" values="{py};{py+ph:.0f};{py}" dur="6s" repeatCount="indefinite"/></rect></g>')
    # floating badges
    badges = [("CS · USTP", 4, 360, BLUE, "bob"), ("RESEARCHER", 999, 140, VIOLET, "bob2"), ("RETL", 999, 440, CYAN, "bob")]
    for i, (t, x, y, col, cls) in enumerate(badges):
        bw = len(t) * 11 + 40
        x = min(x, w - bw - 6)
        o.append(f'<g class="{cls}" style="animation-delay:-{i*1.3:.1f}s"><rect x="{x:.0f}" y="{y}" width="{bw:.0f}" height="34" rx="17" fill="#080d22" stroke="{col}" stroke-width="2"/>'
                 f'<circle cx="{x+16:.0f}" cy="{y+17}" r="4.5" fill="{col}"><animate attributeName="opacity" values="1;0.3;1" dur="2s" begin="-{i*0.6}s" repeatCount="indefinite"/></circle>'
                 f'<text class="m" x="{x+28:.0f}" y="{y+22}" font-size="14" letter-spacing="1.5" fill="{INK}">{t}</text></g>')
    o.append('</svg>')
    M.write("portrait-orbit.svg", "\n".join(o))


# ======================================================================= about me
def about():
    w = 700
    rows = [("Computer Science student at the University of Science and Technology of Southern Philippines (USTP), Cagayan de Oro", BLUE, "cap"),
            ("Python developer who also builds for the web with JavaScript, TypeScript and React", VIOLET, "code"),
            ("Published researcher, with a study that pairs a statistical model with a working web app", CYAN, "doc"),
            ("Active beyond code, in leadership, public speaking, broadcasting and creative work", VIOLET, "mic")]
    top, rh = 70, 84
    h = top + rows.__len__() * rh + 16
    o = head(w, h, "About me")
    o.append('<defs><linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="0.5" stop-color="#fff" stop-opacity="0.10"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>')
    o.append(M.backdrop(w, h, 41, 12, corners=False))
    o.append(f'<text class="m" x="30" y="44" font-size="15" letter-spacing="6" fill="{MUTED}">ABOUT ME</text>')
    o.append(f'<rect x="150" y="38" width="{w-180}" height="2" fill="url(#rule)"/>')
    for i, (txt, col, ic) in enumerate(rows):
        y = top + i * rh
        o.append(f'<g><rect x="22" y="{y}" width="{w-44}" height="{rh-12}" rx="16" fill="url(#card)" stroke="{LINE}" stroke-width="1.8"/>'
                 f'<rect x="22" y="{y+14}" width="4" height="{rh-40}" rx="2" fill="{col}" filter="url(#glowsm)"/>'
                 # shine sweep, staggered per row
                 f'<clipPath id="rc{i}"><rect x="22" y="{y}" width="{w-44}" height="{rh-12}" rx="16"/></clipPath>'
                 f'<g clip-path="url(#rc{i})"><rect y="{y}" width="160" height="{rh-12}" fill="url(#sweep)"><animate attributeName="x" values="-170;{w};{w}" keyTimes="0;0.35;1" dur="6s" begin="{i*0.9:.1f}s" repeatCount="indefinite"/></rect></g>')
        # icon
        ix, iy = 54, y + (rh - 12) / 2
        o.append(f'<circle cx="{ix}" cy="{iy}" r="21" fill="#0b1230" stroke="{col}" stroke-width="2"/>'
                 f'<circle cx="{ix}" cy="{iy}" r="21" fill="none" stroke="{col}" stroke-width="2" opacity="0"><animate attributeName="r" values="21;31" dur="3s" begin="-{i*0.7:.1f}s" repeatCount="indefinite"/><animate attributeName="opacity" values="0.7;0" dur="3s" begin="-{i*0.7:.1f}s" repeatCount="indefinite"/></circle>')
        g = f'<g transform="translate({ix-12},{iy-12})" fill="none" stroke="{col}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        if ic == "cap":
            g += '<path d="M12 4L1 9l11 5 11-5z"/><path d="M5 12v5c3 3 11 3 14 0v-5"/>'
        elif ic == "code":
            g += '<path d="M8 7l-6 5 6 5M16 7l6 5-6 5M14 4l-4 16"/>'
        elif ic == "doc":
            g += '<path d="M5 2h10l5 5v15H5z"/><path d="M9 12h7M9 16h7M9 8h2"/>'
        else:
            g += '<rect x="8" y="2" width="8" height="12" rx="4"/><path d="M4 11a8 8 0 0 0 16 0M12 19v3"/>'
        o.append(g + '</g>')
        # wrapped text (max 2 lines)
        lines = textwrap.wrap(txt, 66)
        ty = y + (rh - 12) / 2 - (len(lines) - 1) * 11 + 6
        for k, ln in enumerate(lines):
            o.append(f'<text class="t" x="94" y="{ty + k*24:.0f}" font-size="18" fill="#d6defa">{esc(ln)}</text>')
        o.append('</g>')
    o.append('</svg>')
    M.write("about-me.svg", "\n".join(o))


# ======================================================================= project cards
def chips(x, y, items, col):
    out, cx = [], x
    for t in items:
        cw = len(t) * 8.9 + 26
        out.append(f'<rect x="{cx:.0f}" y="{y}" width="{cw:.0f}" height="26" rx="14" fill="#0b1230" stroke="{col}" stroke-opacity="0.75" stroke-width="1.5"/>'
                   f'<text class="m" x="{cx+13:.0f}" y="{y+19}" font-size="14" fill="#cfd8ff">{esc(t)}</text>')
        cx += cw + 8
    return "\n".join(out)


def project_card(fname, kicker, title, desc, chip_items, col, art, w=600, h=440, seed=1, num="01"):
    o = head(w, h, f"{title}: {desc}")
    o.append(M.backdrop(w, h, seed, 14))
    o.append(f'<text class="m" x="40" y="58" font-size="14" letter-spacing="4" fill="{MUTED}">{kicker}</text>')
    o.append(f'<text class="m" x="{w-40}" y="58" text-anchor="end" font-size="14" letter-spacing="4" fill="{col}">PROJECT {num}</text>')
    o.append(f'<text class="t" x="40" y="106" font-size="{38 if len(title) < 15 else 31}" font-weight="800" fill="{INK}" filter="url(#glowsm)">{esc(title)}</text>')
    o.append(f'<rect x="40" y="120" width="56" height="4" rx="2" fill="{col}" filter="url(#glowsm)"><animate attributeName="width" values="30;120;30" dur="4s" repeatCount="indefinite"/></rect>')
    for i, ln in enumerate(textwrap.wrap(desc, 25)):
        o.append(f'<text class="t" x="40" y="{170+i*28}" font-size="19.5" fill="#aab6dd">{esc(ln)}</text>')
    o.append(chips(40, h - 94, chip_items, col))
    o.append(f'<rect x="40" y="{h-54}" width="{w-80}" height="1.5" fill="{LINE}"/>')
    o.append(f'<text class="m" x="40" y="{h-22}" font-size="15" letter-spacing="3.5" fill="{INK}">VIEW PROJECT</text>')
    o.append(f'<g class="nudge"><path d="M214 {h-28}h26m-7 -7l7 7-7 7" fill="none" stroke="{col}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" filter="url(#glowsm)"/></g>')
    o.append(f'<g transform="translate({w-290},150)">{art}</g>')
    o.append('</svg>')
    M.write(fname, "\n".join(o))


def art_promptpilot(col=VIOLET):
    s = []
    s.append(f'<rect x="0" y="0" width="250" height="44" rx="12" fill="#0b1230" stroke="{col}" stroke-width="2"/>')
    for i, lw in enumerate((160, 110)):
        s.append(f'<clipPath id="pp{i}"><rect x="14" y="{10+i*15}" width="0" height="8"><animate attributeName="width" values="0;{lw};{lw};0" keyTimes="0;{0.35+i*0.1};0.9;1" dur="5s" repeatCount="indefinite"/></rect></clipPath>'
                 f'<g clip-path="url(#pp{i})"><rect x="14" y="{10+i*15}" width="{lw}" height="8" rx="4" fill="{INK}" opacity="0.85"/></g>')
    s.append(f'<g><circle cx="224" cy="22" r="13" fill="{col}" opacity="0.2"><animate attributeName="r" values="13;19;13" dur="2s" repeatCount="indefinite"/></circle><path d="M219 15l12 7-12 7z" fill="{col}" filter="url(#glowsm)"/></g>')
    for x in (62, 188):
        s.append(f'<line x1="{x}" y1="44" x2="{x}" y2="58" stroke="{LINE}" stroke-width="3"/><line class="fd" x1="{x}" y1="44" x2="{x}" y2="58" stroke="{CYAN}" stroke-width="3"/>')
    for k, (x, c, lab) in enumerate(((0, BLUE, "A"), (126, CYAN, "B"))):
        s.append(f'<rect x="{x}" y="58" width="124" height="78" rx="12" fill="#0b1230" stroke="{LINE}" stroke-width="2"/>'
                 f'<text class="m" x="{x+12}" y="77" font-size="11" letter-spacing="2" fill="{MUTED}">OUTPUT {lab}</text>')
        for j in range(5):
            bh = 8 + (j * 7 + k * 11) % 22
            up = 14 if j % 2 == k else -5
            s.append(f'<rect x="{x+14+j*20}" y="{128-bh}" width="12" height="{bh}" rx="3" fill="{c}">'
                     f'<animate attributeName="height" values="{bh};{bh+up};{bh}" dur="2.8s" begin="-{j*0.35+k*0.5:.2f}s" repeatCount="indefinite"/>'
                     f'<animate attributeName="y" values="{128-bh};{128-bh-up};{128-bh}" dur="2.8s" begin="-{j*0.35+k*0.5:.2f}s" repeatCount="indefinite"/></rect>')
    s.append(f'<rect x="100" y="86" width="50" height="24" rx="12" fill="#080d22" stroke="{col}" stroke-width="2"/><text class="m" x="125" y="103" text-anchor="middle" font-size="13" fill="{INK}">VS</text>')
    pts = [(0, 186), (40, 178), (80, 183), (120, 166), (160, 171), (200, 156), (250, 150)]
    d = "M" + " L".join(f"{x},{y}" for x, y in pts)
    s.append(f'<path d="{d}" fill="none" stroke="url(#acc)" stroke-width="3.5" stroke-linecap="round" pathLength="1" stroke-dasharray="1" filter="url(#glowsm)"><animate attributeName="stroke-dashoffset" values="1;0;0;1" keyTimes="0;0.5;0.9;1" dur="5s" repeatCount="indefinite"/></path>')
    s.append(f'<circle r="5" fill="#fff" filter="url(#glowsm)"><animateMotion dur="5s" repeatCount="indefinite" path="{d}" keyPoints="0;1;1" keyTimes="0;0.5;1" calcMode="linear"/></circle>')
    return "\n".join(s)


def art_organizer(col=BLUE):
    s = []
    folders = [("IMG", 0, BLUE), ("DOC", 62, VIOLET), ("SRC", 124, CYAN)]
    fx = 168
    for lab, fy, c in folders:
        s.append(f'<path d="M{fx} {fy+8}h18l6 7h42a6 6 0 0 1 6 6v28a6 6 0 0 1-6 6h-66a6 6 0 0 1-6-6v-35a6 6 0 0 1 6-6z" fill="#0b1230" stroke="{c}" stroke-width="2.5"/>'
                 f'<text class="m" x="{fx+33}" y="{fy+46}" text-anchor="middle" font-size="14" letter-spacing="2" fill="{INK}">{lab}</text>')
    rnd = random.Random(7)
    kinds = [(0, BLUE), (1, VIOLET), (2, CYAN)]
    for i in range(9):
        k, c = kinds[i % 3]
        sx, sy = rnd.uniform(6, 70), rnd.uniform(14, 150)
        ex, ey = fx + 33, folders[k][1] + 34
        mx = sx + (ex - sx) * 0.5
        path = f"M{sx:.0f},{sy:.0f} C{mx:.0f},{sy-20:.0f} {mx:.0f},{ey+16:.0f} {ex},{ey}"
        dur, beg = 4.5, -(i * 0.5)
        s.append(f'<g><path d="M-9 -11h12l7 7v15h-19z" fill="#0b1230" stroke="{c}" stroke-width="2"/><path d="M3 -11v7h7" fill="none" stroke="{c}" stroke-width="2"/>'
                 f'<animateMotion dur="{dur}s" begin="{beg}s" repeatCount="indefinite" path="{path}" keyPoints="0;0;1;1" keyTimes="0;0.15;0.8;1" calcMode="linear"/>'
                 f'<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;0.78;0.84;0.99;1" dur="{dur}s" begin="{beg}s" repeatCount="indefinite"/></g>')
    s.append(f'<text class="m" x="0" y="186" font-size="11" letter-spacing="2.5" fill="{MUTED}">MESSY  →  ORGANIZED</text>')
    return "\n".join(s)


def art_commitquest(col=CYAN):
    s = []
    s.append(f'<g><polygon points="20,0 38,10 38,30 20,40 2,30 2,10" fill="#0b1230" stroke="{col}" stroke-width="2.5" filter="url(#glowsm)"/><text class="m" x="20" y="25" text-anchor="middle" font-size="13" font-weight="700" fill="{INK}">LV</text></g>')
    s.append(f'<text class="m" x="52" y="14" font-size="11" letter-spacing="3" fill="{MUTED}">EXPERIENCE</text>')
    s.append(f'<rect x="52" y="22" width="198" height="13" rx="6.5" fill="#0b1230" stroke="{LINE}" stroke-width="1.5"/>')
    s.append(f'<clipPath id="xp"><rect x="52" y="22" width="198" height="13" rx="6.5"/></clipPath><g clip-path="url(#xp)"><rect x="52" y="22" width="0" height="13" fill="url(#acc)" filter="url(#glowsm)"><animate attributeName="width" values="0;198;198;0" keyTimes="0;0.6;0.92;1" dur="5s" repeatCount="indefinite"/></rect></g>')
    s.append(f'<text class="m" x="196" y="60" font-size="16" font-weight="700" fill="{col}" opacity="0" filter="url(#glowsm)">+50 XP<animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;0.58;0.66;0.85;1" dur="5s" repeatCount="indefinite"/><animate attributeName="y" values="64;64;56;48;48" keyTimes="0;0.58;0.66;0.85;1" dur="5s" repeatCount="indefinite"/></text>')
    s.append(f'<rect x="0" y="68" width="250" height="86" rx="12" fill="#070c20" stroke="{LINE}" stroke-width="2"/>')
    for i, c in enumerate((VIOLET, BLUE, CYAN)):
        s.append(f'<circle cx="{16+i*13}" cy="81" r="3.5" fill="{c}"/>')
    cmds = [("$ git commit -m \"fix bug\"", 103), ("✓ challenge solved", 123), ("★ hint unlocked", 143)]
    for i, (t, y) in enumerate(cmds):
        s.append(f'<text class="m" x="16" y="{y}" font-size="13" fill="{"#7fe3b5" if i else "#cfd8ff"}" opacity="0">{esc(t)}'
                 f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;{0.05+i*0.22:.2f};{0.12+i*0.22:.2f};0.92;1" dur="5s" repeatCount="indefinite"/></text>')
    for i in range(4):
        x = 4 + i * 30
        s.append(f'<g><circle cx="{x+11}" cy="176" r="11" fill="#0b1230" stroke="{VIOLET}" stroke-width="2"/><path d="M{x+11} 169l2.2 4.8 5.2.6-3.9 3.5 1.1 5.1-4.6-2.6-4.6 2.6 1.1-5.1-3.9-3.5 5.2-.6z" fill="{VIOLET}" opacity="0.3"><animate attributeName="opacity" values="0.25;1;0.25" dur="5s" begin="{-i*1.1:.1f}s" repeatCount="indefinite"/></path></g>')
    s.append(f'<text class="m" x="136" y="180" font-size="11" letter-spacing="2" fill="{MUTED}">ACHIEVEMENTS</text>')
    return "\n".join(s)


def art_dayform(col=VIOLET):
    s = []
    days = ["M", "T", "W", "T", "F"]
    cw, rhh, gap = 50, 30, 5
    for i, d in enumerate(days):
        s.append(f'<text class="m" x="{i*cw+(cw-5)/2:.0f}" y="11" text-anchor="middle" font-size="12" fill="{MUTED}">{d}</text>')
    plan = {(0, 0): BLUE, (0, 1): CYAN, (1, 1): VIOLET, (1, 2): BLUE, (2, 0): VIOLET, (2, 3): CYAN, (3, 1): BLUE, (3, 2): VIOLET, (4, 0): CYAN, (4, 3): BLUE}
    for r in range(4):
        for c in range(5):
            x, y = c * cw, 20 + r * (rhh + gap)
            s.append(f'<rect x="{x}" y="{y}" width="{cw-5}" height="{rhh}" rx="8" fill="#0b1230" stroke="{LINE}" stroke-width="1.5"/>')
            if (c, r) in plan:
                cc = plan[(c, r)]
                s.append(f'<rect x="{x+3}" y="{y+3}" width="{cw-11}" height="{rhh-6}" rx="6" fill="{cc}" opacity="0.25"><animate attributeName="opacity" values="0.15;0.85;0.15" dur="4s" begin="-{(c*0.6+r*0.9):.1f}s" repeatCount="indefinite"/></rect>'
                         f'<rect x="{x+10}" y="{y+rhh/2-2.5:.0f}" width="{cw-25}" height="5" rx="2.5" fill="{INK}" opacity="0.7"/>')
    ph = 4 * (rhh + gap) + 4
    s.append(f'<rect x="-3" y="16" width="3" height="{ph}" rx="1.5" fill="{col}" filter="url(#glowsm)"><animate attributeName="x" values="-3;{5*cw-3}" dur="5s" repeatCount="indefinite"/></rect>')
    s.append(f'<text class="m" x="0" y="{20+ph+16}" font-size="11" letter-spacing="2.5" fill="{MUTED}">TEMPLATE  →  PLAN</text>')
    return "\n".join(s)


def research_card():
    w, h = 1240, 310
    col = CYAN
    o = head(w, h, "Blood Pressure Transition Modeling: published research with a web-based application")
    o.append(M.backdrop(w, h, 61, 20))
    o.append(f'<text class="m" x="44" y="56" font-size="13" letter-spacing="4" fill="{MUTED}">PUBLISHED RESEARCH</text>')
    o.append(f'<circle cx="276" cy="52" r="5" fill="{col}"><animate attributeName="opacity" values="1;0.25;1" dur="1.8s" repeatCount="indefinite"/></circle>')
    o.append(f'<text class="t" x="44" y="108" font-size="35" font-weight="800" fill="{INK}" filter="url(#glowsm)">Blood Pressure Transition Modeling</text>')
    o.append(f'<rect x="44" y="124" width="64" height="4" rx="2" fill="{col}" filter="url(#glowsm)"><animate attributeName="width" values="30;160;30" dur="4s" repeatCount="indefinite"/></rect>')
    for i, ln in enumerate(textwrap.wrap("My published research and its accompanying web-based application. The study models how blood pressure categories change over time, as a basis for hypertension prevention programs.", 72)):
        o.append(f'<text class="t" x="44" y="{162+i*26}" font-size="18.5" fill="#aab6dd">{esc(ln)}</text>')
    o.append(chips(44, h - 78, ["Markov Chain", "Logistic Model", "Web Application"], col))
    o.append(f'<text class="m" x="{w-44}" y="{h-30}" text-anchor="end" font-size="14" letter-spacing="3.5" fill="{INK}">READ THE PUBLICATION</text>')
    o.append(f'<g class="nudge"><path d="M{w-34} {h-36}h26m-7 -7l7 7-7 7" fill="none" stroke="{col}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" transform="translate(-10 0)" filter="url(#glowsm)"/></g>')
    # art: 3-state chain + mini web app window
    ox, oy = 700, 44
    nodes = [(60, 120, "S1", BLUE), (170, 52, "S2", VIOLET), (280, 120, "S3", CYAN)]
    pairs = [(0, 1), (1, 0), (1, 2), (2, 1)]
    for k, (a, b) in enumerate(pairs):
        (x1, y1, *_), (x2, y2, *_) = nodes[a], nodes[b]
        off = 9 if k % 2 == 0 else -9
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = x2 - x1, y2 - y1
        l = math.hypot(dx, dy)
        nx, ny = -dy / l, dx / l
        cxp, cyp = mx + nx * 26 * (1 if k % 2 == 0 else -1), my + ny * 26 * (1 if k % 2 == 0 else -1)
        ux, uy = dx / l, dy / l
        sx, sy, ex, ey = x1 + ux * 24, y1 + uy * 24, x2 - ux * 24, y2 - uy * 24
        d = f"M{ox+sx:.0f},{oy+sy:.0f} Q{ox+cxp:.0f},{oy+cyp:.0f} {ox+ex:.0f},{oy+ey:.0f}"
        o.append(f'<path d="{d}" fill="none" stroke="{LINE}" stroke-width="2.5"/><path class="fd" d="{d}" fill="none" stroke="{CYAN}" stroke-width="2"/>')
        o.append(M.travel(d, 2.6, k * 0.65, 4))
    for i, (x, y, lab, c) in enumerate(nodes):
        o.append(f'<circle cx="{ox+x}" cy="{oy+y}" r="30" fill="{c}" opacity="0.1"><animate attributeName="opacity" values="0.05;0.3;0.05" dur="3s" begin="-{i}s" repeatCount="indefinite"/></circle>'
                 f'<circle cx="{ox+x}" cy="{oy+y}" r="23" fill="#070c20" stroke="{c}" stroke-width="3" filter="url(#glowsm)"/>'
                 f'<text class="m" x="{ox+x}" y="{oy+y+6}" text-anchor="middle" font-size="16" font-weight="700" fill="{INK}">{lab}</text>')
    # web app window
    wx, wy, ww, wh = 1130, 40, 100, 150
    wx = 1115
    bx, by, bw, bh = 1040, 130, 160, 96
    o.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="10" fill="#070c20" stroke="{LINE}" stroke-width="2"/>')
    for i, c in enumerate((VIOLET, BLUE, CYAN)):
        o.append(f'<circle cx="{bx+12+i*11}" cy="{by+11}" r="3.5" fill="{c}"/>')
    for j in range(6):
        hh = 10 + (j * 9) % 30
        o.append(f'<rect x="{bx+14+j*19}" y="{by+bh-10-hh}" width="11" height="{hh}" rx="2.5" fill="{[BLUE,VIOLET,CYAN][j%3]}"><animate attributeName="height" values="{hh};{hh+14};{hh}" dur="3s" begin="-{j*0.4:.1f}s" repeatCount="indefinite"/><animate attributeName="y" values="{by+bh-10-hh};{by+bh-10-hh-14};{by+bh-10-hh}" dur="3s" begin="-{j*0.4:.1f}s" repeatCount="indefinite"/></rect>')
    o.append('</svg>')
    M.write("project-research.svg", "\n".join(o))


def projects():
    project_card("project-promptpilot.svg", "AI  ·  PROMPT WORKSPACE", "PromptPilot",
                 "AI prompt workspace with a library, playground, comparison tools, and analytics.",
                 ["Gemini API", "Prompt Library", "Analytics"], VIOLET, art_promptpilot(), seed=71, num="01")
    project_card("project-smartfileorganizer.svg", "PYTHON  ·  FILE MANAGEMENT", "SmartFileOrganizerPro",
                 "Desktop tool that automatically sorts files into organized folders.",
                 ["Python", "Desktop", "Automation"], BLUE, art_organizer(), seed=72, num="02")
    project_card("project-commitquest.svg", "JAVASCRIPT  ·  CODING GAME", "CommitQuest",
                 "Gamified coding challenges with XP, hints, and achievements.",
                 ["JavaScript", "Gamified", "XP + Badges"], CYAN, art_commitquest(), seed=73, num="03")
    project_card("project-dayform.svg", "PRODUCTIVITY  ·  SCHEDULING", "DayForm",
                 "Scheduling platform with customizable templates for daily planning.",
                 ["Scheduling", "Templates", "Planner"], VIOLET, art_dayform(), seed=74, num="04")
    research_card()


if __name__ == "__main__":
    intro(); portrait(); about(); projects()
