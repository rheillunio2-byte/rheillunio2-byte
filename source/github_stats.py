#!/usr/bin/env python3
"""Builds the animated GitHub statistics graphics in ../assets.

    python3 github_stats.py <username>          # live data (needs GITHUB_TOKEN, see below)
    python3 github_stats.py --placeholder       # empty "syncing" state (committed as the first seed)
    python3 github_stats.py --demo              # random sample data, for design previews only

Outputs (self-contained animated SVGs, safe for <img> on GitHub):
    assets/github-stats.svg   stat tiles + top languages
    assets/github-3d.svg      isometric 3D contribution calendar ("contribution city")

Live data comes from the GitHub GraphQL API using the GITHUB_TOKEN environment variable (the
workflow in .github/workflows/github-stats.yml provides one automatically). Standard library only.
"""
import json, math, os, random, sys, urllib.request
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets")

BLUE, VIOLET, CYAN = "#3b82f6", "#8b5cf6", "#22d3ee"
INK, MUTED, LINE = "#e8edff", "#7f8db0", "#26336b"
# contribution levels, low -> high (flat ground tile first)
LEVELS = ["#141c45", "#3b5bdb", "#6d5df0", "#8b5cf6", "#22d3ee"]

QUERY = """
query($login:String!){
  user(login:$login){
    name
    followers{totalCount}
    following{totalCount}
    repositories(
      ownerAffiliations: [OWNER]
      privacy: PUBLIC
      isFork: false
      first: 100
    ){
      totalCount
      nodes{
        stargazerCount
        languages(first:6, orderBy:{field:SIZE, direction:DESC}){
          edges{size node{name color}}
        }
      }
    }
    contributionsCollection{
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      contributionCalendar{
        totalContributions
        weeks{
          contributionDays{date contributionCount weekday}
        }
      }
    }
  }
}
"""


# ---------------------------------------------------------------- data
def fetch(login):
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("GITHUB_TOKEN is not set")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "profile-readme-stats"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        payload = json.load(r)
    if "errors" in payload or not payload.get("data", {}).get("user"):
        raise SystemExit(f"GraphQL error: {payload.get('errors')}")
    u = payload["data"]["user"]
    repos = u["repositories"]["nodes"]
    langs = {}
    for rp in repos:
        for e in rp["languages"]["edges"]:
            n = e["node"]["name"]
            langs.setdefault(n, [0, e["node"]["color"] or "#8b5cf6"])[0] += e["size"]
    top = sorted(langs.items(), key=lambda kv: -kv[1][0])[:6]
    total = sum(v[0] for _, v in top) or 1
    cc = u["contributionsCollection"]
    weeks = [[d["contributionCount"] for d in w["contributionDays"]] for w in cc["contributionCalendar"]["weeks"]]
    dates = [[d["date"] for d in w["contributionDays"]] for w in cc["contributionCalendar"]["weeks"]]
    return {
        "repos": u["repositories"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in repos),
        "followers": u["followers"]["totalCount"],
        "commits": cc["totalCommitContributions"],
        "prs": cc["totalPullRequestContributions"],
        "issues": cc["totalIssueContributions"],
        "total": cc["contributionCalendar"]["totalContributions"],
        "weeks": weeks, "dates": dates,
        "langs": [(n, v[0] / total * 100, v[1]) for n, v in top],
    }


def demo():
    rnd = random.Random(5)
    weeks, dates = [], []
    d0 = date.today() - timedelta(days=52 * 7 + date.today().weekday() + 1)
    for w in range(53):
        weeks.append([max(0, int(rnd.gauss(2, 3))) if rnd.random() < 0.55 else 0 for _ in range(7)])
        dates.append([(d0 + timedelta(days=w * 7 + i)).isoformat() for i in range(7)])
    return {"repos": 17, "stars": 3, "followers": 3, "commits": 412, "prs": 21, "issues": 6,
            "total": sum(map(sum, weeks)), "weeks": weeks, "dates": dates,
            "langs": [("Python", 38, "#3572A5"), ("JavaScript", 27, "#f1e05a"), ("TypeScript", 17, "#3178c6"), ("CSS", 10, "#563d7c"), ("HTML", 8, "#e34c26")]}


def placeholder():
    return {"weeks": [[0] * 7 for _ in range(53)], "dates": None, "placeholder": True}


def streaks(weeks):
    flat = [c for w in weeks for c in w]
    best = cur = 0
    for c in flat:
        cur = cur + 1 if c > 0 else 0
        best = max(best, cur)
    # current streak counts back from the latest day (today may still be empty)
    trail = flat[:]
    while trail and trail[-1] == 0:
        trail.pop()
        break
    cur = 0
    for c in reversed(trail):
        if c > 0:
            cur += 1
        else:
            break
    return best, cur, max(flat) if flat else 0


# ---------------------------------------------------------------- svg helpers
def shade(hex_, k):
    h = hex_.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % (min(255, int(r * k)), min(255, int(g * k)), min(255, int(b * k)))


CSS = """
.t{font-family:'Segoe UI','Helvetica Neue',Arial,sans-serif}
.m{font-family:'SFMono-Regular',Consolas,'Liberation Mono','Courier New',monospace}
.rise{transform-box:fill-box;transform-origin:50% 100%;animation:rise 1.1s cubic-bezier(.2,.8,.2,1) both}
.pulse{animation:pulse 2.4s ease-in-out infinite}
.fd{stroke-dasharray:10 12;animation:flow2 1.4s linear infinite}
.scan{animation:scan 9s linear infinite}
@keyframes rise{from{transform:scaleY(0);opacity:0}to{transform:scaleY(1);opacity:1}}
@keyframes pulse{0%,100%{opacity:.35}50%{opacity:1}}
@keyframes flow2{to{stroke-dashoffset:-22}}
@keyframes scan{0%{transform:translateY(0)}100%{transform:translateY(var(--h))}}
@media (prefers-reduced-motion: reduce){.rise,.pulse,.fd,.scan{animation:none}}
"""


def head(w, h, title, desc):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{title}">\n'
            f'<title>{title}</title><desc>{desc}</desc>\n<defs>'
            '<radialGradient id="bg" cx="50%" cy="45%" r="80%"><stop offset="0" stop-color="#101a3d"/><stop offset="0.55" stop-color="#070b1c"/><stop offset="1" stop-color="#04060e"/></radialGradient>'
            '<linearGradient id="card" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0d1433"/><stop offset="1" stop-color="#080d22"/></linearGradient>'
            f'<linearGradient id="acc" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{BLUE}"/><stop offset="0.5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{CYAN}"/></linearGradient>'
            f'<linearGradient id="rule" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{VIOLET}" stop-opacity="0"/><stop offset="0.5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></linearGradient>'
            f'<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="{BLUE}" stroke-opacity="0.07" stroke-width="1"/></pattern>'
            '<filter id="glow" x="-30%" y="-60%" width="160%" height="220%"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
            '<filter id="glowsm" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
            f'<clipPath id="frame"><rect x="6" y="6" width="{w-12}" height="{h-12}" rx="22"/></clipPath>'
            f'</defs><style>{CSS}</style>\n')


def backdrop(w, h):
    L = 44
    return (f'<rect width="{w}" height="{h}" rx="24" fill="url(#bg)"/><rect width="{w}" height="{h}" rx="24" fill="url(#grid)"/>'
            f'<g clip-path="url(#frame)"><rect class="scan" style="--h:{h}px" x="0" y="-70" width="{w}" height="70" fill="{VIOLET}" opacity="0.05"/></g>'
            f'<rect x="6" y="6" width="{w-12}" height="{h-12}" rx="22" fill="none" stroke="#25306a" stroke-width="1.5"/>'
            f'<g stroke="url(#acc)" stroke-width="3.5" fill="none" filter="url(#glowsm)">'
            f'<path d="M6 {L+6}V28a22 22 0 0 1 22-22h{L}"/><path d="M{w-6-L-22} 6h{L}a22 22 0 0 1 22 22v{L-16}"/>'
            f'<path d="M6 {h-L-6}v{L-16}a22 22 0 0 0 22 22h{L}"/><path d="M{w-6-L-22} {h-6}h{L}a22 22 0 0 0 22-22v-{L-16}"/></g>\n')


def title(w, t, sub, y=62):
    return (f'<text class="t" x="{w/2}" y="{y}" text-anchor="middle" font-size="34" font-weight="700" letter-spacing="9" fill="{INK}" filter="url(#glow)">{t}</text>'
            f'<text class="m" x="{w/2}" y="{y+30}" text-anchor="middle" font-size="14" letter-spacing="4" fill="{MUTED}">{sub}</text>'
            f'<rect x="{w/2-280}" y="{y+46}" width="560" height="3" fill="url(#rule)"/><path d="M{w/2} {y+39}l8 10-8 10-8-10z" fill="{VIOLET}" filter="url(#glowsm)"/>\n')


def fmt(n):
    return f"{n:,}" if isinstance(n, int) else "—"


# ---------------------------------------------------------------- 3D contribution city
def city(d):
    w, h = 1200, 640
    weeks = d["weeks"]
    ph = d.get("placeholder")
    best, cur, peak = streaks(weeks)
    o = [head(w, h, "GitHub contribution city",
              "Isometric 3D view of the last year of GitHub contributions" if not ph else "Isometric 3D contribution calendar, waiting for the first data sync"),
         backdrop(w, h),
         title(w, "CONTRIBUTION CITY", "THE LAST 12 MONTHS, IN 3D" if not ph else "SYNCS DAILY VIA GITHUB ACTIONS")]
    # stat strip
    stats = [("TOTAL", fmt(d.get("total")) if not ph else "—", CYAN), ("LONGEST STREAK", f"{best} days" if not ph else "—", VIOLET),
             ("CURRENT STREAK", f"{cur} days" if not ph else "—", BLUE), ("BEST DAY", fmt(peak) if not ph else "—", CYAN)]
    sw, sx0 = 250, 60
    for i, (k, v, c) in enumerate(stats):
        x = sx0 + i * ((w - 120 - sw) / 3)
        o.append(f'<rect x="{x:.0f}" y="152" width="{sw}" height="62" rx="14" fill="url(#card)" stroke="{LINE}" stroke-width="2"/>'
                 f'<rect x="{x+20:.0f}" y="152" width="{sw-40}" height="3.5" rx="2" fill="{c}" filter="url(#glowsm)"/>'
                 f'<text class="m" x="{x+20:.0f}" y="178" font-size="11" letter-spacing="3" fill="{MUTED}">{k}</text>'
                 f'<text class="t" x="{x+20:.0f}" y="203" font-size="22" font-weight="700" fill="{INK}">{v}</text>')
    # isometric grid (weeks run right-down, days run left-down => both axes face the viewer)
    ax, ay, bx, by = 17.0, 3.3, -7.5, 8.5
    n_w = len(weeks)
    maxc = max([c for w_ in weeks for c in w_] + [1])
    HMAX = 100
    # horizontal extent -> centre it
    xs = [wk * ax + dy * bx for wk in range(n_w + 1) for dy in (0, 7)]
    ox = w / 2 - (min(xs) + max(xs)) / 2
    oy = 342
    inset = 0.09
    def P(wk, dy):
        return ox + wk * ax + dy * bx, oy + wk * ay + dy * by
    # ground plate
    corners = [P(-0.4, -0.4), P(n_w + 0.4, -0.4), P(n_w + 0.4, 7.4), P(-0.4, 7.4)]
    o.append(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in corners)}" fill="#0a1030" stroke="{LINE}" stroke-width="2" opacity="0.9"/>')
    o.append(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in corners)}" fill="none" stroke="url(#acc)" stroke-width="2" opacity="0.7" filter="url(#glowsm)"/>')
    for wk in range(n_w):
        for dy in range(len(weeks[wk])):
            c = weeks[wk][dy]
            lvl = 0 if c == 0 else min(4, 1 + int(3 * (c - 1) / max(1, maxc - 1) + 0.5)) if maxc > 1 else 1
            if ph:
                lvl = 0
            col = LEVELS[lvl]
            ht = 3 if c == 0 else 6 + (c / maxc) ** 0.8 * HMAX
            x0, y0 = wk + inset, dy + inset
            x1, y1 = wk + 1 - inset, dy + 1 - inset
            p00, p10, p01, p11 = P(x0, y0), P(x1, y0), P(x0, y1), P(x1, y1)
            up = lambda p: (p[0], p[1] - ht)
            t = [up(p00), up(p10), up(p11), up(p01)]
            rf = [p10, p11, up(p11), up(p10)]
            lf = [p01, p11, up(p11), up(p01)]
            pts = lambda ps: " ".join(f"{x:.1f},{y:.1f}" for x, y in ps)
            delay = wk * 0.025 + dy * 0.012
            anim = f'<animate attributeName="opacity" values="1;0.55;1" dur="6s" begin="-{(wk*0.11) % 6:.2f}s" repeatCount="indefinite"/>' if (c > 0 or ph) else ""
            o.append(f'<g class="rise" style="animation-delay:{delay:.2f}s">'
                     f'<polygon points="{pts(lf)}" fill="{shade(col, 0.55)}"/><polygon points="{pts(rf)}" fill="{shade(col, 0.75)}"/>'
                     f'<polygon points="{pts(t)}" fill="{col}">{anim}</polygon></g>')
    if ph:  # scanning light band so the empty state still feels alive
        poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in corners)
        band = " ".join(f"{x:.1f},{y:.1f}" for x, y in (P(-0.4, -0.4), P(3, -0.4), P(3, 7.4), P(-0.4, 7.4)))
        o.append(f'<clipPath id="plate"><polygon points="{poly}"/></clipPath>'
                 f'<g clip-path="url(#plate)"><polygon points="{band}" fill="{CYAN}" opacity="0.35" filter="url(#glowsm)">'
                 f'<animateTransform attributeName="transform" type="translate" from="0 0" to="{n_w*ax:.0f} {n_w*ay:.0f}" dur="4.5s" repeatCount="indefinite"/></polygon></g>')
    cap = "Each tower is one day. Taller and brighter means more contributions." if not ph else "First sync pending. Push this repo or run the workflow once and the city builds itself."
    o.append(f'<text class="m" x="{w/2}" y="{h-26}" text-anchor="middle" font-size="13" letter-spacing="3" fill="{MUTED}">{cap.upper()}</text>')
    o.append('</svg>')
    return "\n".join(o)


# ---------------------------------------------------------------- stats + languages
def tile(x, y, w_, h_, k, v, col, icon):
    return (f'<g><rect x="{x}" y="{y}" width="{w_}" height="{h_}" rx="16" fill="url(#card)" stroke="{LINE}" stroke-width="2"/>'
            f'<rect x="{x+20}" y="{y}" width="{w_-40}" height="4" rx="2" fill="{col}" filter="url(#glowsm)"/>'
            f'<g transform="translate({x+w_-56},{y+h_-58}) scale(0.9)" fill="none" stroke="{col}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" opacity="0.9">{icon}'
            f'<circle cx="30" cy="-2" r="3" fill="{col}" stroke="none" class="pulse"/></g>'
            f'<text class="m" x="{x+22}" y="{y+36}" font-size="12" letter-spacing="3.5" fill="{MUTED}">{k}</text>'
            f'<text class="t" x="{x+22}" y="{y+84}" font-size="42" font-weight="800" fill="{INK}" filter="url(#glowsm)">{v}</text></g>\n')


ICONS = {
    "repo": '<path d="M4 4h18a2 2 0 0 1 2 2v20H6a2 2 0 0 1-2-2z"/><path d="M4 22h20M10 4v10l3-2 3 2V4"/>',
    "star": '<path d="M14 2l3.6 7.6 8.2 1-6 5.7 1.6 8.2L14 20.4 6.6 24.5l1.6-8.2-6-5.7 8.2-1z" transform="scale(.95)"/>',
    "people": '<circle cx="14" cy="9" r="5"/><path d="M4 26c0-6 4-9 10-9s10 3 10 9"/>',
    "commit": '<circle cx="14" cy="14" r="5"/><path d="M0 14h9M19 14h9"/>',
    "pr": '<circle cx="7" cy="6" r="3"/><circle cx="7" cy="24" r="3"/><circle cx="22" cy="24" r="3"/><path d="M7 9v12M22 21V12a5 5 0 0 0-5-5h-4M16 3l-3 4 3 4"/>',
    "issue": '<circle cx="14" cy="14" r="11"/><path d="M14 8v7"/><circle cx="14" cy="20" r="1.4"/>',
}


def stats(d):
    w, h = 1200, 470
    ph = d.get("placeholder")
    o = [head(w, h, "GitHub statistics", "Public repositories, stars, followers, contributions and top languages" if not ph else "GitHub statistics, waiting for the first data sync"),
         backdrop(w, h), title(w, "GITHUB STATS", "LIVE FROM THE GITHUB API" if not ph else "SYNCS DAILY VIA GITHUB ACTIONS")]
    items = [("PUBLIC REPOS", d.get("repos"), BLUE, "repo"), ("STARS EARNED", d.get("stars"), VIOLET, "star"), ("FOLLOWERS", d.get("followers"), CYAN, "people"),
             ("COMMITS · 12 MO", d.get("commits"), CYAN, "commit"), ("PULL REQUESTS", d.get("prs"), BLUE, "pr"), ("ISSUES", d.get("issues"), VIOLET, "issue")]
    tw, th, gap, x0, y0 = 200, 118, 18, 44, 156
    for i, (k, v, c, ic) in enumerate(items):
        x = x0 + (i % 3) * (tw + gap)
        y = y0 + (i // 3) * (th + gap)
        o.append(tile(x, y, tw, th, k, fmt(v) if isinstance(v, int) else "—", c, ICONS[ic]))
    # languages panel
    px, py, pw, phh = 704, 156, 452, 254
    o.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{phh}" rx="16" fill="url(#card)" stroke="{LINE}" stroke-width="2"/>'
             f'<rect x="{px+24}" y="{py}" width="{pw-48}" height="4" rx="2" fill="{VIOLET}" filter="url(#glowsm)"/>'
             f'<text class="m" x="{px+24}" y="{py+36}" font-size="12" letter-spacing="3.5" fill="{MUTED}">TOP LANGUAGES</text>')
    bx, bw = px + 24, pw - 48
    o.append(f'<clipPath id="lb"><rect x="{bx}" y="{py+56}" width="{bw}" height="16" rx="8"/></clipPath>')
    o.append(f'<rect x="{bx}" y="{py+56}" width="{bw}" height="16" rx="8" fill="#0b1230" stroke="{LINE}" stroke-width="1.5"/>')
    langs = d.get("langs")
    if langs:
        o.append('<g clip-path="url(#lb)">')
        cx = bx
        for n, pct, col in langs:
            ww = bw * pct / sum(p for _, p, _ in langs)
            o.append(f'<rect x="{cx:.1f}" y="{py+56}" width="0" height="16" fill="{col}"><animate attributeName="width" from="0" to="{ww:.1f}" dur="1.2s" fill="freeze" begin="0.2s"/></rect>')
            cx += ww
        o.append(f'<rect y="{py+56}" width="120" height="16" fill="#fff" opacity="0.18"><animate attributeName="x" values="{bx-120};{bx+bw}" dur="3.5s" repeatCount="indefinite"/></rect></g>')
        tot = sum(p for _, p, _ in langs)
        for i, (n, pct, col) in enumerate(langs):
            col_x = bx + (i % 2) * (bw / 2)
            yy = py + 108 + (i // 2) * 44
            o.append(f'<circle cx="{col_x+8:.0f}" cy="{yy-5}" r="6" fill="{col}"><animate attributeName="opacity" values="0.4;1;0.4" dur="3s" begin="-{i*0.5}s" repeatCount="indefinite"/></circle>'
                     f'<text class="t" x="{col_x+24:.0f}" y="{yy}" font-size="18" fill="#d6defa">{n}</text>'
                     f'<text class="m" x="{col_x+bw/2-30:.0f}" y="{yy}" text-anchor="end" font-size="15" fill="{MUTED}">{pct/tot*100:.1f}%</text>')
    else:
        o.append(f'<g clip-path="url(#lb)"><rect y="{py+56}" width="140" height="16" fill="url(#acc)" opacity="0.7"><animate attributeName="x" values="{bx-140};{bx+bw}" dur="2.4s" repeatCount="indefinite"/></rect></g>')
        for i in range(6):
            col_x = bx + (i % 2) * (bw / 2)
            yy = py + 108 + (i // 2) * 44
            o.append(f'<circle cx="{col_x+8:.0f}" cy="{yy-5}" r="6" fill="{LINE}"><animate attributeName="opacity" values="0.3;1;0.3" dur="2.4s" begin="-{i*0.4}s" repeatCount="indefinite"/></circle>'
                     f'<rect x="{col_x+24:.0f}" y="{yy-14}" width="{90+(i*23)%50}" height="14" rx="7" fill="{LINE}"><animate attributeName="opacity" values="0.4;1;0.4" dur="2.4s" begin="-{i*0.4}s" repeatCount="indefinite"/></rect>')
    o.append(f'<text class="m" x="{w/2}" y="{h-22}" text-anchor="middle" font-size="13" letter-spacing="3" fill="{MUTED}">PUBLIC REPOSITORIES · LAST 12 MONTHS OF ACTIVITY</text>')
    o.append('</svg>')
    return "\n".join(o)


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    if arg == "--placeholder":
        data = placeholder()
    elif arg == "--demo":
        data = demo()
    elif arg:
        data = fetch(arg)
    else:
        raise SystemExit(__doc__)
    outdir = os.environ.get("STATS_OUT", OUT)
    os.makedirs(outdir, exist_ok=True)
    for name, fn in (("github-stats.svg", stats), ("github-3d.svg", city)):
        with open(os.path.join(outdir, name), "w", encoding="utf-8") as f:
            f.write(fn(data))
        print(name, os.path.getsize(os.path.join(outdir, name)) // 1024, "KB")


if __name__ == "__main__":
    main()
