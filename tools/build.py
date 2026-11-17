import math, itertools, os, html
from fonts import face

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
os.makedirs(OUT, exist_ok=True)

BG = "#06080B"
PANEL = "#0A0F15"
LINE = "#1B2834"
POWDER = "#A9CCE8"
POWDER2 = "#D3E6F6"
INK = "#EEF4F9"
DIM = "#6F8597"
LILAC = "#BFB3EE"

esc = html.escape


def write(name, svg):
    p = os.path.join(OUT, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"{name:28s} {os.path.getsize(p)/1024:6.1f} KB")


# ---------------------------------------------------------------- tesseract
def tesseract_frames(cx, cy, scale, n=72, tilt=0.55):
    verts = list(itertools.product([-1, 1], repeat=4))
    edges = [
        (i, j)
        for i, j in itertools.combinations(range(16), 2)
        if sum(a != b for a, b in zip(verts[i], verts[j])) == 1
    ]
    frames_d, frames_pts = [], []
    for k in range(n):
        t = 2 * math.pi * k / n
        pts = []
        for x, y, z, w in verts:
            # 4D rotations: XW and YZ (both full turns -> seamless loop)
            x, w = x * math.cos(t) - w * math.sin(t), x * math.sin(t) + w * math.cos(t)
            y, z = y * math.cos(t) - z * math.sin(t), y * math.sin(t) + z * math.cos(t)
            # 4D -> 3D perspective
            f4 = 1 / (2.6 - w)
            x, y, z = x * f4, y * f4, z * f4
            # fixed 3D tilt for a nicer view
            y, z = y * math.cos(tilt) - z * math.sin(tilt), y * math.sin(tilt) + z * math.cos(tilt)
            x, z = x * math.cos(0.5) - z * math.sin(0.5), x * math.sin(0.5) + z * math.cos(0.5)
            # 3D -> 2D perspective
            f3 = 1 / (3.2 - z)
            pts.append((cx + x * f3 * scale * 3.2, cy + y * f3 * scale * 3.2))
        d = "".join(
            f"M{pts[i][0]:.1f} {pts[i][1]:.1f}L{pts[j][0]:.1f} {pts[j][1]:.1f}"
            for i, j in edges
        )
        frames_d.append(d)
        frames_pts.append(pts)
    frames_d.append(frames_d[0])
    frames_pts.append(frames_pts[0])
    return frames_d, frames_pts


def tesseract_svg(cx, cy, scale, dur=14, stroke=POWDER, dots=True, width=1.4, n=72):
    fd, fp = tesseract_frames(cx, cy, scale, n=n)
    out = [
        f'<path d="{fd[0]}" fill="none" stroke="{stroke}" stroke-width="{width}" '
        f'stroke-linecap="round" opacity=".9" filter="url(#soft)">'
        f'<animate attributeName="d" dur="{dur}s" repeatCount="indefinite" '
        f'values="{";".join(fd)}"/></path>'
    ]
    if dots:
        for v in range(16):
            xs = ";".join(f"{f[v][0]:.1f}" for f in fp)
            ys = ";".join(f"{f[v][1]:.1f}" for f in fp)
            out.append(
                f'<circle r="2.6" fill="{POWDER2}" cx="{fp[0][v][0]:.1f}" cy="{fp[0][v][1]:.1f}">'
                f'<animate attributeName="cx" dur="{dur}s" repeatCount="indefinite" values="{xs}"/>'
                f'<animate attributeName="cy" dur="{dur}s" repeatCount="indefinite" values="{ys}"/>'
                f"</circle>"
            )
    return "".join(out)


SOFT_FILTER = (
    '<filter id="soft" x="-20%" y="-20%" width="140%" height="140%">'
    '<feGaussianBlur stdDeviation="2.2" result="b"/>'
    '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
)


def corner_ticks(w, h, m=16, l=14, color=DIM):
    s = f'stroke="{color}" stroke-width="1.2" fill="none" opacity=".7"'
    return (
        f'<path {s} d="M{m} {m+l}V{m}H{m+l}M{w-m-l} {m}H{w-m}V{m+l}'
        f'M{w-m} {h-m-l}V{h-m}H{w-m-l}M{m+l} {h-m}H{m}V{h-m-l}"/>'
    )


def dot_grid(w, h, pid="dots", gap=22, color=LINE, drift=True):
    anim = (
        f'<animateTransform attributeName="patternTransform" type="translate" '
        f'from="0 0" to="{gap} {gap}" dur="9s" repeatCount="indefinite"/>'
        if drift
        else ""
    )
    return (
        f'<pattern id="{pid}" width="{gap}" height="{gap}" patternUnits="userSpaceOnUse">'
        f'<circle cx="2" cy="2" r="1.1" fill="{color}"/>{anim}</pattern>'
    )


# ---------------------------------------------------------------- header
def header():
    W, H = 1000, 340
    mono_top = "~/x-dimension  ·  dhaka, bangladesh  ·  utc+06:00"
    first, last = "Sk Shihan", "Fardin."
    tag = "AI builder  ·  founder @ X Dimension  ·  researcher"
    bn = "AI শিখি, AI শেখাই — বাংলায়।"
    aka = "aka shad"
    css = (
        face("PB", "Poppins-Bold", first)
        + face("PL", "Poppins-Light", tag)
        + face("LI", "Lora-Italic", last)
        + face("MO", "Mono", mono_top + aka + "building in every dimension")
        + """
.r{opacity:0;animation:rise .9s cubic-bezier(.2,.7,.2,1) forwards}
.d1{animation-delay:.15s}.d2{animation-delay:.45s}.d3{animation-delay:.75s}
.d4{animation-delay:1.05s}.d5{animation-delay:1.35s}
@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
.glow{animation:pulse 6s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:.55}50%{opacity:1}}
.scan{animation:scan 7s linear infinite}
@keyframes scan{from{transform:translateY(-20px)}to{transform:translateY(360px)}}
.caret{animation:blink 1s steps(1) infinite}
@keyframes blink{50%{opacity:0}}
"""
    )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Sk Shihan Fardin — AI builder, founder, researcher">
<defs><style>{css}</style>{SOFT_FILTER}{dot_grid(W,H)}
<radialGradient id="g1" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="{POWDER}" stop-opacity=".28"/><stop offset="1" stop-color="{POWDER}" stop-opacity="0"/></radialGradient>
<radialGradient id="g2" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="{LILAC}" stop-opacity=".14"/><stop offset="1" stop-color="{LILAC}" stop-opacity="0"/></radialGradient>
<linearGradient id="scanl" gradientUnits="userSpaceOnUse" x1="0" x2="{W}"><stop offset="0" stop-color="{POWDER}" stop-opacity="0"/><stop offset=".5" stop-color="{POWDER}" stop-opacity=".35"/><stop offset="1" stop-color="{POWDER}" stop-opacity="0"/></linearGradient>
<linearGradient id="namefill" x1="0" x2="1"><stop offset="0" stop-color="{POWDER2}"/><stop offset="1" stop-color="{LILAC}"/></linearGradient>
<clipPath id="card"><rect width="{W}" height="{H}" rx="20"/></clipPath>
</defs>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="{BG}"/>
<rect width="{W}" height="{H}" fill="url(#dots)"/>
<circle class="glow" cx="210" cy="172" r="190" fill="url(#g1)"/>
<circle cx="860" cy="60" r="260" fill="url(#g2)"/>
{tesseract_svg(210, 172, 108)}
<rect class="scan" x="0" y="0" width="{W}" height="1.5" fill="url(#scanl)"/>
</g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="20" fill="none" stroke="{LINE}"/>
{corner_ticks(W,H)}
<g font-family="MO" font-size="13" fill="{DIM}" letter-spacing=".5">
<text class="r d1" x="410" y="84">{esc(mono_top)}</text>
</g>
<text class="r d2" x="406" y="160" font-family="PB" font-size="66" fill="{INK}" letter-spacing="-1.5">{first}</text>
<text class="r d3" x="410" y="226" font-family="LI" font-size="68" fill="url(#namefill)" font-style="italic">{last}<tspan font-family="MO" font-size="15" fill="{DIM}" dx="16" dy="-10" font-style="normal">{aka}</tspan><tspan class="caret" font-family="MO" font-size="15" fill="{POWDER}" dy="0">_</tspan></text>
<text class="r d4" x="411" y="266" font-family="PL" font-size="17.5" fill="{POWDER2}" letter-spacing=".4">{esc(tag)}</text>
<g class="r d5">
<rect x="408" y="284" width="270" height="34" rx="17" fill="{PANEL}" stroke="{LINE}"/>
<circle cx="428" cy="301" r="4" fill="{POWDER}"><animate attributeName="opacity" values="1;.25;1" dur="2.4s" repeatCount="indefinite"/></circle>
<text x="442" y="306" font-family="MO" font-size="13.5" fill="{POWDER}">building in every dimension</text>
</g>
</svg>"""
    write("header.svg", svg)


# ---------------------------------------------------------------- section titles
SECTIONS = [
    ("01", "The human behind the commits", "who i am, in one breath"),
    ("02", "Current chapters", "what keeps me busy"),
    ("03", "Things I've built", "selected work"),
    ("04", "Toolbox", "what i build (and learn) with"),
    ("05", "Research & receipts", "papers, posters, certificates"),
    ("06", "GitHub pulse", "the numbers, live"),
]


def section_title(num, title, sub):
    W, H = 1000, 86
    label = f"D{num}"
    css = (
        face("MO", "Mono", label + sub + "/ ·")
        + face("LI", "Lora-Italic", title)
        + """
.r{opacity:0;animation:rise .8s ease forwards}
@keyframes rise{from{opacity:0;transform:translateX(-10px)}to{opacity:1;transform:none}}
.ln{stroke-dasharray:1000;stroke-dashoffset:1000;animation:draw 1.6s .2s ease forwards}
@keyframes draw{to{stroke-dashoffset:0}}
"""
    )
    tw = len(title) * 17.2 + 150  # rough end of title for the rule
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(title)}">
<defs><style>{css}</style>
<linearGradient id="rule" gradientUnits="userSpaceOnUse" x1="{min(tw, 900):.0f}" x2="{W}"><stop offset="0" stop-color="{POWDER}" stop-opacity=".8"/><stop offset="1" stop-color="{POWDER}" stop-opacity="0"/></linearGradient></defs>
<g class="r">
<rect x="2" y="22" width="58" height="30" rx="8" fill="{PANEL}" stroke="{LINE}"/>
<text x="31" y="42.5" text-anchor="middle" font-family="MO" font-size="14" fill="{POWDER}">{label}</text>
<text x="78" y="49" font-family="LI" font-size="34" fill="{INK}" font-style="italic">{esc(title)}</text>
<text x="80" y="74" font-family="MO" font-size="12.5" fill="{DIM}" letter-spacing=".6">/ {esc(sub)}</text>
</g>
<path class="ln" d="M{min(tw, 900):.0f} 39H{W-4}" stroke="url(#rule)" stroke-width="1.2"/>
</svg>"""
    write(f"d{num}.svg", svg)


# ---------------------------------------------------------------- python REPL "about me"
def repl():
    W = 1000
    lines = [
        ("p", ">>> ", "from bangladesh import Shad"),
        ("p", ">>> ", "me = Shad()"),
        ("p", ">>> ", "me.roles"),
        ("o", "", "['Founder @ X Dimension',"),
        ("o", "", "\u00a0'AI builder — LLM apps, automations, local AI',"),
        ("o", "", "\u00a0'ICE undergrad @ Daffodil International University']"),
        ("p", ">>> ", "me.currently_learning"),
        ("o", "", "'AI Engineering'"),
        ("p", ">>> ", "me.mission"),
        ("o", "", "'Build AI products people actually use.'"),
        ("p", ">>> ", "me.fun_fact"),
        ("o", "", "'Turned my tablet into a wireless pen for Windows.'"),
        ("p", ">>> ", ""),
    ]
    top = 52
    lh = 25
    H = top + lh * len(lines) + 30
    alltext = "".join(a + b for _, a, b in lines) + "shad@dhaka: ~ python3 — 80×24"
    css = (
        face("MO", "Mono", alltext)
        + face("MB", "Mono-Bold", ">>> ")
        + """
.l{opacity:0;animation:show .01s forwards}
@keyframes show{to{opacity:1}}
.caret{animation:blink 1s steps(1) infinite}
@keyframes blink{50%{opacity:0}}
"""
    )
    rows = []
    t = 0.4
    for i, (kind, prompt, text) in enumerate(lines):
        y = top + lh * (i + 1)
        delay = f"animation-delay:{t:.2f}s"
        if kind == "p":
            col = INK
            body = (
                f'<tspan font-family="MB" fill="{POWDER}">{esc(prompt)}</tspan>'
                f'<tspan fill="{col}">{esc(text)}</tspan>'
            )
            t += 0.55 if text else 0
        else:
            body = f'<tspan fill="{POWDER2}" opacity=".78">{esc(text)}</tspan>'
            t += 0.18
        if i == len(lines) - 1:
            body += f'<tspan class="caret" fill="{POWDER}">▍</tspan>'
        rows.append(f'<text class="l" style="{delay}" x="34" y="{y}">{body}</text>')
    # need ▍ glyph too
    css = css.replace(face("MO", "Mono", alltext), face("MO", "Mono", alltext + "▍"))
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="About me, as a Python REPL session">
<defs><style>{css}</style>{dot_grid(W,H,gap=26,drift=False)}</defs>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="16" fill="{BG}" stroke="{LINE}"/>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="16" fill="url(#dots)" opacity=".5"/>
<path d="M1 46H{W-1}" stroke="{LINE}"/>
<circle cx="28" cy="24" r="6" fill="#2A3946"/><circle cx="48" cy="24" r="6" fill="#2A3946"/><circle cx="68" cy="24" r="6" fill="{POWDER}" opacity=".8"/>
<text x="{W/2}" y="29" text-anchor="middle" font-family="MO" font-size="12.5" fill="{DIM}">shad@dhaka: ~ python3 — 80×24</text>
<g font-family="MO" font-size="15.5" style="white-space:pre" xml:space="preserve">
{''.join(rows)}
</g>
</svg>"""
    write("repl.svg", svg)


# ---------------------------------------------------------------- project covers
def cover(slug, title, kicker, motif, title_font="Poppins-Bold", title_family="PB"):
    W, H = 480, 250
    css = (
        face("PB", title_font, title)
        + face("MO", "Mono", kicker + motif.get("text", ""))
        + motif.get("css", "")
    )
    if motif.get("bn"):
        css += face("BN", "Bangla-Bold", motif["bn"])
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(title)}">
<defs><style>{css}</style>{SOFT_FILTER}{dot_grid(W,H,pid="cd",gap=18,drift=False)}
<radialGradient id="cg" cx="78%" cy="40%" r="60%"><stop offset="0" stop-color="{motif.get('glow', POWDER)}" stop-opacity=".22"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></radialGradient>
<clipPath id="cc"><rect width="{W}" height="{H}" rx="16"/></clipPath></defs>
<g clip-path="url(#cc)">
<rect width="{W}" height="{H}" fill="{BG}"/><rect width="{W}" height="{H}" fill="url(#cd)" opacity=".7"/>
<rect width="{W}" height="{H}" fill="url(#cg)"/>
{motif["art"]}
</g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="{LINE}"/>
<text x="26" y="40" font-family="MO" font-size="12" fill="{DIM}" letter-spacing="1">{esc(kicker)}</text>
<text x="24" y="{H-30}" font-family="{title_family}" font-size="{36 if len(title) < 13 else 30}" fill="{INK}" letter-spacing="-.5">{esc(title) if not motif.get('bn') else ''}</text>
{motif.get("title_svg", "")}
</svg>"""
    write(f"p-{slug}.svg", svg)


def covers():
    # FacultyMind — Bloom's taxonomy pyramid with nodes lighting up
    levels = ["remember", "understand", "apply", "analyze", "evaluate", "create"]
    art = []
    for i, lv in enumerate(levels):
        w = 190 - i * 28
        y = 172 - i * 24
        x = 372 - w / 2
        art.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="21" rx="5" fill="{PANEL}" stroke="{POWDER}" stroke-opacity=".35">'
            f'<animate attributeName="stroke-opacity" values=".25;.25;1;.25" keyTimes="0;{i/7:.2f};{(i+.6)/7:.2f};1" dur="5s" repeatCount="indefinite"/></rect>'
            f'<text x="372" y="{y+14.5}" text-anchor="middle" font-family="MO" font-size="10" fill="{POWDER2}" opacity=".85">{lv}</text>'
        )
    cover(
        "facultymind",
        "FacultyMind",
        "OFFLINE AI · OBE ACCREDITATION",
        {"art": "".join(art), "text": "".join(levels)},
    )

    # InkCast — a pen stroke that draws itself, with a tablet frame
    stroke = "M250 170 C 270 90, 330 80, 345 130 S 410 190, 440 100"
    art = f"""
<rect x="232" y="56" width="226" height="150" rx="14" fill="{PANEL}" stroke="{LINE}"/>
<path class="ink" d="{stroke}" fill="none" stroke="{POWDER}" stroke-width="5" stroke-linecap="round" filter="url(#soft)"/>
<path class="ink2" d="M262 186 L 300 186" fill="none" stroke="{LILAC}" stroke-width="4" stroke-linecap="round"/>
<circle r="6" fill="{INK}"><animateMotion dur="3.2s" repeatCount="indefinite" path="{stroke}" keyPoints="0;1;1" keyTimes="0;.7;1" calcMode="linear"/></circle>"""
    css = """.ink{stroke-dasharray:420;stroke-dashoffset:420;animation:ink 3.2s ease-in-out infinite}
@keyframes ink{0%{stroke-dashoffset:420}70%,100%{stroke-dashoffset:0}}
.ink2{stroke-dasharray:40;stroke-dashoffset:40;animation:ink2 3.2s ease-in-out infinite}
@keyframes ink2{0%,70%{stroke-dashoffset:40}90%,100%{stroke-dashoffset:0}}"""
    cover("inkcast", "InkCast", "TABLET → WINDOWS · LIVE INK", {"art": art, "css": css, "glow": LILAC})

    # hello-world — journal / terminal
    art = f"""
<rect x="240" y="58" width="210" height="136" rx="12" fill="{PANEL}" stroke="{LINE}"/>
<text font-family="MO" font-size="12" fill="{POWDER2}">
<tspan x="258" y="88" fill="{POWDER}">day 01</tspan><tspan x="310" y="88" opacity=".7">print("hello")</tspan>
<tspan x="258" y="112" fill="{POWDER}">day 02</tspan><tspan x="310" y="112" opacity=".7">for i in range</tspan>
<tspan x="258" y="136" fill="{POWDER}">day 03</tspan><tspan x="310" y="136" opacity=".7">def learn():</tspan>
<tspan x="258" y="160" fill="{POWDER}">day 04</tspan><tspan x="310" y="160" opacity=".7">streak +1</tspan></text>
<rect x="258" y="172" width="0" height="6" rx="3" fill="{POWDER}"><animate attributeName="width" values="0;174;174" keyTimes="0;.8;1" dur="4s" repeatCount="indefinite"/></rect>"""
    cover(
        "helloworld",
        "Hello World",
        "TAURI · RUST · REACT JOURNAL",
        {"art": art, "text": 'day0123print("hello")forirangedef learn():streak+1'},
    )

    # WSN fault detection — sensor mesh with one node flagged faulty
    nodes=[(262,92),(318,70),(380,88),(436,74),(290,146),(352,136),(414,150),(456,128),(320,196),(388,192),(440,190)]
    links=[(0,1),(1,2),(2,3),(0,4),(1,5),(2,5),(2,6),(3,7),(4,5),(5,6),(6,7),(4,8),(5,8),(5,9),(6,9),(6,10),(7,10),(8,9),(9,10)]
    art=[]
    for i,j in links:
        (x1,y1),(x2,y2)=nodes[i],nodes[j]
        bad = 6 in (i,j)
        art.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{"#E8A0A8" if bad else POWDER}" stroke-opacity="{.5 if bad else .35}" stroke-width="1.2"' + (' stroke-dasharray="4 4"' if bad else '') + '/>')
    for k,(x,y) in enumerate(nodes):
        if k==6:
            art.append(f'<circle cx="{x}" cy="{y}" r="14" fill="none" stroke="#E8A0A8"><animate attributeName="r" values="7;20" dur="1.6s" repeatCount="indefinite"/><animate attributeName="opacity" values="1;0" dur="1.6s" repeatCount="indefinite"/></circle>')
            art.append(f'<circle cx="{x}" cy="{y}" r="6" fill="#E8A0A8"/>')
            art.append(f'<text x="{x}" y="{y-14}" text-anchor="middle" font-family="MO" font-size="10" fill="#E8A0A8">fault</text>')
        else:
            art.append(f'<circle cx="{x}" cy="{y}" r="4.5" fill="{POWDER2}"><animate attributeName="opacity" values="1;.4;1" dur="{2+k%3*.7:.1f}s" repeatCount="indefinite"/></circle>')
    cover(
        "wsn",
        "WSN Fault Detection",
        "WIRELESS SENSOR NETWORKS · ML",
        {"art": "".join(art), "text": "fault", "glow": "#E8A0A8"},
    )

    # Plant recognition — leaf with scanning line
    leaf = "M300 190 C 300 120, 360 70, 440 66 C 436 150, 380 196, 300 190 Z"
    art = f"""<g transform="translate(14 -26)">
<path d="{leaf}" fill="{PANEL}" stroke="{POWDER}" stroke-width="2" opacity=".95"/>
<path d="M300 190 Q 360 140 430 74 M340 160 L 352 128 M370 132 L 392 124 M330 172 L 362 170 M362 144 L 380 150" stroke="{POWDER}" stroke-width="1.4" fill="none" opacity=".6"/>
<rect x="285" y="60" width="170" height="2" fill="{LILAC}" opacity=".9" filter="url(#soft)"><animate attributeName="y" values="60;196;60" dur="3.6s" repeatCount="indefinite"/></rect>
<text x="372" y="222" text-anchor="middle" font-family="MO" font-size="11" fill="{POWDER2}">leaf.jpg → species</text></g>"""
    cover(
        "plant",
        "Plant Recognition",
        "COMPUTER VISION · PYTHON",
        {"art": art, "text": "leaf.jpg → species", "glow": "#9FD9B9"},
    )


# ---------------------------------------------------------------- sign-off
def signoff():
    W, H = 1000, 230
    line1 = "Thanks for dropping into another dimension."
    bn = "আবার দেখা হবে"
    es = "see you in the next commit"
    css = (
        face("LI", "Lora-Italic", line1)
        + face("MO", "Mono", es)
        + f"""
.w{{fill:transparent;stroke:{POWDER2};stroke-width:.8;stroke-dasharray:600;stroke-dashoffset:600;
animation:write 3.2s ease forwards,fill 1s 2.6s forwards}}
@keyframes write{{to{{stroke-dashoffset:0}}}}
@keyframes fill{{to{{fill:{INK};stroke-width:0}}}}
.r{{opacity:0;animation:rise 1s 3s forwards}}
@keyframes rise{{to{{opacity:1}}}}
"""
    )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(line1)}">
<defs><style>{css}</style>{SOFT_FILTER}{dot_grid(W,H)}
<radialGradient id="sg" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="{POWDER}" stop-opacity=".22"/><stop offset="1" stop-color="{POWDER}" stop-opacity="0"/></radialGradient>
<clipPath id="sc"><rect width="{W}" height="{H}" rx="20"/></clipPath></defs>
<g clip-path="url(#sc)"><rect width="{W}" height="{H}" fill="{BG}"/><rect width="{W}" height="{H}" fill="url(#dots)"/>
<circle cx="500" cy="80" r="160" fill="url(#sg)"/>
{tesseract_svg(500, 66, 34, dur=12, width=1, dots=False, n=48)}</g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="20" fill="none" stroke="{LINE}"/>
<text class="w" x="500" y="150" text-anchor="middle" font-family="LI" font-size="40" font-style="italic">{esc(line1)}</text>
<g class="r">
<text x="500" y="192" text-anchor="middle" font-family="MO" font-size="12" fill="{DIM}" letter-spacing=".6">{esc(es)}</text>
</g>
</svg>"""
    write("signoff.svg", svg)


if __name__ == "__main__":
    header()
    for s in SECTIONS:
        section_title(*s)
    repl()
    covers()
    signoff()
