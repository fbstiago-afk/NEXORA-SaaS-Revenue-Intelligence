# -*- coding: utf-8 -*-
"""Gera backgrounds 1920x1080 (glass panels + menu lateral), logo negativo e home. Uso: python gerar_assets.py <uploads_dir> <out_dir>"""
import sys, os, math
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

UP, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
W, H = 1920, 1080
S = 2  # supersampling
F_INTER = "/usr/share/fonts/opentype/inter/Inter-%s.otf"
F_POP = "/usr/share/fonts/truetype/google-fonts/Poppins-%s.ttf"


def font(kind, w, size):
    return ImageFont.truetype((F_INTER if kind == "i" else F_POP) % w, size * S)


def find(name):
    for f in os.listdir(UP):
        if name in f:
            return os.path.join(UP, f)
    raise FileNotFoundError(name)


# ------------------------------------------------ logo negativo
lg = Image.open(find("Logo_Nexora")).convert("RGBA")
px = lg.load()
for y in range(lg.height):
    for x in range(lg.width):
        r, g, b, a = px[x, y]
        if a == 0:
            continue
        mx, mn = max(r, g, b), min(r, g, b)
        if mx - mn < 70 and mx < 140:
            px[x, y] = (255, 255, 255, a)  # texto navy -> branco (versão negativa)
for _ in []:
    pass
bbox = lg.getbbox()
lg = lg.crop(bbox)
lg.save(os.path.join(OUT, "nexora_logo_negativo.png"))
# símbolo isolado (N) — parte esquerda
sym = lg.crop((0, 0, int(lg.height * 0.95), lg.height))
sym = sym.crop(sym.getbbox())
sym.save(os.path.join(OUT, "nexora_simbolo.png"))

# ------------------------------------------------ base wallpaper
wp = Image.open(find("09_03_09")).convert("RGB").resize((W * S, H * S), Image.LANCZOS)
dark = Image.new("RGB", wp.size, (5, 13, 32))
base = Image.blend(wp, dark, 0.80)
# vinheta / gradiente vertical sutil
grad = Image.new("L", (1, H * S))
for y in range(H * S):
    grad.putpixel((0, y), int(70 * (y / (H * S)) ** 1.6))
grad = grad.resize(base.size)
base = Image.composite(dark, base, grad)


def glass(img, box, r=18, fill=(10, 26, 60, 150), border=(0, 184, 245, 80), glow=True, accent=True):
    x0, y0, x1, y1 = [v * S for v in box]
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    if glow:
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle((x0, y0 + 6 * S, x1, y1 + 6 * S), r * S, fill=(0, 0, 0, 110))
        sh = sh.filter(ImageFilter.GaussianBlur(14 * S))
        lay = Image.alpha_composite(lay, sh)
        d = ImageDraw.Draw(lay)
    d.rounded_rectangle((x0, y0, x1, y1), r * S, fill=fill, outline=border, width=1 * S)
    if accent:  # brilho no topo cyan->violeta
        ln = Image.new("RGBA", img.size, (0, 0, 0, 0))
        dl = ImageDraw.Draw(ln)
        w = x1 - x0
        for i in range(int(w * .55)):
            t = i / (w * .55)
            c = (int(0 + t * 103), int(184 - t * 130), int(245), int(200 * (1 - t) ** 0.7))
            dl.line((x0 + r * S + i, y0, x0 + r * S + i + 1, y0), fill=c, width=2 * S)
        lay = Image.alpha_composite(lay, ln)
    return Image.alpha_composite(img, lay)


# ------------------------------------------------ ícones de linha
def icon(d, kind, cx, cy, col, s=11):
    w = int(2.2 * S)
    X = lambda v: cx + v * S
    Y = lambda v: cy + v * S
    if kind == "home":
        d.line([(X(-s), Y(0)), (X(0), Y(-s)), (X(s), Y(0))], fill=col, width=w, joint="curve")
        d.line([(X(-s + 3), Y(-2)), (X(-s + 3), Y(s)), (X(s - 3), Y(s)), (X(s - 3), Y(-2))], fill=col, width=w, joint="curve")
    elif kind == "exec":
        for i, h in enumerate([5, 10, 15]):
            x = -8 + i * 8
            d.rounded_rectangle((X(x - 2.5), Y(s - h), X(x + 2.5), Y(s)), 1 * S, outline=col, width=w)
    elif kind == "revenue":
        d.ellipse((X(-s), Y(-s), X(s), Y(s)), outline=col, width=w)
        f = ImageFont.truetype(F_INTER % "Bold", 13 * S)
        d.text((X(0), Y(0)), "$", font=f, fill=col, anchor="mm")
    elif kind == "customer":
        d.ellipse((X(-5), Y(-s), X(5), Y(-1)), outline=col, width=w)
        d.arc((X(-s), Y(1), X(s), Y(s + 14)), 180, 360, fill=col, width=w)
    elif kind == "growth":
        d.line([(X(-s), Y(s - 2)), (X(-3), Y(1)), (X(2), Y(5)), (X(s), Y(-s + 2))], fill=col, width=w, joint="curve")
        d.line([(X(s - 7), Y(-s + 2)), (X(s), Y(-s + 2)), (X(s), Y(-s + 9))], fill=col, width=w, joint="curve")
    elif kind == "filter":
        d.polygon([(X(-s), Y(-s + 2)), (X(s), Y(-s + 2)), (X(3), Y(1)), (X(3), Y(s)), (X(-3), Y(s - 3)), (X(-3), Y(1))], outline=col, width=w)


NAV = [("home", "Início", "Home"), ("exec", "Executive SaaS", "Visão executiva"),
       ("revenue", "Revenue Intelligence", "Receita e expansão"), ("customer", "Customer & Retention", "Clientes e retenção"),
       ("growth", "Growth & Unit Econ.", "Aquisição e eficiência")]
NAV_Y0, NAV_H, NAV_GAP = 196, 60, 10
SIDE_W = 248


def sidebar(img, active):
    img = glass(img, (14, 14, SIDE_W - 6, H - 14), r=22, fill=(6, 16, 40, 175), border=(70, 120, 220, 70), accent=False)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    # logo
    lw = 176
    l2 = lg.resize((lw * S, int(lg.height * lw / lg.width) * S), Image.LANCZOS)
    lay.paste(l2, (36 * S, 52 * S), l2)
    d.text((38 * S, 52 * S + l2.height + 14 * S), "SaaS REVENUE INTELLIGENCE", font=font("i", "SemiBold", 10), fill=(169, 187, 216, 230))
    d.line((36 * S, 150 * S, (SIDE_W - 30) * S, 150 * S), fill=(120, 150, 210, 60), width=S)
    d.text((38 * S, 166 * S), "NAVEGAÇÃO", font=font("i", "Bold", 9), fill=(110, 134, 179, 255))
    for i, (k, lab, sub) in enumerate(NAV):
        y = NAV_Y0 + i * (NAV_H + NAV_GAP)
        on = (i == active)
        if on:
            pill = Image.new("RGBA", img.size, (0, 0, 0, 0))
            dp = ImageDraw.Draw(pill)
            x0, x1 = 26 * S, (SIDE_W - 22) * S
            gl = Image.new("RGBA", img.size, (0, 0, 0, 0))
            ImageDraw.Draw(gl).rounded_rectangle((x0, y * S, x1, (y + NAV_H) * S), 14 * S, fill=(22, 120, 255, 120))
            gl = gl.filter(ImageFilter.GaussianBlur(10 * S))
            lay = Image.alpha_composite(lay, gl)
            # gradiente horizontal
            gw = x1 - x0
            grd = Image.new("RGBA", (gw, NAV_H * S))
            gd = ImageDraw.Draw(grd)
            for xx in range(gw):
                t = xx / gw
                gd.line((xx, 0, xx, NAV_H * S), fill=(int(22 + t * 81), int(120 - t * 66), int(255 - t * 10), 235))
            mask = Image.new("L", grd.size, 0)
            ImageDraw.Draw(mask).rounded_rectangle((0, 0, gw - 1, NAV_H * S - 1), 14 * S, fill=255)
            lay.paste(grd, (x0, y * S), mask)
            d = ImageDraw.Draw(lay)
        col = (255, 255, 255, 255) if on else (169, 187, 216, 235)
        icon(d, k, 52 * S, int((y + NAV_H / 2) * S), col)
        d.text((76 * S, (y + 12) * S), lab, font=font("i", "SemiBold" if on else "Medium", 14), fill=col)
        d.text((76 * S, (y + 33) * S), sub, font=font("i", "Regular", 10.5), fill=(225, 235, 255, 210) if on else (110, 134, 179, 255))
    # rodapé
    d.line((36 * S, (H - 128) * S, (SIDE_W - 30) * S, (H - 128) * S), fill=(120, 150, 210, 60), width=S)
    for j, t in enumerate(["CONNECT.", "AUTOMATE.", "GROW."]):
        d.text((38 * S, (H - 112 + j * 18) * S), t, font=font("i", "Bold", 11), fill=[(0, 184, 245, 255), (22, 120, 255, 255), (103, 54, 245, 255)][j])
    d.text((38 * S, (H - 46) * S), "Base fictícia · jan/24–out/26", font=font("i", "Regular", 10), fill=(110, 134, 179, 255))
    return Image.alpha_composite(img, lay)


# layout de painéis por página (x, y, w, h) em px 1920x1080
X0 = 280
PANELS = {
    "exec": [(X0, 334, 1062, 716), (1366, 334, 524, 346), (1366, 704, 524, 346)],
    "revenue": [(X0, 334, 1062, 410), (X0, 768, 1062, 282), (1366, 334, 524, 346), (1366, 704, 524, 346)],
    "customer": [(X0, 334, 1062, 716), (1366, 334, 524, 346), (1366, 704, 524, 346)],
    "growth": [(X0, 334, 1062, 340), (X0, 698, 1062, 352), (1366, 334, 524, 716)],
}
ORDER = ["exec", "revenue", "customer", "growth"]

for idx, pg in enumerate(ORDER):
    img = base.convert("RGBA")
    img = sidebar(img, idx + 1)
    for (x, y, w, h) in PANELS[pg]:
        img = glass(img, (x, y, x + w, y + h))
    img = img.resize((W, H), Image.LANCZOS).convert("RGB")
    img.save(os.path.join(OUT, f"bg_{pg}.png"), optimize=True)

# tooltip bg
tt = Image.new("RGBA", (360 * S, 240 * S), (0, 0, 0, 0))
tt = glass(tt, (0, 0, 359, 239), r=14, fill=(8, 21, 47, 245), border=(0, 184, 245, 140), glow=False)
tt.resize((360, 240), Image.LANCZOS).convert("RGB").save(os.path.join(OUT, "bg_tooltip.png"))

# filtro: painel lateral (sobreposição) — desenhado como imagem própria
fp = Image.new("RGBA", (420 * S, H * S), (0, 0, 0, 0))
fp = glass(fp, (0, 14, 406, H - 14), r=22, fill=(6, 16, 40, 248), border=(0, 184, 245, 120), glow=False)
dfp = ImageDraw.Draw(fp)
icon(dfp, "filter", 40 * S, 56 * S, (0, 184, 245, 255), s=10)
dfp.text((62 * S, 42 * S), "Filtros", font=font("p", "Bold", 20), fill=(255, 255, 255, 255))
dfp.text((62 * S, 72 * S), "Refine a análise · aplicados em todas as páginas", font=font("i", "Regular", 11), fill=(169, 187, 216, 255))
fp.resize((420, H), Image.LANCZOS).save(os.path.join(OUT, "painel_filtros.png"))

# ------------------------------------------------ HOME
hm = Image.open(find("09_03_39")).convert("RGBA").resize((W, H), Image.LANCZOS)
hm2 = hm.resize((W * S, H * S), Image.LANCZOS)
lay = Image.new("RGBA", hm2.size, (0, 0, 0, 0))
d = ImageDraw.Draw(lay)
lw = 240
l2 = lg.resize((lw * S, int(lg.height * lw / lg.width) * S), Image.LANCZOS)
lay.paste(l2, (494 * S, 52 * S), l2)
d.text((496 * S, 1000 * S), "Case de portfólio · empresa e dados fictícios · jan/2024 – out/2026",
       font=font("i", "Regular", 12), fill=(110, 134, 179, 255))
hm2 = Image.alpha_composite(hm2, lay)
hm2.resize((W, H), Image.LANCZOS).convert("RGB").save(os.path.join(OUT, "bg_home.png"), optimize=True)
print("ok", os.listdir(OUT))
