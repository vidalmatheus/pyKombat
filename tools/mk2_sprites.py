"""Recorta as folhas de sprites do Mortal Kombat II (SNES) em tiras no formato do jogo.

As folhas vêm de https://www.spriters-resource.com/snes/mortalkombat2/ (rip de
ant19831983) e ficam em res/Char/<base>/sheet.png. Cada folha é um mosaico de
sprites soltos sobre um fundo liso; aqui:

  1. cada sprite é achado sozinho (componentes conexos sobre o fundo) — a ordem
     é estável: por linha da folha, da esquerda para a direita, então os
     índices abaixo (FRAMES_MK2) apontam sempre para o mesmo desenho;
  2. as tiras são montadas com os índices escolhidos para cada animação,
     ampliadas (os sprites do SNES são menores que os do MK1 arcade) e
     alinhadas pelos pés na última linha e pelo quadril no centro do frame;
  3. cada tira é gravada como PNG paletizado (índice 0 transparente), igual às
     de tools/build_sprites.py — assim a troca de paleta funciona igual.

Não usa Pillow (só zlib, via tools/pngio.py): as folhas do SNES têm poucas
cores, então não é preciso quantizar.

Uso: python3 tools/mk2_sprites.py   (ou via tools/build_sprites.py)
"""
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pngio  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'res', 'Char')
DST = os.path.join(ROOT, 'res', 'sprites')

CELL_W = 200
CELL_H = 164
SCALE = 1.36   # Liu Kang parado: ~99 px no SNES -> ~135 px (altura do Sub-Zero)

# Tiras: nome -> lista de frames. Cada frame é o índice de um sprite da folha
# (ou uma tupla (índice, dx) para corrigir o alinhamento na mão, em pixels já
# ampliados). As tiras usam os mesmos nomes e a mesma quantidade de frames das
# do Sub-Zero/Scorpion, para as animações comuns (fighter.COMMON_ANIMS) valerem
# para todos; o que falta no MK2 repete um frame vizinho.
# Opções por tira (dict em ALIGN): 'center' = alinha pelo centro da caixa
# (cambalhotas, quedas), 'left' = pela borda de trás.
FRAMES_MK2 = {
    'LiuKang': {
        'dance': [1, 2, 3, 4, 5, 6],
        'walk': list(range(17, 26)),
        'jump': [11, 28, 27],                      # agachado, esticado, encolhido
        'spin': [28] + list(range(29, 36)),
        'crouch': [11, 12, 12],
        'Apunch': [1, 42, 43],
        # soco forte: 3-5 e 6-8 (um braço de cada vez, alternando)
        'Bpunch': [44, 44, 44, 51, 52, 53, 44, 45, 46, 45, 44],
        'Cpunch': [89, 89, 90],
        'Dpunch': [85, 86, 87, 88, 88],
        'Akick': [69, 69, 70, 70, 71, 71, 72],
        'Bkick': [65, 65, 66, 66, 67, 68, 68, 67, 66],
        'Ckick': [12, 12, 99, 99, 100, 100, 100],
        'Dkick': [80, 81, 82, 83, 84, 80],
        'Ekick': [28, 98, 98],
        'Epunch': [28, 26, 26],
        'Ahit': [101, 101, 102],
        'Bhit': [107, 109, 110],
        'Chit': [101, 105, 106, 106, 105, 101],
        'Ehit': [111, 112, 112],
        # queda (0-6, o último deitado) + levantar com rolamento para trás (7-13)
        'Fhit': [121, 122, 123, 124, 125, 126, 126, 57, 58, 59, 60, 61, 62, 64],
        'Ghit': [54, 55, 56, 57, 57, 57, 58, 59, 61, 62, 64],
        'Ablock': [7, 8, 8],
        'Bblock': [13, 14, 14],
        'dizzy': list(range(136, 142)),
        'win': [36, 37, 38, 39],
        'Special': [1, 142, 144, 144, 142, 1],      # bola de fogo
        'Fkick': [96, 97],                         # voadora (flying kick)
        'fatality': list(range(189, 201)),         # vira dragão e morde
        'fatalityhit': [218, 219, 220, 221, 222, 223, 223, 223, 223, 223],
    },
    'Kitana': {
        'dance': [1, 2, 3, 4, 5],
        'walk': list(range(16, 24)),
        'jump': [10, 24, 25],
        'spin': [24] + list(range(27, 34)),
        'crouch': [10, 11, 11],
        'Apunch': [1, 49, 50],
        'Bpunch': [56, 56, 56, 53, 54, 55, 56, 57, 58, 57, 56],
        'Cpunch': [92, 92, 93],
        'Dpunch': [87, 88, 89, 90, 90],
        'Akick': [69, 69, 70, 71, 72, 72, 73],
        'Bkick': [64, 64, 65, 66, 67, 68, 68, 67, 65],
        'Ckick': [10, 10, 99, 99, 100, 100, 100],
        'Dkick': [82, 83, 86, 84, 85, 82],
        'Ekick': [25, 102, 102],
        'Epunch': [25, 26, 26],
        'Ahit': [105, 106, 106],
        'Bhit': [110, 112, 113],
        'Chit': [105, 107, 108, 108, 107, 105],
        'Ehit': [115, 116, 116],
        'Fhit': [125, 126, 127, 128, 129, 129, 129, 136, 136, 137, 137, 138, 138, 139],
        'Ghit': [130, 131, 132, 133, 134, 135, 136, 137, 138, 138, 139],
        'Ablock': [6, 7, 7],
        'Bblock': [12, 13, 13],
        'dizzy': list(range(141, 146)),
        'win': [34, 36, 37, 38],
        'Special': [1, 168, 168, 146, 147, 1],     # arremesso do leque
        'Special2': [1, 40, 41, 41, 40, 1],        # leque que levanta (fan lift)
        'fatality': [1, 168, 169, 170, 171, 172, 173, 173],  # leque corta a cabeça
        'fatalityhit': [202, 203, 204, 205, 206, 207, 208, 209, 210, 210],
    },
    'Raiden': {
        'dance': list(range(1, 9)),
        'walk': list(range(19, 27)),
        'jump': [13, 27, 28],
        'spin': [27] + list(range(30, 37)),
        'crouch': [13, 14, 14],
        'Apunch': [1, 61, 62],
        'Bpunch': [63, 63, 63, 70, 71, 72, 63, 64, 65, 64, 63],
        'Cpunch': [114, 114, 115],
        'Dpunch': [108, 109, 110, 111, 111],
        'Akick': [87, 87, 88, 89, 90, 90, 91],
        'Bkick': [82, 82, 83, 84, 85, 86, 86, 85, 83],
        'Ckick': [13, 13, 118, 118, 119, 119, 119],
        'Dkick': [102, 103, 104, 105, 106, 102],
        'Ekick': [28, 123, 123],
        'Epunch': [28, 29, 29],
        'Ahit': [126, 127, 127],
        'Bhit': [130, 131, 131],
        'Chit': [126, 128, 129, 129, 128, 126],
        'Ehit': [138, 139, 139],
        'Fhit': [145, 146, 146, 147, 148, 149, 149, 149, 13, 13, 14, 173, 174, 1],
        'Ghit': [150, 151, 152, 153, 154, 155, 13, 14, 173, 174, 1],
        'Ablock': [9, 10, 10],
        'Bblock': [15, 16, 16],
        'dizzy': list(range(161, 168)),
        'win': [37, 38, 39, 40, 41],
        'Special': [1, 173, 174, 168, 169, 174],   # raio
        'Fkick': [170, 171],                       # torpedo
        'fatality': [1, 204, 205],                 # chama o raio do céu
        'fatalityhit': [226, 227, 228, 229, 230, 231, 232, 233, 234, 234],
    },
}
ALIGN = {
    'spin': 'center', 'Fhit': 'center', 'Ghit': 'center', 'fatalityhit': 'center',
    ('LiuKang', 'fatality'): 'left',   # o dragão cresce para a frente; a cauda fica no lugar
}
# efeitos (sem troca de paleta): nome -> (base, frames); âncora = frente do efeito
FX_MK2 = {
    'fireball': ('LiuKang', [146, 147, 150, 151, 152, 153, 154, 155]),   # 0-1 saindo, 2-3 voando, 4-7 explosão
    'fan': ('Kitana', list(range(148, 158))),                          # leque girando
    'fanwind': ('Kitana', [158, 159, 160, 161, 162, 163, 164, 165]),   # vento do fan lift
    'lightning': ('Raiden', [175, 177, 179, 181, 182, 183, 184, 186, 188, 193]),  # 0-2 forma, 3-6 voa, 7-9 estoura
    'raidenbolt': ('Raiden', [206, 207]),                              # raio do céu (fatality)
}


def find_sprites(w, h, px, bg, gap=2, minPixels=12):
    """Caixas [x0, y0, x1, y1] dos sprites, em ordem de leitura (linhas da folha)."""
    m = [[c is not None and c != bg for c in row] for row in px]
    seen = [[False] * w for _ in range(h)]
    found = []
    for y in range(h):
        for x in range(w):
            if m[y][x] and not seen[y][x]:
                stack = [(x, y)]
                seen[y][x] = True
                x0 = x1 = x
                y0 = y1 = y
                n = 0
                while stack:
                    cx, cy = stack.pop()
                    n += 1
                    x0, x1 = min(x0, cx), max(x1, cx)
                    y0, y1 = min(y0, cy), max(y1, cy)
                    for yy in range(max(0, cy - gap), min(h, cy + gap + 1)):
                        for xx in range(max(0, cx - gap), min(w, cx + gap + 1)):
                            if m[yy][xx] and not seen[yy][xx]:
                                seen[yy][xx] = True
                                stack.append((xx, yy))
                if n >= minPixels:
                    found.append([x0, y0, x1 + 1, y1 + 1])
    # agrupa em linhas pelo centro vertical
    found.sort(key=lambda b: (b[1] + b[3]) / 2)
    rows = []
    for b in found:
        cy = (b[1] + b[3]) / 2
        for r in rows:
            if r[0] - 4 <= cy <= r[1] + 4:
                r[2].append(b)
                r[0], r[1] = min(r[0], b[1]), max(r[1], b[3])
                break
        else:
            rows.append([b[1], b[3], [b]])
    rows.sort(key=lambda r: r[0])
    out = []
    for r in rows:
        out += sorted(r[2], key=lambda b: b[0])
    return out


class Sheet:
    def __init__(self, base):
        self.w, self.h, self.px = pngio.read(os.path.join(SRC, base, 'sheet.png'))
        self.bg = Counter(c for row in self.px[:40] for c in row).most_common(1)[0][0]
        self.boxes = find_sprites(self.w, self.h, self.px, self.bg)
        stand = self.boxes[FRAMES_MK2[base]['dance'][0]]
        self.standH = stand[3] - stand[1]

    def sprite(self, i):
        """(largura, altura, pixels) do sprite i, já ampliado."""
        x0, y0, x1, y1 = self.boxes[i]
        bw, bh = x1 - x0, y1 - y0
        sw, sh = int(round(bw * SCALE)), int(round(bh * SCALE))
        src = self.px
        bg = self.bg
        out = []
        for y in range(sh):
            row = src[y0 + min(bh - 1, int(y / SCALE))]
            line = []
            for x in range(sw):
                c = row[x0 + min(bw - 1, int(x / SCALE))]
                line.append(None if c == bg else c)
            out.append(line)
        return sw, sh, out

    def hip(self, sw, sh, spx):
        """x do quadril: mediana dos pixels na faixa da cintura (ou o centro da caixa)."""
        H = self.standH * SCALE
        ys = range(max(0, int(sh - 0.56 * H)), max(0, int(sh - 0.44 * H)))
        xs = sorted(x for y in ys for x in range(sw) if spx[y][x])
        return xs[len(xs) // 2] if len(xs) > 20 else sw // 2


def build_strip(sheet, frames, align):
    sprites = []
    for f in frames:
        i, dx = (f if isinstance(f, tuple) else (f, 0))
        sprites.append((sheet.sprite(i), dx))
    # ponto de referência de cada frame (fica no centro do frame da tira)
    refs = []
    for (sw, sh, spx), dx in sprites:
        if align == 'center':
            refs.append(sw // 2 - dx)
        elif align == 'left':
            refs.append(-dx)
        else:
            refs.append(sheet.hip(sw, sh, spx) - dx)
    if align == 'left':  # o primeiro frame (corpo parado) define onde fica a borda de trás
        (sw0, sh0, spx0), _ = sprites[0]
        shift = sheet.hip(sw0, sh0, spx0)
        refs = [r + shift for r in refs]
    cw = max(CELL_W, max(2 * max(r, sw - r) for ((sw, _, _), _), r in zip(sprites, refs)) + 4)
    ch = max(CELL_H, max(sh for ((_, sh, _), _) in sprites))
    cw += cw % 2
    n = len(frames)
    img = [[None] * (cw * n) for _ in range(ch)]
    for k, (((sw, sh, spx), _), r) in enumerate(zip(sprites, refs)):
        ox = k * cw + cw // 2 - r
        oy = ch - sh
        for y in range(sh):
            line = img[oy + y]
            for x, c in enumerate(spx[y]):
                if c is not None and 0 <= ox + x - k * cw < cw:
                    line[ox + x] = c
    return cw * n, ch, img


def build_fx(sheet, frames):
    """Efeito (bola de fogo...): frames alinhados pela frente (borda direita) e pelo centro vertical."""
    sprites = [sheet.sprite(i) for i in frames]
    cw = max(sw for sw, _, _ in sprites) + 4
    ch = max(sh for _, sh, _ in sprites) + 4
    img = [[None] * (cw * len(frames)) for _ in range(ch)]
    for k, (sw, sh, spx) in enumerate(sprites):
        ox = (k + 1) * cw - 2 - sw
        oy = (ch - sh) // 2
        for y in range(sh):
            for x, c in enumerate(spx[y]):
                if c is not None:
                    img[oy + y][ox + x] = c
    return cw * len(frames), ch, img


def build_toasty():
    """Toasty! do MK2: rosto do Dan Forden + o texto, sem fundo (res/sprites/toasty.png).
    Vem da folha de menus do MK2 (res/Char/MK2/menu.png)."""
    w, h, px = pngio.read(os.path.join(SRC, 'MK2', 'menu.png'))
    bg = Counter(c for row in px[:5] for c in row[600:]).most_common(1)[0][0]

    def cut(x0, y0, x1, y1, k):
        return [[None if px[y0 + y // k][x0 + x // k] == bg else px[y0 + y // k][x0 + x // k]
                 for x in range((x1 - x0) * k)] for y in range((y1 - y0) * k)]
    face = cut(1053, 628, 1095, 684, 2)     # 84 x 112
    text = cut(841, 770, 898, 784, 2)       # "TOASTY!!" (laranja), 114 x 28
    W = max(len(face[0]), len(text[0]))
    img = [[None] * W for _ in range(len(face) + 4 + len(text))]
    for y, row in enumerate(face):
        for x, c in enumerate(row):
            img[y][(W - len(face[0])) // 2 + x] = c
    for y, row in enumerate(text):
        for x, c in enumerate(row):
            img[len(face) + 4 + y][(W - len(text[0])) // 2 + x] = c
    save_indexed(os.path.join(DST, 'toasty.png'), W, len(img), img)
    print('ok toasty', W, 'x', len(img))


def save_indexed(path, w, h, img):
    colors = Counter(c for row in img for c in row if c is not None)
    pal = [c for c, _ in colors.most_common()]
    if len(pal) > 255:  # junta as cores raras na mais próxima
        keep = pal[:255]
        near = {}
        for c in pal[255:]:
            near[c] = min(keep, key=lambda k: sum((a - b) ** 2 for a, b in zip(k, c)))
        img = [[near.get(c, c) if c is not None else None for c in row] for row in img]
        pal = keep
    index = {c: i + 1 for i, c in enumerate(pal)}
    idx = [[index[c] if c is not None else 0 for c in row] for row in img]
    pngio.write_indexed(path, w, h, idx, [(255, 0, 255)] + pal)


def build(base):
    sheet = Sheet(base)
    os.makedirs(os.path.join(DST, base), exist_ok=True)
    counts = {}
    for name, frames in FRAMES_MK2[base].items():
        w, h, img = build_strip(sheet, frames, ALIGN.get((base, name), ALIGN.get(name, 'waist')))
        save_indexed(os.path.join(DST, base, name + '.png'), w, h, img)
        counts[name] = len(frames)
        print('ok', base, name, len(frames), 'frames de', w // len(frames), 'x', h)
    for name, (fxBase, frames) in FX_MK2.items():
        if fxBase == base:
            w, h, img = build_fx(sheet, frames)
            save_indexed(os.path.join(DST, name + '.png'), w, h, img)
            print('ok fx', name, len(frames), 'frames de', w // len(frames), 'x', h)
    return counts


if __name__ == '__main__':
    for base in (sys.argv[1:] or FRAMES_MK2):
        build(base)
    if not sys.argv[1:]:
        build_toasty()
