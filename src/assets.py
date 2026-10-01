# Carregamento e cache de imagens/sons.
#
# As spritesheets em res/sprites são PNGs paletizados (ver tools/build_sprites.py)
# já virados para a direita. A segunda cor de um lutador (os dois lados com o
# mesmo personagem) é só uma troca de paleta (≤256 cores), instantânea até no
# navegador.
import colorsys
import pygame
import characters

SPRITE_DIR = 'res/sprites/'
CELL_W = 200
CELL_H = 164

# nº de frames de cada sheet (mesma tabela de tools/build_sprites.py e
# tools/mk2_sprites.py)
_MK1 = {'dance': 7, 'walk': 9, 'jump': 3, 'crouch': 3, 'Apunch': 3, 'Bpunch': 11,
        'Cpunch': 3, 'Dpunch': 5, 'Akick': 7, 'Bkick': 9, 'Ckick': 7, 'Dkick': 6,
        'Ekick': 3, 'Epunch': 3, 'Ahit': 3, 'Bhit': 3, 'Chit': 6, 'Dhit': 2, 'Ehit': 3,
        'Fhit': 14, 'Ghit': 11, 'Ablock': 3, 'Bblock': 3, 'dizzy': 7, 'fatalityhit': 10}
# lutadores do MK2 (SNES): mesmas tiras comuns, com a quantidade de frames de cada um
_MK2 = {'jump': 3, 'spin': 8, 'crouch': 3, 'Apunch': 3, 'Bpunch': 11, 'Cpunch': 3, 'Dpunch': 5,
        'Akick': 7, 'Bkick': 9, 'Ckick': 7, 'Dkick': 6, 'Ekick': 3, 'Epunch': 3, 'Ahit': 3,
        'Bhit': 3, 'Chit': 6, 'Ehit': 3, 'Fhit': 14, 'Ghit': 11, 'Ablock': 3, 'Bblock': 3,
        'fatalityhit': 10}
FRAMES = {
    'Sub-Zero': dict(_MK1, hitSpecial=3, Special=12, fatality=17, spin=8, win=3),
    'Scorpion': dict(_MK1, Special=7, fatality=20),
    'LiuKang': dict(_MK2, dance=6, walk=9, dizzy=6, win=4, Special=6, Fkick=2, fatality=12),
    'Kitana': dict(_MK2, dance=5, walk=8, dizzy=5, win=4, Special=6, Special2=6, fatality=8),
    'Raiden': dict(_MK2, dance=8, walk=8, dizzy=7, win=5, Special=6, Fkick=2, fatality=3),
    'KungLao': dict(_MK2, dance=6, walk=9, dizzy=6, win=6, Special=6, fatality=10),
    'JohnnyCage': dict(_MK2, dance=5, walk=8, dizzy=6, win=5, Special=6, Fkick=2, fatality=7),
    'Baraka': dict(_MK2, dance=6, walk=9, dizzy=5, win=4, Special=6, Fkick=4, fatality=11),
    'Mileena': dict(_MK2, dance=10, walk=8, dizzy=5, win=6, Special=6, Fkick=8, fatality=14),
    'ShangTsung': dict(_MK2, dance=5, walk=9, dizzy=5, win=4, Special=6, Special2=6, fatality=5),
    'Jax': dict(_MK2, dance=5, walk=9, dizzy=5, win=6, Special=6, Special2=6, fatality=10),
}
# ponto de ancoragem (centro do corpo) dentro do frame, para sheets onde o
# corpo não está no meio do frame
ANCHOR_X = {('Sub-Zero', 'fatality'): 64, ('Scorpion', 'fatality'): 64}

# matizes da roupa de cada corpo-base (graus mín., máx., saturação mín., brilho mín.)
# — o resto (pele, preto, sangue) fica
COSTUME_HUE = {'Sub-Zero': (150, 250, 0.12, 0.0), 'Scorpion': (29, 66, 0.08, 0.30),
               'LiuKang': (350, 8, 0.55, 0.25), 'Kitana': (205, 250, 0.35, 0.0),
               'Raiden': (180, 205, 0.35, 0.0), 'KungLao': (180, 210, 0.30, 0.0),
               'JohnnyCage': (345, 10, 0.45, 0.15), 'Baraka': (345, 12, 0.45, 0.2),
               'Mileena': (265, 320, 0.30, 0.0), 'ShangTsung': (40, 65, 0.40, 0.2),
               'Jax': (350, 12, 0.45, 0.2)}
# roupa do "espelho" (mesmo lutador dos dois lados) quando o personagem não troca a paleta
ALT_COSTUME = {'Sub-Zero': (228, 1.0, 0.75), 'Scorpion': (30, 1.0, 0.88),
               'LiuKang': (222, 0.9, 0.85),     # calça azul (como a 2ª cor do MK2)
               'Kitana': (300, 0.85, 0.85),     # roxo da Mileena
               'Raiden': (28, 0.9, 0.9),
               'KungLao': (350, 0.85, 0.8),     # roupa vermelha
               'JohnnyCage': (215, 0.9, 0.9),   # faixa e calça azuis
               'Baraka': (110, 0.8, 0.8),       # detalhes verdes
               'Mileena': (140, 0.8, 0.75),     # verde da Jade
               'ShangTsung': (270, 0.8, 0.8),   # manto roxo
               'Jax': (210, 0.8, 0.8)}          # calça azul


def _clamp(v):
    return 0.0 if v < 0 else 1.0 if v > 1 else v


def _transform(rgb, spec):
    h, s, v = colorsys.rgb_to_hsv(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)
    hue, smul, vmul = spec
    r, g, b = colorsys.hsv_to_rgb(hue / 360.0, _clamp(s * smul), _clamp(v * vmul))
    return (int(r * 255), int(g * 255), int(b * 255))


def _inRange(rgb, rng):
    lo, hi, smin, vmin = rng
    h, s, v = colorsys.rgb_to_hsv(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)
    h *= 360
    inHue = lo <= h <= hi if lo <= hi else (h >= lo or h <= hi)  # lo > hi: faixa que passa do 360 (vermelho)
    return inHue and s > smin and v > vmin


def recolorPalette(palette, char, alt):
    """Cores do "espelho" (mesmo lutador dos dois lados): troca a cor da roupa."""
    costume = ALT_COSTUME.get(char.base) if alt else None
    if costume is None:
        return palette
    out = []
    for i, c in enumerate(palette):
        c = tuple(c[:3])
        if i == 0:
            out.append(c)  # índice transparente
        elif _inRange(c, COSTUME_HUE[char.base]):
            out.append(_transform(c, costume))
        else:
            out.append(c)
    return out


class Sheet:
    """Uma tira de animação: frames lado a lado, virados p/ direita."""

    def __init__(self, surf, frames, anchorX):
        self.n = frames
        self.surf = surf
        self.w = surf.get_width() // frames
        self.h = surf.get_height()
        self.anchorX = anchorX
        self._flipped = None
        self._frames = {}
        self._masks = {}
        self._hitMasks = {}

    def frame(self, i, facing):
        """Surface de um frame (facing: +1 direita, -1 esquerda)."""
        i = max(0, min(self.n - 1, int(i)))
        key = (i, facing)
        f = self._frames.get(key)
        if f is None:
            f = self.surf.subsurface((i * self.w, 0, self.w, self.h))
            if facing < 0:
                f = pygame.transform.flip(f, True, False)
            self._frames[key] = f
        return f

    def anchor(self, facing):
        return self.anchorX if facing > 0 else self.w - self.anchorX

    def mask(self, i, facing):
        key = (int(i), facing)
        m = self._masks.get(key)
        if m is None:
            m = pygame.mask.from_surface(self.frame(i, facing), 127)
            self._masks[key] = m
        return m

    def hitMask(self, i, facing, reach=18):
        """Máscara só da parte do corpo à frente do lutador (braço/perna do golpe)."""
        key = (int(i), facing)
        m = self._hitMasks.get(key)
        if m is None:
            full = self.mask(i, facing)
            m = pygame.mask.Mask((self.w, self.h))
            ax = self.anchor(facing)
            if facing > 0:
                region = pygame.Rect(ax + reach, 0, self.w - ax - reach, self.h)
            else:
                region = pygame.Rect(0, 0, max(0, ax - reach), self.h)
            if region.w > 0:
                cut = pygame.mask.Mask(region.size, fill=True)
                m.draw(cut, region.topleft)
                m = m.overlap_mask(full, (0, 0))
            self._hitMasks[key] = m
        return m


_sheets = {}
_images = {}
_sounds = {}
_fonts = {}
_tinted = {}


def sheet(char, name, alt=False):
    """Sheet `name` já recolorida para o personagem `char`."""
    key = (char.name, alt, name)
    s = _sheets.get(key)
    if s is not None:
        return s
    frames = FRAMES[char.base].get(name)
    if frames is None:
        if name == 'spin':
            s = _synthSpin(char, alt)
            _sheets[key] = s
            return s
        return None
    raw = pygame.image.load(SPRITE_DIR + char.base + '/' + name + '.png')
    pal = raw.get_palette() if raw.get_bitsize() == 8 else None
    if pal is not None:
        raw.set_palette(recolorPalette(pal, char, alt))
        if raw.get_colorkey() is None:
            raw.set_colorkey(0)  # índice 0 = transparente (tools/build_sprites.py)
    surf = raw.convert_alpha()
    s = Sheet(surf, frames, ANCHOR_X.get((char.base, name), surf.get_width() // frames // 2))
    _sheets[key] = s
    return s


def _synthSpin(char, alt):
    # cambalhota p/ corpos sem sheet de 'spin': gira o frame encolhido do pulo
    tuck = sheet(char, 'jump', alt).frame(2, 1)
    strip = pygame.Surface((CELL_W * 8, CELL_H), pygame.SRCALPHA)
    body = tuck.subsurface(tuck.get_bounding_rect()).copy()
    for i in range(8):
        r = pygame.transform.rotate(body, -45 * i)
        strip.blit(r, (i * CELL_W + (CELL_W - r.get_width()) // 2,
                       CELL_H - 40 - r.get_height() // 2 - 30))
    return Sheet(strip, 8, CELL_W // 2)


def fxSheet(name, frames, anchorX=None):
    """Sheet de efeito (sem troca de paleta), ex.: a rajada de gelo original.
    anchorX None = frente do efeito (borda direita do frame, tools/mk2_sprites.py)."""
    key = ('fx', name)
    s = _sheets.get(key)
    if s is None:
        raw = pygame.image.load(SPRITE_DIR + name + '.png')
        if raw.get_bitsize() == 8 and raw.get_colorkey() is None:
            raw.set_colorkey(0)
        if anchorX is None:
            anchorX = raw.get_width() // frames - 2
        s = Sheet(raw.convert_alpha(), frames, anchorX)
        _sheets[key] = s
    return s


def hasSheet(char, name):
    return name in FRAMES[char.base]


def preload(char, alt=False):
    for name in FRAMES[char.base]:
        sheet(char, name, alt)


def tinted(surf, key, color, mode):
    """Cópia de um frame com tinta (congelado, carbonizado...). Cacheada."""
    k = (id(surf), key)
    entry = _tinted.get(k)
    if entry is None or entry[0] is not surf:  # id() pode ser reaproveitado
        t = surf.copy()
        t.fill(color, special_flags=mode)
        if len(_tinted) > 600:
            _tinted.clear()
        entry = _tinted[k] = (surf, t)
    return entry[1]


def image(path, alpha=True):
    s = _images.get(path)
    if s is None:
        s = pygame.image.load(path)
        s = s.convert_alpha() if alpha else s.convert()
        _images[path] = s
    return s


def scaledImage(path, size):
    key = (path, size)
    s = _images.get(key)
    if s is None:
        s = pygame.transform.smoothscale(image(path), size)
        _images[key] = s
    return s


def portrait(char, alt=False, size=(100, 100)):
    """Retrato p/ seleção de lutadores: cabeça/tronco do frame parado."""
    key = ('portrait', char.name, alt, size)
    s = _images.get(key)
    if s is None:
        sh = sheet(char, 'dance', alt)
        f = sh.frame(0, 1)
        top = max(0, f.get_bounding_rect().y - 6)   # enquadra a partir do topo da cabeça
        crop = f.subsurface(pygame.Rect(sh.anchorX - 45, top, 90, 90)).copy()
        s = pygame.transform.scale(crop, size)
        _images[key] = s
    return s


def sound(name):
    s = _sounds.get(name)
    if s is None:
        try:
            s = pygame.mixer.Sound('res/Sound/' + name + '.ogg')
        except Exception as e:  # som ausente não pode derrubar o jogo
            print('sound error', name, e)
            s = False
        _sounds[name] = s
    return s or None


def playSound(name, volume=1.0):
    s = sound(name)
    if s is not None:
        s.set_volume(volume)
        s.play()


def font(size):
    f = _fonts.get(size)
    if f is None:
        f = pygame.font.Font('res/mk2.ttf', size)
        _fonts[size] = f
    return f


def charByIndex(i):
    return characters.ROSTER[i]
