"""Stoneleigh Cottage color plan renderer (works on the embedded 300ppi rasters). Usage: python3 render_sc.py main|up"""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage
rng = np.random.default_rng(4)
def noise(w, h, amt, blur=0.6):
    n = rng.normal(0, amt, (h, w)); im = Image.fromarray(np.clip(n + 128, 0, 255).astype('uint8'))
    return np.array(im.filter(ImageFilter.GaussianBlur(blur))).astype(int) - 128
def tint(arr, rgb): return np.clip(np.stack([arr + c for c in rgb], -1), 0, 255).astype('uint8')
SAGE = (184, 200, 168); K = 2.5
which = sys.argv[1]
if which == 'main':
    SRC = 'img-000.png'; OUT = 'sc_main.png'
    ERASE = [(150, 172, 232, 212), (95, 237, 142, 255), (125, 282, 232, 312), (64, 288, 96, 304), (62, 348, 104, 366), (192, 355, 260, 380),
             (128, 402, 162, 420), (100, 462, 155, 478), (126, 516, 210, 545), (108, 570, 142, 585), (98, 688, 236, 752), (362, 370, 508, 470),
             (302, 694, 366, 722), (424, 730, 476, 755), (385, 575, 445, 612), (532, 575, 580, 612), (605, 606, 655, 622), (536, 648, 594, 666),
             (608, 680, 648, 694), (595, 703, 655, 725), (575, 752, 590, 768), (618, 752, 640, 768), (668, 628, 696, 642), (676, 700, 742, 716),
             (806, 696, 840, 712), (730, 588, 805, 642), (740, 742, 800, 768), (655, 280, 835, 296), (668, 345, 805, 408), (314, 820, 446, 838),
             (62, 897, 275, 924), (636, 1005, 745, 1062), (545, 1258, 868, 1274), (195, 120, 252, 148), (418, 250, 450, 262),
             (300, 750, 348, 800), (498, 755, 550, 800), (205, 220, 238, 262), (555, 695, 600, 742)]
    ROOMS = [('porch', (52, 38, 397, 222)), ('lvp', (56, 222, 270, 610)), ('lvp', (56, 608, 270, 832)), ('lvp', (268, 255, 600, 562)),
             ('lvp', (268, 558, 600, 627)), ('lvp', (268, 622, 392, 797)), ('lvp', (390, 622, 557, 690)), ('lvp', (490, 686, 557, 797)),
             ('tile', (390, 686, 492, 797)), ('lvp', (553, 668, 657, 797)), ('lvp', (525, 598, 657, 672)),
             ('carpet', (598, 222, 777, 502)), ('carpet', (775, 262, 884, 502)), ('lvp', (380, 215, 485, 262)), ('lvp', (595, 498, 662, 600)), ('tile', (655, 498, 884, 692)), ('carpet', (663, 688, 884, 797)),
             ('porch', (268, 795, 492, 872)), ('garage', (490, 795, 884, 1302)), ('garage', (668, 1298, 884, 1337))]
    PROTECT = [(60, 228, 100, 600), (165, 385, 236, 500), (168, 565, 248, 608), (370, 558, 598, 628), (395, 690, 445, 785),
               (660, 505, 712, 548), (660, 568, 700, 610), (840, 505, 880, 690), (668, 655, 745, 718), (560, 742, 655, 768),
               (610, 660, 648, 680), (375, 218, 482, 285)]
    LABELS = [('Covered Deck', 225, 130, 22), ('Breakfast', 180, 295, 20), ('Kitchen', 140, 530, 20), ('Dining Room', 165, 715, 22),
              ('Family Room', 435, 410, 24), ('Foyer', 333, 707, 18), ('Powder', 455, 742, 13), ('Laundry', 605, 715, 13),
              ('Primary Suite', 740, 375, 22), ('Primary Bath', 767, 620, 16), ('Primary Closet', 770, 755, 16), ('Front Porch', 380, 832, 16),
              ('2 Car Garage', 690, 1030, 24)]
    POSTS = []
else:
    SRC = 'img-001.png'; OUT = 'sc_up.png'
    ERASE, ROOMS, PROTECT, LABELS, POSTS = [], [], [], [], []
    exec(open('sc_up_cfg.py').read())
im = Image.open(SRC).convert('L'); im = im.resize((int(im.width * K), int(im.height * K)), Image.LANCZOS)
S = lambda b: [int(v * K) for v in b]
d = ImageDraw.Draw(im)
for b in ERASE: d.rectangle(S(b), fill=255)
g = np.array(im).astype(int); H, W = g.shape
lines = g < 160
thick = ndimage.binary_dilation(ndimage.binary_opening(lines, structure=np.ones((8, 8))), iterations=1)
P = np.zeros((H, W), bool)
for b in PROTECT:
    x0, y0, x1, y1 = S(b); P[y0:y1, x0:x1] = True
hm = np.zeros((H, W), bool)
for _k, b in ROOMS:
    x0, y0, x1, y1 = S(b); hm[y0:y1, x0:x1] = True
band = ndimage.binary_dilation(hm, iterations=14) & ~ndimage.binary_erosion(hm, iterations=14)
_l, _n = ndimage.label(thick); _sz = ndimage.sum(thick, _l, range(1, _n + 1)); thick &= ~(np.isin(_l, np.nonzero(_sz < 400)[0] + 1) & ~P)
keep = thick | (lines & (P | band))
_l2, _n2 = ndimage.label(keep, structure=np.ones((3, 3))); _s2 = ndimage.sum(keep, _l2, range(1, _n2 + 1)); keep &= ~(np.isin(_l2, np.nonzero(_s2 < 150)[0] + 1) & ~P)
alpha = np.clip((215 - g) / 130, 0, 1) * ndimage.binary_dilation(keep, iterations=1)
def lvp(w, h):
    img = Image.new('RGB', (w, h), (216, 196, 164)); dd = ImageDraw.Draw(img)
    for y in range(0, h, 44): dd.line([0, y, w, y], fill=(208, 187, 154), width=1)
    x = np.array(img).astype(int) + noise(w, h, 3, 1.5)[..., None]; return np.clip(x, 0, 255).astype('uint8')
def tile(w, h):
    s = 30; img = Image.new('RGB', (w, h), (222, 226, 229)); dd = ImageDraw.Draw(img)
    for k in range(-h, w + h, s):
        dd.line([k, 0, k + h, h], fill=(196, 202, 207), width=1); dd.line([k, 0, k - h, h], fill=(196, 202, 207), width=1)
    x = np.array(img).astype(int) + noise(w, h, 3, 0.6)[..., None]; return np.clip(x, 0, 255).astype('uint8')
def boards(w, h):
    img = Image.new('RGB', (w, h), (196, 170, 132)); dd = ImageDraw.Draw(img)
    for x in range(0, w, 13): dd.line([x, 0, x, h], fill=(176, 150, 112), width=2)
    x = np.array(img).astype(int) + noise(w, h, 5, 0.8)[..., None]; return np.clip(x, 0, 255).astype('uint8')
TEX = {'lvp': lvp(W, H), 'carpet': tint(noise(W, H, 5, 0.6), (240, 233, 220)), 'tile': tile(W, H), 'garage': tint(noise(W, H, 7, 1.4), (178, 181, 185)),
       'porch': boards(W, H), 'open': tint(noise(W, H, 3, 1.0), (226, 230, 220))}
res = tint(noise(W, H, 5, 1.1), SAGE)
for k, b in ROOMS:
    x0, y0, x1, y1 = S(b); res[y0:y1, x0:x1] = TEX[k][y0:y1, x0:x1]
white = (g > 235) & P & hm & ~keep
col = np.array([35, 35, 35])
res = (res * (1 - alpha[..., None]) + col * alpha[..., None]).astype('uint8')
img = Image.fromarray(res); dr = ImageDraw.Draw(img)
def font(sz):
    f = ImageFont.truetype('/usr/share/fonts/truetype/google-fonts/ofl/opensans/OpenSans[wdth,wght].ttf', sz); f.set_variation_by_name('SemiBold'); return f
for t, x, y, sz in LABELS:
    f = font(int(sz * K * 0.9)); X, Y = x * K, y * K; bb = dr.textbbox((0, 0), t, font=f)
    dr.text((X - (bb[2] - bb[0]) / 2 - bb[0], Y - (bb[3] - bb[1]) / 2 - bb[1]), t, font=f, fill=(55, 55, 55))
if which == 'main':
    L = (60, 60, 60); x0, y0, x1, y1 = S((372, 562, 598, 625)); dr.rectangle([x0, y0, x1, y1], outline=L, width=4)
    for x in np.arange(x0, x1, (x1 - x0) / 16): dr.line([x, y0, x, y1], fill=L, width=3)
    dr.line([x0, (y0 + y1) / 2, x1, (y0 + y1) / 2], fill=L, width=4)
    POSTS = [(57, 42), (392, 42)]
if 'POST' in globals(): POST(dr, S)
for x, y in POSTS:
    X, Y = x * K, y * K; dr.rectangle([X - 9, Y - 9, X + 9, Y + 9], fill=(30, 30, 30))
img.save(OUT); print(OUT, img.size)
