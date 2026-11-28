import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage
rng = np.random.default_rng(5)
def noise(w, h, amt, blur=0.6):
    n = rng.normal(0, amt, (h, w)); im = Image.fromarray(np.clip(n + 128, 0, 255).astype('uint8'))
    return np.array(im.filter(ImageFilter.GaussianBlur(blur))).astype(int) - 128
def tint(arr, rgb): return np.clip(np.stack([arr + c for c in rgb], -1), 0, 255).astype('uint8')
SAGE = (184, 200, 168)
K = 2.0  # upscale source 1559px -> 3118px
src = Image.open('hr_main_src.png').convert('RGB')
src = src.resize((int(src.width * K), int(src.height * K)), Image.LANCZOS)
a = np.array(src).astype(int); H, W = a.shape[:2]
C = K / 0.8980115458627326
S = lambda b: [int(v * C) for v in b]
mx = a.max(2); mn = a.min(2)
dark = mx < 120
wall = ndimage.binary_opening(dark, structure=np.ones((int(7*K), int(7*K))))
wall = ndimage.binary_dilation(wall, iterations=1) & dark

def lvp(w, h):
    img = Image.new('RGB', (w, h), (216, 196, 164)); dd = ImageDraw.Draw(img)
    for y in range(0, h, 56): dd.line([0, y, w, y], fill=(208, 187, 154), width=1)
    x = np.array(img).astype(int) + noise(w, h, 3, 1.5)[..., None]; return np.clip(x, 0, 255).astype('uint8')
def tile(w, h):
    s = 40; img = Image.new('RGB', (w, h), (222, 226, 229)); dd = ImageDraw.Draw(img)
    for k in range(-h, w + h, s):
        dd.line([k, 0, k + h, h], fill=(196, 202, 207), width=2); dd.line([k, 0, k - h, h], fill=(196, 202, 207), width=2)
    x = np.array(img).astype(int) + noise(w, h, 3, 0.6)[..., None]; return np.clip(x, 0, 255).astype('uint8')
def boards(w, h):
    img = Image.new('RGB', (w, h), (196, 170, 132)); dd = ImageDraw.Draw(img)
    for x in range(0, w, 16): dd.line([x, 0, x, h], fill=(176, 150, 112), width=2)
    x = np.array(img).astype(int) + noise(w, h, 5, 0.8)[..., None]; return np.clip(x, 0, 255).astype('uint8')
TEX = {'lvp': lvp(W, H), 'carpet': tint(noise(W, H, 5, 0.6), (240, 233, 220)), 'tile': tile(W, H),
       'garage': tint(noise(W, H, 7, 1.4), (178, 181, 185)), 'porch': boards(W, H)}
ROOMS = [
    ('carpet', (30, 90, 368, 482)), ('carpet', (93, 880, 370, 1082)),
    ('tile', (30, 485, 225, 880)), ('tile', (225, 485, 288, 672)), ('tile', (225, 750, 370, 885)),
    ('lvp', (285, 480, 370, 752)), ('lvp', (225, 670, 290, 752)),
    ('lvp', (370, 90, 1132, 640)), ('lvp', (370, 575, 858, 882)),
    ('lvp', (1132, 342, 1368, 488)), ('lvp', (1132, 485, 1368, 637)),
    ('porch', (1132, 90, 1368, 342)), ('porch', (1145, 18, 1370, 88)), ('porch', (370, 882, 830, 1008)),
    ('garage', (858, 635, 1368, 820)), ('garage', (828, 815, 1368, 1184)),
]
PROTECT = [(40, 495, 115, 625), (230, 495, 285, 665), (30, 625, 160, 735), (55, 815, 100, 875), (245, 825, 290, 880), (310, 840, 362, 880),
           (878, 312, 962, 500), (1072, 312, 1132, 502), (825, 565, 1135, 635), (465, 478, 745, 580),
           (1140, 345, 1362, 408), (1228, 560, 1264, 630), (515, 20, 680, 128)]
ERASE = [(745, 490, 785, 565), (290, 438, 358, 484), (122, 662, 165, 722), (88, 830, 133, 905), (140, 820, 205, 872), (280, 683, 322, 800),
         (296, 742, 362, 798), (400, 820, 488, 880), (1155, 436, 1226, 484), (1148, 582, 1222, 637), (1262, 492, 1312, 556),
         (1132, 125, 1192, 280), (300, 440, 356, 487), (560, 55, 634, 82), (842, 816, 868, 884)]
res = tint(noise(W, H, 5, 1.1), SAGE)
house = np.zeros((H, W), bool); living = np.zeros((H, W), bool); P = np.zeros((H, W), bool); E = np.zeros((H, W), bool)
for k, bx in ROOMS:
    x0, y0, x1, y1 = S(bx); house[y0:y1, x0:x1] = True; res[y0:y1, x0:x1] = TEX[k][y0:y1, x0:x1]
    if k not in ('porch', 'garage'): living[y0:y1, x0:x1] = True
for bx in PROTECT:
    x0, y0, x1, y1 = S(bx); P[y0:y1, x0:x1] = True
for bx in ERASE:
    x0, y0, x1, y1 = S(bx); E[y0:y1, x0:x1] = True
# white fixtures/counters inside protect stay white
whiteish = mn > 236
res[P & whiteish & house] = a[P & whiteish & house].astype('uint8')
inside = ndimage.binary_dilation(house, iterations=int(10*K))
neutral = (mx - mn) < 30
lines = ((mn < 125) | ((mn < 200) & neutral)) & P & ~E
outer = ndimage.binary_dilation(living, iterations=int(6*K)) & ~ndimage.binary_erosion(living, iterations=int(6*K)) & ~ndimage.binary_dilation(house & ~living, iterations=int(2*K))
win = (mn < 225) & neutral & outer & ~wall & ~E
keep = (wall & inside) | lines
alpha = np.clip((235 - mn) / 160, 0, 1) * ndimage.binary_dilation(keep, iterations=1)
col = np.where(wall[..., None], np.array([30, 30, 30]), np.array([70, 70, 70]))
res = (res * (1 - alpha[..., None]) + col * alpha[..., None]).astype('uint8')
wm = ndimage.binary_dilation(win, iterations=1) & ~wall
res[wm] = (120, 168, 180)
img = Image.fromarray(res); dr = ImageDraw.Draw(img)
def font(sz):
    f = ImageFont.truetype('/usr/share/fonts/truetype/google-fonts/ofl/opensans/OpenSans[wdth,wght].ttf', sz); f.set_variation_by_name('SemiBold'); return f
LABELS = [('Primary Suite', 200, 285, 30), ('Primary Bath', 150, 560, 24), ('Primary Closet', 230, 975, 24), ('Great Room', 570, 265, 30),
          ('Breakfast', 935, 205, 28), ('Kitchen', 1010, 540, 26), ('Foyer', 437, 728, 26), ('Dining / Flex', 660, 718, 28), ('Laundry', 1250, 450, 22),
          ('Pantry', 1310, 600, 20), ('Covered Porch', 1250, 215, 24), ('Grilling Deck', 1258, 55, 20), ('Front Porch', 600, 940, 26),
          ('2 Car Garage', 1100, 835, 30), ('Powder', 300, 800, 18)]
for t, x, y, sz in LABELS:
    f = font(int(sz * K / 1.6)); X, Y = x * C, y * C; bb = dr.textbbox((0, 0), t, font=f)
    dr.text((X - (bb[2] - bb[0]) / 2 - bb[0], Y - (bb[3] - bb[1]) / 2 - bb[1]), t, font=f, fill=(55, 55, 55))
img.save('hr_main.png'); print(img.size)
