import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage
rng = np.random.default_rng(6)
def noise(w, h, amt, blur=0.6):
    n = rng.normal(0, amt, (h, w)); im = Image.fromarray(np.clip(n + 128, 0, 255).astype('uint8'))
    return np.array(im.filter(ImageFilter.GaussianBlur(blur))).astype(int) - 128
def tint(arr, rgb): return np.clip(np.stack([arr + c for c in rgb], -1), 0, 255).astype('uint8')
SAGE = (184, 200, 168)
G = 2.2 / 0.6172839506172839          # grid px -> 330dpi px
g = np.array(Image.open('up330-1.png').convert('L')); H, W = g.shape
S = lambda b: [int(v * G) for v in b]
dark = g < 160
wall = ndimage.binary_opening(ndimage.binary_closing(dark, structure=np.ones((11, 11))), structure=np.ones((19, 19)))
lab, n = ndimage.label(wall); sizes = ndimage.sum(wall, lab, range(1, n + 1))
wall &= np.isin(lab, np.nonzero(sizes >= 3000)[0] + 1)
for bx in [(80, 80, 320, 165), (500, 95, 710, 140), (140, 550, 310, 600), (660, 770, 800, 815), (410, 625, 480, 652), (760, 765, 800, 800), (500, 1040, 574, 1070), (853, 1040, 910, 1070)]:   # heading underlines
    x0, y0, x1, y1 = S(bx); wall[y0:y1, x0:x1] = False
dr0 = Image.fromarray(wall); d0 = ImageDraw.Draw(dr0)
for bx in [(35, 47, 460, 54), (35, 47, 42, 130)]:   # family room top + left wall top piece
    d0.rectangle(S(bx), fill=True)
wall = np.array(dr0)

def tile(w, h):
    s = 40; img = Image.new('RGB', (w, h), (222, 226, 229)); dd = ImageDraw.Draw(img)
    for k in range(-h, w + h, s):
        dd.line([k, 0, k + h, h], fill=(196, 202, 207), width=2); dd.line([k, 0, k - h, h], fill=(196, 202, 207), width=2)
    x = np.array(img).astype(int) + noise(w, h, 3, 0.6)[..., None]; return np.clip(x, 0, 255).astype('uint8')
TEX = {'carpet': tint(noise(W, H, 5, 0.6), (240, 233, 220)), 'tile': tile(W, H), 'open': tint(noise(W, H, 3, 1.0), (226, 230, 220))}
ROOMS = [('open', (35, 47, 462, 497)), ('carpet', (235, 405, 462, 497)), ('carpet', (460, 40, 745, 372)), ('carpet', (460, 300, 545, 500)),
         ('tile', (540, 370, 780, 494)), ('carpet', (110, 495, 387, 826)), ('carpet', (385, 495, 577, 690)),
         ('carpet', (575, 495, 852, 1057)), ('carpet', (540, 490, 580, 585))]
res = tint(noise(W, H, 5, 1.1), SAGE)
for k, bx in ROOMS:
    x0, y0, x1, y1 = S(bx); res[y0:y1, x0:x1] = TEX[k][y0:y1, x0:x1]
res[wall] = (30, 30, 30)
img = Image.fromarray(res); dr = ImageDraw.Draw(img)
for bx in [(165, 820, 333, 829), (686, 1050, 744, 1059)]:
    dr.rectangle(S(bx), fill=(120, 168, 180))
L = (70, 70, 70); lw = 4
def R(b): return S(b)
# stairs: run down from landing toward the left
x0, y0, x1, y1 = R((238, 412, 458, 492)); dr.rectangle([x0, y0, x1, y1], outline=L, width=lw)
for x in np.arange(x0, x1, (x1 - x0) / 11): dr.line([x, y0, x, y1], fill=L, width=3)
dr.line([x0, (y0 + y1) / 2, x1 - 40, (y0 + y1) / 2], fill=L, width=3)
ax = x0 + 30; ay = (y0 + y1) / 2; dr.line([ax, ay, ax + 40, ay - 25], fill=L, width=3); dr.line([ax, ay, ax + 40, ay + 25], fill=L, width=3)
# bath: vanity + sink, toilet, tub
vx0, vy0, vx1, vy1 = R((547, 374, 639, 420)); dr.rectangle([vx0, vy0, vx1, vy1], fill=(245, 245, 243), outline=L, width=lw)
cx, cy = (vx0 + vx1) / 2, (vy0 + vy1) / 2; dr.ellipse([cx - 70, cy - 42, cx + 70, cy + 42], outline=L, width=lw)
tx0, ty0, tx1, ty1 = R((659, 376, 697, 431))
dr.rectangle([tx0 + 10, ty0, tx1 - 10, ty0 + 40], fill=(245, 245, 243), outline=L, width=lw)
dr.ellipse([tx0 + 8, ty0 + 40, tx1 - 8, ty1], fill=(245, 245, 243), outline=L, width=lw)
bx0, by0, bx1, by1 = R((718, 374, 777, 490)); dr.rectangle([bx0, by0, bx1, by1], fill=(245, 245, 243), outline=L, width=lw)
dr.rounded_rectangle([bx0 + 22, by0 + 22, bx1 - 22, by1 - 22], radius=50, outline=L, width=lw)
# open-to-below rail along landing
dr.line(R((238, 405, 462, 405)), fill=L, width=6)
def font(sz):
    f = ImageFont.truetype('/usr/share/fonts/truetype/google-fonts/ofl/opensans/OpenSans[wdth,wght].ttf', sz); f.set_variation_by_name('SemiBold'); return f
LABELS = [('Open to Great Room Below', 248, 250, 52), ('Bedroom 3', 602, 190, 58), ('Bath', 600, 465, 44), ('Bedroom 2', 248, 660, 58),
          ('WIC', 437, 640, 40), ('WIC', 532, 640, 40), ('Optional Bonus Room', 712, 800, 54)]
for t, x, y, sz in LABELS:
    f = font(sz); X, Y = x * G, y * G; bb = dr.textbbox((0, 0), t, font=f)
    dr.text((X - (bb[2] - bb[0]) / 2 - bb[0], Y - (bb[3] - bb[1]) / 2 - bb[1]), t, font=f, fill=(55, 55, 55))
img.save('hr_up.png'); print(img.size)
