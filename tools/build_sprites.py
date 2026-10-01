"""Gera res/sprites/<base>/*.png a partir das spritesheets originais (res/Char).

Cada sheet é:
  * normalizada para o lutador olhar para a DIREITA (o jogo espelha em tempo real);
  * convertida para PNG paletizado (8 bits, índice 0 transparente).

A paleta é o que permite criar novos lutadores por troca de cores (palette
swap, exatamente como o MK fazia com Reptile, Smoke, Noob Saibot...): em tempo
de execução só os ~255 índices da paleta são recoloridos, sem tocar pixel a
pixel (o que seria lento demais no navegador/pygbag).

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


def build_spear_head():
    # ponta do arpão do Scorpion (a corda é desenhada no código), já virada p/ direita
    img = Image.open(os.path.join(SRC, 'Scorpion', 'projectile.png')).convert('RGBA')
    head = img.crop((1348, 58, 1381, 66)).transpose(Image.FLIP_LEFT_RIGHT)
    palettize(head).save(os.path.join(DST, 'spearhead.png'), optimize=True, transparency=0)


if __name__ == '__main__':
    for base, sheets in SHEETS.items():
        for name, frames in sheets.items():
            build_sheet(base, name, frames)
            print('ok', base, name)
    build_spear_head()
