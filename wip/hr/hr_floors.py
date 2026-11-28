import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
rng = np.random.default_rng(5)
def noise(w, h, amt, blur=0.6):
    n = rng.normal(0, amt, (h, w)); im = Image.fromarray(np.clip(n + 128, 0, 255).astype('uint8'))
    return np.array(im.filter(ImageFilter.GaussianBlur(blur))).astype(int) - 128
def tint(arr, rgb): return np.clip(np.stack([arr + c for c in rgb], -1), 0, 255).astype('uint8')
SAGE = (184, 200, 168)
F = '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'; FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; FS = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
NAME = 'Huntington Ridge'
def sage(w, h): return Image.fromarray(tint(noise(w, h, 5, 1.1), SAGE))
C = 2 / 0.8980115458627326
def main_panel():
    src = Image.open('hr_main.png').convert('RGB')
    pad = 60; extra = 520
    im = sage(src.width + 2 * pad, src.height + pad + extra); im.paste(src, (pad, pad))
    P = lambda x, y: (int(x * C) + pad, int(y * C) + pad)
    # driveway from garage door
    dx0, dy0 = P(830, 1184); dx1, _ = P(1366, 0)
    dw = Image.fromarray(tint(noise(dx1 - dx0, im.height - dy0, 4, 1.2), (214, 215, 214))); dd = ImageDraw.Draw(dw)
    for yy in range(160, dw.height, 160): dd.line([0, yy, dw.width, yy], fill=(196, 197, 196), width=2)
    dd.line([dw.width // 2, 0, dw.width // 2, dw.height], fill=(196, 197, 196), width=2)
    im.paste(dw, (dx0, dy0))
    # front steps + curved walk to the driveway
    door = P(600, 0)[0]; sy0 = P(0, 1006)[1]; sy1 = sy0 + 70; sx0, sx1 = door - 70, door + 70
    Kk = 3; WR = 38; mk = Image.new('L', (im.width * Kk, im.height * Kk), 0); md = ImageDraw.Draw(mk)
    P0 = (dx0 + 10, sy1 + 300); P1 = (door, sy1 + 300); P2 = (door, sy1 + 100); P3 = (door, sy1 - 2)
    for i in range(301):
        t = i / 300
        x = (1 - t) ** 3 * P0[0] + 3 * (1 - t) ** 2 * t * P1[0] + 3 * (1 - t) * t ** 2 * P2[0] + t ** 3 * P3[0]
        y = (1 - t) ** 3 * P0[1] + 3 * (1 - t) ** 2 * t * P1[1] + 3 * (1 - t) * t ** 2 * P2[1] + t ** 3 * P3[1]
        md.ellipse([(x - WR) * Kk, (y - WR) * Kk, (x + WR) * Kk, (y + WR) * Kk], fill=255)
    mk = mk.resize(im.size, Image.LANCZOS); im.paste(Image.new('RGB', im.size, (214, 215, 214)), (0, 0), mk)
    dr = ImageDraw.Draw(im); dr.rectangle([sx0, sy0, sx1, sy1], fill=(206, 182, 146), outline=(40, 40, 40), width=3)
    for yy in range(sy0 + 18, sy1, 18): dr.line([sx0, yy, sx1, yy], fill=(120, 100, 80), width=2)
    return im
def up_panel():
    src = Image.open('hr_up.png').convert('RGB'); G = 2.2 / 0.6172839506172839
    b = [int(v * G) for v in (20, 0, 905, 1075)]; src = src.crop(b)
    s = 0.76; src = src.resize((int(src.width * s), int(src.height * s)), Image.LANCZOS)  # match main-floor scale
    im = sage(src.width + 100, src.height + 100); im.paste(src, (50, 50)); return im
def swatch(k):
    if k == 'lvp':
        img = Image.new('RGB', (90, 90), (216, 196, 164)); ImageDraw.Draw(img).line([0, 58, 90, 58], fill=(208, 187, 154)); return img
    if k == 'carpet': return Image.fromarray(tint(noise(90, 90, 5, 0.6), (240, 233, 220)))
    if k == 'tile':
        img = Image.new('RGB', (90, 90), (222, 226, 229)); d = ImageDraw.Draw(img)
        for kk in range(-90, 180, 36): d.line([kk, 0, kk + 90, 90], fill=(196, 202, 207), width=2); d.line([kk, 0, kk - 90, 90], fill=(196, 202, 207), width=2)
        return img
    return Image.fromarray(tint(noise(90, 90, 7, 1.4), (178, 181, 185)))
def photo(): return Image.open('hr-front.jpg').convert('RGB')
def framed(canvas, ph, px0, py0):
    dr = ImageDraw.Draw(canvas)
    sh = Image.new('RGBA', (ph.width + 40, ph.height + 40), (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle([20, 20, ph.width + 20, ph.height + 20], fill=(0, 0, 0, 90)); sh = sh.filter(ImageFilter.GaussianBlur(12))
    canvas.paste(sh, (px0 - 12, py0 - 6), sh); dr.rectangle([px0 - 12, py0 - 12, px0 + ph.width + 12, py0 + ph.height + 62], fill=(255, 255, 255)); canvas.paste(ph, (px0, py0))
    cap = f"{NAME}, built by Riverstone Homes"; f = ImageFont.truetype(F, 28)
    dr.text((px0 + (ph.width - dr.textlength(cap, font=f)) / 2, py0 + ph.height + 14), cap, font=f, fill=(27, 40, 35))
def finish(img, sub, legend, out):
    W = img.width
    bar = Image.new('RGB', (W, 190), (27, 40, 35)); bd = ImageDraw.Draw(bar)
    bd.text((60, 40), NAME, font=ImageFont.truetype(F, 64), fill=(242, 240, 234))
    fsub = ImageFont.truetype(FB, 26); bd.text((64, 118), sub, font=fsub, fill=(197, 164, 111))
    f30 = ImageFont.truetype(FS, 30); lx = max(int(64 + bd.textlength(NAME, font=ImageFont.truetype(F, 64)) + 120), int(64 + bd.textlength(sub, font=fsub) + 120))
    for k, name in legend:
        bar.paste(swatch(k), (lx, 50)); bd.rectangle([lx, 50, lx + 90, 140], outline=(197, 164, 111), width=2)
        bd.text((lx + 105, 78), name, font=f30, fill=(242, 240, 234)); lx += int(105 + bd.textlength(name, font=f30) + 70)
    foot = Image.new('RGB', (W, 60), (27, 40, 35)); fd = ImageDraw.Draw(foot)
    fd.text((60, 16), "Artist's rendering. Standard finishes shown; options and layouts can be customized. Call the builder for dimensions.  goriverstone.com  ·  706-514-6637", font=ImageFont.truetype(FS, 24), fill=(242, 240, 234))
    fin = Image.new('RGB', (W, img.height + 250)); fin.paste(bar, (0, 0)); fin.paste(img, (0, 190)); fin.paste(foot, (0, 190 + img.height))
    fin.save(out, quality=90); print(out, fin.size)
def single(p, sub, legend, out):
    ph = photo(); ph.thumbnail((860, 645))
    W = max(p.width + ph.width + 360, 2200); H = max(p.height, ph.height + 200)
    c = sage(W, H); c.paste(p, ((W - ph.width - 160 - p.width) // 2, (H - p.height) // 2)); framed(c, ph, W - ph.width - 80, 120); finish(c, sub, legend, out)
M = main_panel(); U = up_panel()
single(M, "3 BEDROOM + BONUS  ·  MAIN FLOOR  ·  RIVERSTONE HOMES", [('lvp', 'LVP'), ('carpet', 'Carpet'), ('tile', 'Tile'), ('garage', 'Garage')], 'hr-main.jpg')
single(U, "3 BEDROOM + BONUS  ·  UPSTAIRS  ·  RIVERSTONE HOMES", [('carpet', 'Carpet'), ('tile', 'Tile')], 'hr-up.jpg')
# combined: main + upstairs side by side, photo under upstairs
ph = photo(); ph.thumbnail((1000, 750))
HEAD = 90; fh = ImageFont.truetype(FB, 46)
W = M.width + max(U.width, ph.width + 40) + 120; H = HEAD + max(M.height, U.height + ph.height + 200) + 40
c = sage(W, H); dr = ImageDraw.Draw(c)
def head(t, x, w, y): dr.text((x + (w - dr.textlength(t, font=fh)) / 2, y), t, font=fh, fill=(27, 40, 35))
c.paste(M, (40, HEAD)); head("MAIN FLOOR", 40, M.width, 20)
ux = M.width + 80; c.paste(U, (ux, HEAD)); head("UPSTAIRS", ux, U.width, 20)
framed(c, ph, ux + (U.width - ph.width) // 2, HEAD + U.height + 60)
c = c.resize((int(W * 0.7), int(H * 0.7)), Image.LANCZOS)
finish(c, "3 BEDROOM + BONUS  ·  MAIN FLOOR + UPSTAIRS", [('lvp', 'LVP'), ('carpet', 'Carpet'), ('tile', 'Tile'), ('garage', 'Concrete')], 'hr-combined.jpg')
