#!/usr/bin/env python3
"""Generates the animated SVG graphics in ../assets (run: python3 make_svgs.py).

All SVGs are self-contained (no external fonts or images) so GitHub renders them
when used as <img src="assets/....svg">. Animations use SMIL + CSS only.
"""
import base64, io, math, os, random
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets")

BLUE, VIOLET, CYAN = "#3b82f6", "#8b5cf6", "#22d3ee"
INK, MUTED, GREEN = "#e8edff", "#7f8db0", "#4ade80"
LINE = "#26336b"


def data_uri(name, width):
    im = Image.open(os.path.join(OUT, name)).convert("RGBA")
    im = im.resize((width, int(im.height * width / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode(), im.size


CSS = """
.t{font-family:'Segoe UI','Helvetica Neue',Arial,sans-serif}
.m{font-family:'SFMono-Regular',Consolas,'Liberation Mono','Courier New',monospace}
.flow{stroke-dasharray:20 90;animation:flow 3s linear infinite}
.fd{stroke-dasharray:10 12;animation:flow2 1.4s linear infinite}
.pulse{animation:pulse 2.4s ease-in-out infinite}
.scan{animation:scan 9s linear infinite}
.spin{transform-box:fill-box;transform-origin:center;animation:spin 60s linear infinite}
.spinr{transform-box:fill-box;transform-origin:center;animation:spin 90s linear infinite reverse}
@keyframes flow{to{stroke-dashoffset:-110}}
@keyframes flow2{to{stroke-dashoffset:-22}}
@keyframes pulse{0%,100%{opacity:.35}50%{opacity:1}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes scan{0%{transform:translateY(0)}100%{transform:translateY(var(--h))}}
@media (prefers-reduced-motion: reduce){.flow,.fd,.pulse,.scan,.spin,.spinr{animation:none}}
"""


def svg_open(w, h, title, desc=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{title}">\n'
            f'<title>{title}</title>\n')


def defs(w, h, extra=""):
    return f"""<defs>
<radialGradient id="bg" cx="50%" cy="45%" r="80%"><stop offset="0" stop-color="#101a3d"/><stop offset="0.55" stop-color="#070b1c"/><stop offset="1" stop-color="#04060e"/></radialGradient>
<linearGradient id="card" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0d1433"/><stop offset="1" stop-color="#080d22"/></linearGradient>
<linearGradient id="acc" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{BLUE}"/><stop offset="0.5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{CYAN}"/></linearGradient>
<linearGradient id="rule" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{VIOLET}" stop-opacity="0"/><stop offset="0.5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></linearGradient>
<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="{BLUE}" stroke-opacity="0.07" stroke-width="1"/></pattern>
<filter id="glow" x="-30%" y="-60%" width="160%" height="220%"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="glowsm" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="frame"><rect x="6" y="6" width="{w-12}" height="{h-12}" rx="22"/></clipPath>
<marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="{CYAN}"/></marker>
{extra}
</defs>
<style>{CSS}</style>
"""


def backdrop(w, h, seed=1, n=26, corners=True):
    rnd = random.Random(seed)
    s = [f'<rect width="{w}" height="{h}" rx="24" fill="url(#bg)"/>',
         f'<rect width="{w}" height="{h}" rx="24" fill="url(#grid)"/>', '<g>']
    for _ in range(n):
        x, y = rnd.uniform(20, w - 20), rnd.uniform(20, h - 20)
        r, op = rnd.uniform(1.2, 3), rnd.uniform(0.2, 0.55)
        col = rnd.choice([BLUE, VIOLET, CYAN])
        dur, beg = rnd.uniform(7, 13), -rnd.uniform(0, 12)
        s.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="{col}" opacity="{op:.2f}">'
                 f'<animate attributeName="cy" values="{y:.0f};{y-40:.0f};{y:.0f}" dur="{dur:.1f}s" begin="{beg:.1f}s" repeatCount="indefinite"/></circle>')
    s.append('</g>')
    s.append(f'<g clip-path="url(#frame)"><rect class="scan" style="--h:{h}px" x="0" y="-70" width="{w}" height="70" fill="{VIOLET}" opacity="0.05"/></g>')
    s.append(f'<rect x="6" y="6" width="{w-12}" height="{h-12}" rx="22" fill="none" stroke="#25306a" stroke-opacity="0.9" stroke-width="1.5"/>')
    if corners:
        L = 44
        s.append(f'<g stroke="url(#acc)" stroke-width="3.5" fill="none" filter="url(#glowsm)">'
                 f'<path d="M6 {L+6}V28a22 22 0 0 1 22-22h{L}"/>'
                 f'<path d="M{w-6-L-22} 6h{L}a22 22 0 0 1 22 22v{L-16}"/>'
                 f'<path d="M6 {h-L-6}v{L-16}a22 22 0 0 0 22 22h{L}"/>'
                 f'<path d="M{w-6-L-22} {h-6}h{L}a22 22 0 0 0 22-22v-{L-16}"/></g>')
    return "\n".join(s) + "\n"


def title_block(w, title, sub, y=70, size=40, track=10):
    return (f'<text class="t" x="{w/2}" y="{y}" text-anchor="middle" font-size="{size}" font-weight="700" letter-spacing="{track}" fill="{INK}" filter="url(#glow)">{title}</text>\n'
            f'<text class="m" x="{w/2}" y="{y+34}" text-anchor="middle" font-size="16" letter-spacing="4" fill="{MUTED}">{sub}</text>\n'
            f'<rect x="{w/2-300}" y="{y+52}" width="600" height="3" fill="url(#rule)"/>\n'
            f'<path d="M{w/2} {y+44}l8 11-8 11-8-11z" fill="{VIOLET}" filter="url(#glowsm)"/>\n')


def card(x, y, w, h, kicker, title, lines, tsize=26, lsize=19, accent=VIOLET):
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="url(#card)" stroke="{LINE}" stroke-width="2"/>',
           f'<rect x="{x+24}" y="{y}" width="{w-48}" height="4" rx="2" fill="{accent}" filter="url(#glowsm)"/>',
           f'<text class="m" x="{x+24}" y="{y+34}" font-size="13" letter-spacing="3.5" fill="{MUTED}">{kicker}</text>',
           f'<text class="t" x="{x+24}" y="{y+68}" font-size="{tsize}" font-weight="700" fill="{INK}">{title}</text>']
    for i, ln in enumerate(lines):
        out.append(f'<text class="t" x="{x+24}" y="{y+98+i*(lsize+9)}" font-size="{lsize}" fill="{MUTED}">{ln}</text>')
    return "\n".join(out) + "\n"


def travel(path, dur, begin, r=5):
    return (f'<circle r="{r}" fill="#fff" filter="url(#glowsm)"><animateMotion dur="{dur}s" begin="-{begin}s" repeatCount="indefinite" path="{path}"/></circle>\n')


def write(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print(name, os.path.getsize(os.path.join(OUT, name)) // 1024, "KB")


# ------------------------------------------------------------------ typing
def typing():
    w, h = 900, 64
    phrases = ["Student Developer", "Researcher", "Aspiring Software Engineer"]
    cw, size, x0 = 19.2, 32, 60
    dur = 12
    o = [svg_open(w, h, "Animated typing: Student Developer, Researcher, Aspiring Software Engineer"), defs(w, h)]
    o.append(f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="14" fill="#090e22" stroke="#25306a" stroke-width="2"/>')
    o.append(f'<text class="m" x="34" y="43" font-size="{size}" fill="{VIOLET}">&gt;_</text>')
    # centered group computed per phrase
    for i, ph in enumerate(phrases):
        n = len(ph)
        width = n * cw
        sx = (w - width) / 2
        a = i / 3
        kt = f"0;{a:.4f};{a+0.12:.4f};{a+0.26:.4f};{a+0.31:.4f};1"
        o.append(f'<clipPath id="c{i}"><rect x="{sx-4:.1f}" y="6" width="0" height="52">'
                 f'<animate attributeName="width" values="0;0;{width+8:.1f};{width+8:.1f};0;0" keyTimes="{kt}" dur="{dur}s" repeatCount="indefinite"/></rect></clipPath>')
        o.append(f'<g clip-path="url(#c{i})"><text class="m" x="{sx:.1f}" y="43" font-size="{size}" fill="{INK}" textLength="{width:.1f}" lengthAdjust="spacing" filter="url(#glowsm)">{ph}</text></g>')
        ct = f"0;{a:.4f};{a+0.31:.4f};{a+0.32:.4f};1"
        o.append(f'<g><animate attributeName="opacity" values="1;0;1" dur="0.9s" repeatCount="indefinite"/>'
                 f'<rect x="{sx:.1f}" y="12" width="3" height="40" fill="{CYAN}" filter="url(#glowsm)" opacity="0">'
                 f'<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="{ct}" calcMode="discrete" dur="{dur}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="x" values="{sx:.1f};{sx:.1f};{sx+width:.1f};{sx+width:.1f};{sx:.1f};{sx:.1f}" keyTimes="{kt}" dur="{dur}s" repeatCount="indefinite"/></rect></g>')
    o.append('</svg>')
    write("typing.svg", "\n".join(o))


# ------------------------------------------------------------------ divider
def divider():
    w, h = 1200, 28
    p = f"M60 14H{w-60}"
    o = [svg_open(w, h, "divider"), defs(w, h)]
    o.append(f'<rect x="60" y="13" width="{w-120}" height="2.5" fill="url(#rule)"/>')
    o.append(f'<path d="M{w/2} 4l8 10-8 10-8-10z" fill="{VIOLET}" filter="url(#glowsm)"/>')
    o.append(f'<line class="flow" x1="60" y1="14" x2="{w-60}" y2="14" stroke="{CYAN}" stroke-width="3" stroke-linecap="round" style="stroke-dasharray:18 220;animation-duration:5s"/>')
    o.append(f'<circle r="4" fill="#fff" filter="url(#glowsm)"><animateMotion dur="6s" repeatCount="indefinite" path="{p}"/></circle>')
    o.append('</svg>')
    write("divider.svg", "\n".join(o))


# ------------------------------------------------------------------ focus network
def focus():
    w, h = 1200, 600
    mark, (mw, mh) = data_uri("logo-mark.png", 340)
    o = [svg_open(w, h, "Current focus: software development, AI, web development, research, UI/UX design and technology"), defs(w, h)]
    o.append(backdrop(w, h, 3))
    o.append(title_block(w, "CURRENT FOCUS", "SOFTWARE  /  AI  /  WEB  /  RESEARCH  /  UI·UX", 68))
    cx, cy = 600, 360
    o.append(f'<circle cx="{cx}" cy="{cy}" r="190" fill="{VIOLET}" opacity="0.07"/>')
    o.append(f'<circle class="spin" cx="{cx}" cy="{cy}" r="150" fill="none" stroke="{VIOLET}" stroke-opacity="0.55" stroke-width="2.5" stroke-dasharray="4 18"/>')
    o.append(f'<circle class="spinr" cx="{cx}" cy="{cy}" r="125" fill="none" stroke="{CYAN}" stroke-opacity="0.4" stroke-width="2.5" stroke-dasharray="90 45"/>')
    items = [("01", "Software Development", "Practical tools that ship", BLUE),
             ("02", "Artificial Intelligence", "Prompt tools, AI assistants", VIOLET),
             ("03", "Web Development", "Responsive, polished UIs", CYAN),
             ("04", "Research", "Modeling health data", VIOLET),
             ("05", "UI/UX Design", "Clear hierarchy, consistent", CYAN),
             ("06", "Technology", "Always exploring new ideas", BLUE)]
    ys = [160, 305, 450]
    paths = []
    for i, (k, t, d, col) in enumerate(items):
        left = i < 3
        x = 30 if left else 790
        y = ys[i % 3]
        ccy = y + 62
        o.append(card(x, y, 380, 125, f"FOCUS {k}", t, [d], tsize=28, lsize=20, accent=col))
        sx = x + 380 if left else x
        ex = cx - 126 if left else cx + 126
        c1 = sx + (60 if left else -60)
        path = f"M{sx},{ccy} C{c1},{ccy} {ex+(-70 if left else 70)},{cy} {ex},{cy}"
        o.append(f'<path d="{path}" fill="none" stroke="{LINE}" stroke-width="3"/>')
        o.append(f'<path class="fd" d="{path}" fill="none" stroke="{col}" stroke-width="3"/>')
        paths.append((path, i))
        o.append(f'<circle class="pulse" cx="{sx}" cy="{ccy}" r="7" fill="{col}" filter="url(#glowsm)" style="animation-delay:-{i*0.4:.1f}s"/>')
    for path, i in paths:
        o.append(travel(path, 3.2 + i * 0.25, i * 0.7))
    o.append(f'<image xlink:href="{mark}" x="{cx-mw/2*0.62:.0f}" y="{cy-mh/2*0.62:.0f}" width="{mw*0.62:.0f}" height="{mh*0.62:.0f}"/>')
    o.append(f'<text class="m" x="{cx}" y="{h-26}" text-anchor="middle" font-size="14" letter-spacing="5" fill="{MUTED}">BUILD  ·  RESEARCH  ·  ITERATE</text>')
    o.append('</svg>')
    write("focus-network.svg", "\n".join(o))


# ------------------------------------------------------------------ stack
def stack():
    w, h = 1200, 560
    o = [svg_open(w, h, "Technology stack: languages, frontend, backend, AI and tooling"), defs(w, h)]
    o.append(backdrop(w, h, 5))
    o.append(title_block(w, "TECHNOLOGY STACK", "FROM THE REPOSITORIES ON THIS PROFILE", 68))
    cols = [("LAYER 01", "Languages", ["Python", "JavaScript", "TypeScript", "HTML &amp; CSS"], BLUE),
            ("LAYER 02", "Frontend", ["React", "Vite"], VIOLET),
            ("LAYER 03", "Backend", ["Node.js", "Express"], CYAN),
            ("LAYER 04", "AI", ["Gemini API", "Gen AI SDK"], VIOLET),
            ("LAYER 05", "Tooling", ["Git", "GitHub", "VS Code"], BLUE)]
    cw, gap, x0, y0, ch = 204, 26, 38, 170, 310
    mid = y0 + ch / 2
    for i, (k, t, items, col) in enumerate(cols):
        x = x0 + i * (cw + gap)
        o.append(card(x, y0, cw, ch, k, t, [], tsize=27, accent=col))
        o.append(f'<line x1="{x+24}" y1="{y0+88}" x2="{x+cw-24}" y2="{y0+88}" stroke="{LINE}" stroke-width="2"/>')
        for j, it in enumerate(items):
            yy = y0 + 128 + j * 44
            o.append(f'<circle cx="{x+31}" cy="{yy-7}" r="6" fill="{col}"><animate attributeName="opacity" values="0.25;1;0.25" dur="3s" begin="-{(i*0.5+j*0.35):.2f}s" repeatCount="indefinite"/></circle>')
            o.append(f'<text class="t" x="{x+48}" y="{yy}" font-size="22" fill="#d6defa">{it}</text>')
        if i < len(cols) - 1:
            ax, bx = x + cw, x + cw + gap
            p = f"M{ax},{mid} L{bx},{mid}"
            o.append(f'<line x1="{ax}" y1="{mid}" x2="{bx}" y2="{mid}" stroke="{LINE}" stroke-width="3"/>')
            o.append(f'<line class="fd" x1="{ax}" y1="{mid}" x2="{bx}" y2="{mid}" stroke="{CYAN}" stroke-width="3"/>')
            o.append(travel(p, 1.6, i * 0.4, 4))
    bx0, bw = 330, 540
    o.append(f'<circle class="pulse" cx="60" cy="{h-34}" r="7" fill="{VIOLET}"/>')
    o.append(f'<text class="m" x="78" y="{h-29}" font-size="15" letter-spacing="4" fill="{MUTED}">BUILD PIPELINE</text>')
    o.append(f'<clipPath id="bar"><rect x="{bx0}" y="{h-40}" width="{bw}" height="10" rx="5"/></clipPath>')
    o.append(f'<rect x="{bx0}" y="{h-40}" width="{bw}" height="10" rx="5" fill="#0b1230" stroke="{LINE}" stroke-width="1.5"/>')
    o.append(f'<g clip-path="url(#bar)"><rect y="{h-40}" width="170" height="10" rx="5" fill="url(#acc)" filter="url(#glowsm)"><animate attributeName="x" values="{bx0-170};{bx0+bw}" dur="3s" repeatCount="indefinite"/></rect></g>')
    o.append(f'<text class="m" x="{w-60}" y="{h-29}" text-anchor="end" font-size="15" letter-spacing="4" fill="{MUTED}">SHIP  /  TEST  /  REFINE</text>')
    o.append('</svg>')
    write("stack.svg", "\n".join(o))


# ------------------------------------------------------------------ research
def research():
    w, h = 1200, 600
    o = [svg_open(w, h, "Illustration of the multistate Markov chain and logistic model used in the research"), defs(w, h)]
    o.append(backdrop(w, h, 8))
    o.append(title_block(w, "RESEARCH MODEL", "MULTISTATE MARKOV CHAIN  /  LOGISTIC MODEL  /  WEB APP", 68))
    # panels
    for x, lab in ((40, "STATE TRANSITIONS"), (680, "LOGISTIC RESPONSE")):
        pw = 480 if x == 680 else 610
        o.append(f'<rect x="{x}" y="168" width="{pw}" height="372" rx="18" fill="url(#card)" stroke="{LINE}" stroke-width="2"/>')
        o.append(f'<rect x="{x+24}" y="168" width="{pw-48}" height="4" rx="2" fill="{VIOLET if x==40 else CYAN}" filter="url(#glowsm)"/>')
        o.append(f'<text class="m" x="{x+24}" y="204" font-size="13" letter-spacing="3.5" fill="{MUTED}">{lab}</text>')
    nodes = {"N": (130, 440, "NORMAL", BLUE), "E": (345, 290, "ELEVATED", VIOLET), "H": (560, 440, "HIGH", CYAN)}
    R = 46

    def unit(vx, vy):
        l = math.hypot(vx, vy)
        return vx / l, vy / l

    def curve(a, b, bend):
        ax, ay = nodes[a][:2]
        bx, by = nodes[b][:2]
        mx, my = (ax + bx) / 2, (ay + by) / 2
        px, py = unit(-(by - ay), bx - ax)
        cx_, cy_ = mx + px * bend, my + py * bend
        ux, uy = unit(cx_ - ax, cy_ - ay)
        sx, sy = ax + ux * (R + 3), ay + uy * (R + 3)
        vx, vy = unit(bx - cx_, by - cy_)
        ex, ey = bx - vx * (R + 10), by - vy * (R + 10)
        return f"M{sx:.1f},{sy:.1f} Q{cx_:.1f},{cy_:.1f} {ex:.1f},{ey:.1f}", (cx_, cy_)
    edges = [("N", "E", 46, "p12"), ("E", "N", 46, "p21"), ("E", "H", 46, "p23"), ("H", "E", 46, "p32")]
    for k, (a, b, bend, lab) in enumerate(edges):
        d, (lx, ly) = curve(a, b, bend)
        o.append(f'<path d="{d}" fill="none" stroke="{LINE}" stroke-width="3" marker-end="url(#arr)"/>')
        o.append(f'<path class="fd" d="{d}" fill="none" stroke="{CYAN}" stroke-width="2.5" stroke-opacity="0.8"/>')
        o.append(travel(d.replace(" Q", " Q"), 2.8, k * 0.7, 4.5))
        ax_, ay_ = nodes[a][:2]; bx_, by_ = nodes[b][:2]
        pxx, pyy = unit(-(by_ - ay_), bx_ - ax_)
        mx_, my_ = (ax_ + bx_) / 2 + pxx * (bend / 2 + 22), (ay_ + by_) / 2 + pyy * (bend / 2 + 22)
        o.append(f'<text class="m" x="{mx_:.0f}" y="{my_ + 5:.0f}" text-anchor="middle" font-size="15" fill="{MUTED}">{lab}</text>')
    for key, (x, y, lab, col) in nodes.items():
        o.append(f'<circle cx="{x}" cy="{y}" r="{R+10}" fill="{col}" opacity="0.1"><animate attributeName="opacity" values="0.05;0.28;0.05" dur="3.2s" begin="-{list(nodes).index(key)*1.0}s" repeatCount="indefinite"/></circle>')
        o.append(f'<circle cx="{x}" cy="{y}" r="{R}" fill="#070c20" stroke="{col}" stroke-width="3.5" filter="url(#glowsm)"/>')
        o.append(f'<text class="m" x="{x}" y="{y+9}" text-anchor="middle" font-size="26" font-weight="700" fill="{INK}">S{list(nodes).index(key)+1}</text>')
        o.append(f'<text class="m" x="{x}" y="{y-R-18 if key=="E" else y+R+32}" text-anchor="middle" font-size="14" letter-spacing="3" fill="{MUTED}">{lab}</text>')
    # logistic curve
    x0, x1, yb, yt = 730, 1130, 478, 232
    o.append(f'<path d="M{x0} {yt-10}V{yb}H{x1+10}" fill="none" stroke="{LINE}" stroke-width="2.5"/>')
    o.append(f'<line x1="{x0}" y1="{(yb+yt)/2}" x2="{x1}" y2="{(yb+yt)/2}" stroke="{LINE}" stroke-width="1.5" stroke-dasharray="5 7"/>')
    xm = (x0 + x1) / 2
    o.append(f'<line x1="{xm}" y1="{yt}" x2="{xm}" y2="{yb}" stroke="{LINE}" stroke-width="1.5" stroke-dasharray="5 7"/>')
    pts = []
    for i in range(61):
        x = x0 + (x1 - x0) * i / 60
        s = 1 / (1 + math.exp(-(x - xm) / 48))
        pts.append((x, yb - (yb - yt) * (0.04 + 0.92 * s)))
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    o.append(f'<path d="{d}" fill="none" stroke="{VIOLET}" stroke-opacity="0.25" stroke-width="5" stroke-linecap="round"/>')
    o.append(f'<path d="{d}" pathLength="1" fill="none" stroke="url(#acc)" stroke-width="5" stroke-linecap="round" stroke-dasharray="1" filter="url(#glowsm)">'
             f'<animate attributeName="stroke-dashoffset" values="1;0;0;1" keyTimes="0;0.6;0.92;1" dur="5s" repeatCount="indefinite"/></path>')
    o.append(f'<circle r="8" fill="#fff" filter="url(#glowsm)"><animateMotion dur="5s" repeatCount="indefinite" path="{d}" keyPoints="0;1;1" keyTimes="0;0.6;1" calcMode="linear"/></circle>')
    o.append(f'<text class="m" x="{x0-14}" y="{(yb+yt)/2+5}" text-anchor="end" font-size="13" letter-spacing="2" fill="{MUTED}" transform="rotate(-90 {x0-14} {(yb+yt)/2})">RISK</text>')
    o.append(f'<text class="m" x="{xm}" y="{yb+30}" text-anchor="middle" font-size="13" letter-spacing="3" fill="{MUTED}">PREDICTOR</text>')
    o.append(f'<text class="m" x="{w/2}" y="{h-26}" text-anchor="middle" font-size="13" letter-spacing="4" fill="{MUTED}">ILLUSTRATION OF THE MODELING APPROACH  ·  NOT STUDY DATA</text>')
    o.append('</svg>')
    write("research-markov.svg", "\n".join(o))


# ------------------------------------------------------------------ promptpilot flow
def promptpilot():
    w, h = 1200, 330
    o = [svg_open(w, h, "PromptPilot workflow: library, playground, compare lab, versions, analytics"), defs(w, h)]
    o.append(backdrop(w, h, 11, 18))
    o.append(f'<text class="t" x="60" y="62" font-size="30" font-weight="700" letter-spacing="8" fill="{INK}" filter="url(#glow)">PROMPTPILOT</text>')
    o.append(f'<text class="m" x="62" y="90" font-size="14" letter-spacing="4" fill="{MUTED}">PROMPT ENGINEERING WORKSPACE  ·  WORKFLOW</text>')
    steps = [("01", "Library", "write &amp; organize", BLUE), ("02", "Playground", "run with Gemini", VIOLET),
             ("03", "Compare Lab", "side by side", CYAN), ("04", "Versions", "track revisions", VIOLET),
             ("05", "Analytics", "review runs", BLUE)]
    bw, gap, x0, y0, bh = 190, 40, 60, 128, 150
    for i, (k, t, sub, col) in enumerate(steps):
        x = x0 + i * (bw + gap)
        o.append(f'<rect x="{x}" y="{y0}" width="{bw}" height="{bh}" rx="16" fill="url(#card)" stroke="{LINE}" stroke-width="2"/>')
        o.append(f'<rect x="{x+20}" y="{y0}" width="{bw-40}" height="4" rx="2" fill="{col}" filter="url(#glowsm)"/>')
        o.append(f'<text class="m" x="{x+20}" y="{y0+34}" font-size="13" letter-spacing="3.5" fill="{MUTED}">STEP {k}</text>')
        o.append(f'<text class="t" x="{x+20}" y="{y0+72}" font-size="25" font-weight="700" fill="{INK}">{t}</text>')
        o.append(f'<text class="t" x="{x+20}" y="{y0+100}" font-size="18" fill="{MUTED}">{sub}</text>')
        for j in range(8):  # tiny activity bars
            o.append(f'<rect x="{x+20+j*17}" y="{y0+bh-18}" width="10" height="6" rx="2" fill="{col}"><animate attributeName="height" values="4;18;4" dur="2.6s" begin="-{(i*0.4+j*0.3):.1f}s" repeatCount="indefinite"/>'
                     f'<animate attributeName="y" values="{y0+bh-16};{y0+bh-30};{y0+bh-16}" dur="2.6s" begin="-{(i*0.4+j*0.3):.1f}s" repeatCount="indefinite"/></rect>')
        if i < len(steps) - 1:
            ax, bx = x + bw, x + bw + gap
            my = y0 + bh / 2
            o.append(f'<line x1="{ax}" y1="{my}" x2="{bx}" y2="{my}" stroke="{LINE}" stroke-width="3"/>')
            o.append(f'<line class="fd" x1="{ax}" y1="{my}" x2="{bx}" y2="{my}" stroke="{CYAN}" stroke-width="3"/>')
            o.append(travel(f"M{ax},{my} L{bx},{my}", 1.4, i * 0.3, 4))
    full = f"M{x0},{y0+bh+26} H{w-60}"
    o.append(f'<rect x="{x0}" y="{y0+bh+25}" width="{w-120}" height="2.5" fill="url(#rule)"/>')
    o.append(travel(full, 5, 0, 4))
    o.append('</svg>')
    write("promptpilot-flow.svg", "\n".join(o))


# ------------------------------------------------------------------ achievements
def achievements():
    w, h = 1200, 400
    o = [svg_open(w, h, "Certifications and achievements"), defs(w, h)]
    o.append(backdrop(w, h, 13))
    o.append(title_block(w, "ACHIEVEMENTS", "CERTIFICATION  /  EVENTS  /  RESEARCH  /  LEADERSHIP", 66))
    data = [("CERTIFICATION", "TESDA NC II", ["Computer Systems", "Servicing"], BLUE, "chip"),
            ("EVENT  ·  2026", "Google I/O Extended", ["Cagayan de Oro City", "September 5, 2026"], VIOLET, "io"),
            ("PUBLICATION", "Published Research", ["Blood pressure", "transition modeling"], CYAN, "doc"),
            ("BEYOND CODE", "Leadership &amp; Media", ["Public speaking,", "broadcasting, creative"], VIOLET, "people")]
    cw, gap, x0, y0, ch = 268, 28, 22, 168, 200
    for i, (k, t, ls, col, icon) in enumerate(data):
        x = x0 + i * (cw + gap)
        o.append(card(x, y0, cw, ch, k, t, ls, tsize=21, lsize=18, accent=col))
        ix, iy = x + cw - 52, y0 + 12
        g = f'<g transform="translate({ix},{iy}) scale(0.68)" fill="none" stroke="{col}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
        if icon == "chip":
            g += '<rect x="8" y="8" width="28" height="28" rx="5"/><rect x="16" y="16" width="12" height="12" rx="2" fill="%s" opacity="0.5"/>' % col
            g += ''.join(f'<path d="M{a} 8v-5M{a} 36v5M8 {a}h-5M36 {a}h5"/>' for a in (15, 22, 29))
        elif icon == "io":
            g += f'<rect x="2" y="8" width="40" height="28" rx="8"/><text x="22" y="28" text-anchor="middle" font-size="15" font-weight="700" fill="{col}" stroke="none" class="m">I/O</text>'
        elif icon == "doc":
            g += '<path d="M10 4h18l8 8v28H10z"/><path d="M16 20h14M16 27h14M16 34h8"/>'
        else:
            g += '<circle cx="22" cy="14" r="6"/><circle cx="8" cy="30" r="5"/><circle cx="36" cy="30" r="5"/><path d="M18 19l-7 7M26 19l7 7"/>'
        g += f'<circle cx="38" cy="6" r="3.5" fill="{col}" stroke="none" class="pulse" style="animation-delay:-{i*0.5}s"/></g>'
        o.append(g)
    o.append('</svg>')
    write("achievements.svg", "\n".join(o))


# ------------------------------------------------------------------ footer
def footer():
    w, h = 1200, 190
    logo, (lw, lh) = data_uri("logo-horizontal.png", 560)
    o = [svg_open(w, h, "RETL logo footer"), defs(w, h)]
    o.append(backdrop(w, h, 21, 16, corners=False))
    tw = 300
    th = tw * lh / lw
    o.append(f'<image xlink:href="{logo}" x="{w/2-tw/2}" y="30" width="{tw}" height="{th:.0f}"/>')
    for side, sgn in (("L", -1), ("R", 1)):
        x1 = w / 2 + sgn * 190
        x2 = w / 2 + sgn * 540
        o.append(f'<line x1="{x1}" y1="{30+th/2:.0f}" x2="{x2}" y2="{30+th/2:.0f}" stroke="{LINE}" stroke-width="2"/>')
        o.append(f'<line class="fd" x1="{x1}" y1="{30+th/2:.0f}" x2="{x2}" y2="{30+th/2:.0f}" stroke="{VIOLET}" stroke-width="2"/>')
        o.append(travel(f"M{x1},{30+th/2:.0f} L{x2},{30+th/2:.0f}", 3, 0 if sgn < 0 else 1.5, 4))
    o.append(f'<text class="m" x="{w/2}" y="{h-48}" text-anchor="middle" font-size="15" letter-spacing="5" fill="{MUTED}">STUDENT DEVELOPER  ·  RESEARCHER  ·  ASPIRING SOFTWARE ENGINEER</text>')
    o.append(f'<text class="m" x="{w/2}" y="{h-24}" text-anchor="middle" font-size="13" letter-spacing="5" fill="{LINE.replace("26336b","4b5a96")}">CAGAYAN DE ORO  ·  PHILIPPINES</text>')
    o.append('</svg>')
    write("footer.svg", "\n".join(o))


if __name__ == "__main__":
    typing(); divider(); focus(); stack(); research(); promptpilot(); achievements(); footer()
