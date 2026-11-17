"""Subset local fonts to just the glyphs an SVG needs and return @font-face CSS
with the font embedded as base64 WOFF (GitHub serves README SVGs as <img>,
which can't load external fonts — so they must be embedded)."""
import base64, io
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

GF = "/usr/share/fonts/truetype/google-fonts/"
FONTS = {
    "Poppins-Bold": GF + "Poppins-Bold.ttf",
    "Poppins-Medium": GF + "Poppins-Medium.ttf",
    "Poppins-Light": GF + "Poppins-Light.ttf",
    "Poppins-Regular": GF + "Poppins-Regular.ttf",
    "Lora-Italic": (GF + "Lora-Italic-Variable.ttf", {"wght": 500}),
    "Lora": (GF + "Lora-Variable.ttf", {"wght": 500}),
    "Mono": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "Mono-Bold": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    "Bangla": "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    "Bangla-Bold": "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
}

_cache = {}


def _load(name):
    spec = FONTS[name]
    if isinstance(spec, tuple):
        path, axes = spec
        f = TTFont(path)
        f = instancer.instantiateVariableFont(f, axes)
    else:
        f = TTFont(spec)
    return f


def face(family, name, text):
    """CSS @font-face for `family` using local font `name`, subset to `text`."""
    f = _load(name)
    opts = subset.Options()
    opts.flavor = "woff"
    opts.layout_features = ["*"]
    opts.name_IDs = []
    opts.notdef_outline = True
    opts.hinting = False
    s = subset.Subsetter(opts)
    s.populate(text=text + " ")
    s.subset(f)
    buf = io.BytesIO()
    f.flavor = "woff"
    f.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return (
        f"@font-face{{font-family:'{family}';"
        f"src:url(data:font/woff;base64,{b64}) format('woff');}}"
    )
