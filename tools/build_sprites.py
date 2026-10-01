"""Gera res/sprites/<base>/*.png a partir das spritesheets originais (res/Char).

Cada sheet é:
  * normalizada para o lutador olhar para a DIREITA (o jogo espelha em tempo real);
  * convertida para PNG paletizado (8 bits, índice 0 transparente).

A paleta é o que permite a segunda cor de um lutador (os dois lados com o
mesmo personagem): em tempo de execução só os ~255 índices da paleta são
recoloridos, sem tocar pixel a pixel (o que seria lento demais no navegador).

Os lutadores do Mortal Kombat II saem das folhas do SNES em
res/Char/<base>/sheet.png, recortadas por tools/mk2_sprites.py (chamado no fim
deste script; também roda sozinho, sem Pillow).

Uso: python3 tools/build_sprites.py   (requer Pillow)
"""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'res', 'Char')
DST = os.path.join(ROOT, 'res', 'sprites')

# sheet -> nº de frames (largura de frame = largura/frames)
SHEETS = {
    'Sub-Zero': {'dance': 7, 'walk': 9, 'jump': 3, 'crouch': 3, 'Apunch': 3, 'Bpunch': 11,
                 'Cpunch': 3, 'Dpunch': 5, 'Akick': 7, 'Bkick': 9, 'Ckick': 7, 'Dkick': 6,
                 'Ekick': 3, 'Epunch': 3, 'Ahit': 3, 'Bhit': 3, 'Chit': 6, 'Dhit': 2, 'Ehit': 3,
                 'Fhit': 14, 'Ghit': 11, 'hitSpecial': 3, 'Ablock': 3, 'Bblock': 3,
                 'Special': 12, 'dizzy': 7, 'fatality': 17, 'fatalityhit': 10, 'spin': 8, 'win': 3},
    'Scorpion': {'dance': 7, 'walk': 9, 'jump': 3, 'crouch': 3, 'Apunch': 3, 'Bpunch': 11,
                 'Cpunch': 3, 'Dpunch': 5, 'Akick': 7, 'Bkick': 9, 'Ckick': 7, 'Dkick': 6,
                 'Ekick': 3, 'Epunch': 3, 'Ahit': 3, 'Bhit': 3, 'Chit': 6, 'Dhit': 2, 'Ehit': 3,
                 'Fhit': 14, 'Ghit': 11, 'Ablock': 3, 'Bblock': 3,
                 'Special': 7, 'dizzy': 7, 'fatality': 20, 'fatalityhit': 10},
}
# orientação original: Sub-Zero olha p/ direita, Scorpion p/ esquerda — mas as
# sheets de fatality foram desenhadas espelhadas em relação às demais
FACES_LEFT = {
    'Sub-Zero': {'fatality'},
    'Scorpion': set(SHEETS['Scorpion']) - {'fatality'},
}


def palettize(img):
    """RGBA -> 'P' com índice 0 transparente (alpha binário)."""
    img = img.convert('RGBA')
    w, h = img.size
    alpha = img.getchannel('A').point(lambda a: 255 if a >= 110 else 0)
    rgb = Image.new('RGB', (w, h), (0, 0, 0))
    rgb.paste(img.convert('RGB'), mask=alpha)
    q = rgb.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    # desloca os índices em +1 e reserva o 0 para o transparente
    pal = q.getpalette()[:255 * 3]
    shifted = q.point(lambda i: i + 1)
    out = Image.new('P', (w, h), 0)
    out.paste(shifted, mask=alpha)
    out.putpalette([255, 0, 255] + pal + [0, 0, 0] * (256 - 1 - len(pal) // 3))
    out.info['transparency'] = 0
    return out


def build_sheet(base, name, frames):
    img = Image.open(os.path.join(SRC, base, name + '.png')).convert('RGBA')
    fw = img.width // frames
    if name in FACES_LEFT[base]:
        out = Image.new('RGBA', (fw * frames, img.height))
        for i in range(frames):
            cell = img.crop((i * fw, 0, (i + 1) * fw, img.height)).transpose(Image.FLIP_LEFT_RIGHT)
            out.paste(cell, (i * fw, 0))
        img = out
    p = palettize(img)
    os.makedirs(os.path.join(DST, base), exist_ok=True)
    p.save(os.path.join(DST, base, name + '.png'), optimize=True, transparency=0)


# Na fatality original os frames 9-15 foram desenhados de costas: o lutador
# virava para trás e golpeava o vazio, como se trocasse de lado com a vítima.
# Esses frames são espelhados em torno do próprio quadril (o corpo fica onde
# está e o golpe passa a ir na direção da vítima). Feito depois da paleta, só
# com pngio (sem Pillow).
REFACE = {('Sub-Zero', 'fatality'): range(9, 16), ('Scorpion', 'fatality'): range(9, 16)}


def reface(base, name, frames, count):
    import pngio
    from mk2_sprites import save_indexed
    path = os.path.join(DST, base, name + '.png')
    w, h, px = pngio.read(path)
    fw = w // count
    for k in frames:
        cell = [row[k * fw:(k + 1) * fw] for row in px]
        band = sorted(x for y in range(h - 75, h - 60) for x in range(fw) if cell[y][x])
        hip = band[len(band) // 2]
        xs = [x for row in cell for x, c in enumerate(row) if c is not None]
        # espelho em torno do quadril; se o golpe passar da borda, recua o corpo
        shift = min(0, (fw - 1) - (2 * hip - min(xs)))
        for y in range(h):
            row = [None] * fw
            for x, c in enumerate(cell[y]):
                nx = 2 * hip - x + shift
                if c is not None and 0 <= nx < fw:
                    row[nx] = c
            px[y][k * fw:(k + 1) * fw] = row
    save_indexed(path, w, h, px)


def build_spear_head():
    # ponta do arpão do Scorpion (a corda é desenhada no código), já virada p/ direita
    img = Image.open(os.path.join(SRC, 'Scorpion', 'projectile.png')).convert('RGBA')
    head = img.crop((1348, 58, 1381, 66)).transpose(Image.FLIP_LEFT_RIGHT)
    palettize(head).save(os.path.join(DST, 'spearhead.png'), optimize=True, transparency=0)


# rajada de gelo original do Sub-Zero. A tira original desenha a trajetória
# inteira (12 "fotos" do gelo avançando); cada foto é recortada para um frame
# de 240x100 com o ponto de referência em x=200: a frente do gelo (saída e voo)
# ou o centro do estilhaço (impacto). Frames: 0-4 saindo, 5-6 voando, 7-11 impacto.
ICE_FX_W = 240
ICE_FX_ANCHOR = 200
ICE_FX = [  # (x0, x1, âncora) na tira original; âncora None = borda da frente
    (0, 40, None), (255, 320, None), (510, 610, None), (765, 890, None), (1010, 1150, None),
    (1280, 1465, None), (1500, 1720, None),
    (1845, 1980, 1950), (2125, 2228, 2201), (2395, 2490, 2452), (2655, 2750, 2700), (2895, 3000, 2955),
]


def build_ice_fx():
    img = Image.open(os.path.join(SRC, 'Sub-Zero', 'projectile.png')).convert('RGBA')
    out = Image.new('RGBA', (ICE_FX_W * len(ICE_FX), img.height))
    for i, (x0, x1, anchor) in enumerate(ICE_FX):
        piece = img.crop((x0, 0, x1, img.height))
        bbox = piece.getchannel('A').getbbox()
        ref = (x0 + bbox[2]) if anchor is None else anchor
        dx = i * ICE_FX_W + ICE_FX_ANCHOR - (ref - x0)
        out.alpha_composite(piece, (max(i * ICE_FX_W, dx), 0),
                            (max(0, i * ICE_FX_W - dx), 0))
    palettize(out).save(os.path.join(DST, 'icefx.png'), optimize=True, transparency=0)


if __name__ == '__main__':
    for base, sheets in SHEETS.items():
        for name, frames in sheets.items():
            build_sheet(base, name, frames)
            print('ok', base, name)
    for (base, name), frames in REFACE.items():
        reface(base, name, frames, SHEETS[base][name])
    build_spear_head()
    build_ice_fx()
    import mk2_sprites  # lutadores do MK2 (SNES)
    for base in mk2_sprites.FRAMES_MK2:
        mk2_sprites.build(base)
    mk2_sprites.build_toasty()
