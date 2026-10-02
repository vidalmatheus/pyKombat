# Fatalities procedurais: tudo é função do tempo t (+ semente), sem estado —
# assim o convidado online desenha exatamente o mesmo que o host.
import math
import random
import pygame
import assets

G = 0.5
# efeitos (sheet, nº de frames) gerados por tools/mk2_sprites.py
FREEZE_FX = ('freezefx', 2)   # bola de gelo do Sub-Zero
FIRE_FX = ('firebreath', 4)   # fogo saindo da boca do Scorpion
BURN_FX = ('fireburn', 6)     # fogo tomando a vítima
_tiles = {}
_drops = {}


def _chunks(surf, size=14):
    """Recorta o sprite da vítima em pedaços (só os que têm pixels)."""
    key = (id(surf), size)
    tiles = _tiles.get(key)
    if tiles is None:
        tiles = []
        w, h = surf.get_size()
        for ty in range(0, h, size):
            for tx in range(0, w, size):
                r = pygame.Rect(tx, ty, min(size, w - tx), min(size, h - ty))
                piece = surf.subsurface(r)
                if piece.get_bounding_rect().w > 0:
                    tiles.append((r, piece))
        _tiles[key] = tiles
        if len(_tiles) > 40:
            _tiles.clear()
            _tiles[key] = tiles
    return tiles


def _drawChunks(screen, surf, left, top, ground, tau, seed, power=1.0, upward=1.0, tint=None, spin=True,
                fade=None):
    rng = random.Random(seed)
    cx = surf.get_width() / 2
    for r, piece in _chunks(surf):
        vx = (r.centerx - cx) * 0.07 * power + rng.uniform(-3, 3) * power
        vy = -rng.uniform(3, 11) * upward
        rot = rng.uniform(-14, 14) if spin else 0
        x = left + r.x + vx * tau
        y = top + r.y + vy * tau + 0.5 * G * tau * tau
        rest = ground - r.h
        if y > rest:
            y = rest
            # no chão: desliza um pouco e para
            x = left + r.x + vx * min(tau, 40)
            rot = 0
        img = piece
        if tint is not None:
            img = assets.tinted(piece, tint[0], tint[1], tint[2])
        if rot:
            img = pygame.transform.rotate(img, rot * tau % 360)
        if fade is not None and tau > fade:
            a = max(0, 255 - (tau - fade) * 6)
            if a == 0:
                continue
            img = img.copy()
            img.set_alpha(a)
        screen.blit(img, (int(x), int(y)))


def _blood(screen, x0, y0, ground, tau, seed, n=60, spread=7.0, up=9.0, color=(170, 0, 0)):
    key = (seed, n)
    drops = _drops.get(key)
    if drops is None:
        rng = random.Random(seed)
        drops = [(rng.uniform(-spread, spread), -rng.uniform(2, up), rng.randint(2, 5),
                  rng.choice(((150, 0, 0), (200, 10, 10), (110, 0, 0))), rng.uniform(0, 12),
                  rng.randint(0, 7)) for _ in range(n)]
        _drops[key] = drops
        if len(_drops) > 60:
            _drops.clear()
            _drops[key] = drops
    for vx, vy, size, col, delay, jy in drops:
        t = tau - delay
        if t < 0:
            continue
        x = x0 + vx * t
        y = y0 + vy * t + 0.5 * G * t * t
        floor = ground - jy
        if y >= floor:
            land = (-vy + math.sqrt(max(0.0, vy * vy + 2 * G * (floor - y0)))) / G
            x = x0 + vx * land * 0.6
            pygame.draw.ellipse(screen, col, (int(x) - size, floor - 1, size * 2 + 2, 3))
        else:
            pygame.draw.rect(screen, col, (int(x), int(y), size, size))


def _glow(screen, x, y, r, color, alpha):
    s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    pygame.draw.circle(s, color + (alpha,), (r, r), r)
    screen.blit(s, (int(x - r), int(y - r)))


def draw(screen, kind, t, victimSurf, left, top, ground, seed, winnerX):
    """Desenha a vítima + efeito da fatality `kind` no tick t."""
    if kind == 'electro':
        drawElectro(screen, t, victimSurf, left, top, ground, seed)
    elif kind == 'hatsplit':
        drawHatSplit(screen, t, victimSurf, left, top, ground, seed, winnerX)
    elif kind == 'soulsteal':
        drawSoulSteal(screen, t, victimSurf, left, top, ground, seed, winnerX)
    elif kind == 'deepfreeze':
        drawDeepFreeze(screen, t, victimSurf, left, top, ground, seed, winnerX)
    elif kind == 'firebreath':
        drawFireBreath(screen, t, victimSurf, left, top, ground, seed, winnerX)


# tempos sincronizados com as animações 'fatal' de fighter.py
THROW_AT = 60       # deep freeze: a bola de gelo sai da mão (índice 10 da animação)
FREEZE_AT = 72      # ... acerta e a vítima começa a congelar
SHATTER_AT = 110    # ... o uppercut (índice 16) a estilhaça


def _fxCentered(screen, name, n, frame, cx, cy, facing):
    sh = assets.fxSheet(name, n)
    img = sh.frame(frame, facing)
    br = img.get_bounding_rect()
    screen.blit(img, (int(cx - br.centerx), int(cy - br.centery)))


def drawDeepFreeze(screen, t, victimSurf, left, top, ground, seed, winnerX):
    """Deep Freeze (Sub-Zero, MK2): a bola de gelo congela a vítima por inteiro e
    o uppercut a estilhaça em pedaços de gelo."""
    w, h = victimSurf.get_size()
    body = victimSurf.get_bounding_rect()
    cx = left + body.centerx
    facing = 1 if cx > winnerX else -1
    if t < SHATTER_AT:
        k = 0 if t < FREEZE_AT else min(4, (t - FREEZE_AT) // 8 + 1)
        img = victimSurf
        if k:
            img = assets.tinted(victimSurf, ('ice', k), (255 - 30 * k, 255 - 12 * k, 255), pygame.BLEND_RGB_MULT)
            img = assets.tinted(img, ('ice+', k), (18 * k, 34 * k, 48 * k), pygame.BLEND_RGB_ADD)
        screen.blit(img, (left, top))
        if THROW_AT <= t < FREEZE_AT:     # a bola de gelo voa da mão até a vítima
            f = (t - THROW_AT) / (FREEZE_AT - THROW_AT)
            hx = winnerX + facing * 40
            hy = top + body.y + 10
            _fxCentered(screen, FREEZE_FX[0], FREEZE_FX[1], (t // 2) % FREEZE_FX[1],
                        hx + (cx - hx) * f, hy + (top + body.y + body.h * 0.3 - hy) * f, facing)
        if FREEZE_AT <= t < FREEZE_AT + 10:
            _glow(screen, cx, top + body.y + body.h * 0.3, 14 + (t - FREEZE_AT) * 3, (200, 240, 255),
                  220 - (t - FREEZE_AT) * 20)
        if t > FREEZE_AT + 24:            # brilhos no gelo
            rng = random.Random(seed + t // 6)
            for _ in range(5):
                sx = left + body.x + rng.randint(0, body.w)
                sy = top + body.y + rng.randint(0, body.h)
                pygame.draw.line(screen, (240, 255, 255), (sx - 4, sy), (sx + 4, sy), 1)
                pygame.draw.line(screen, (240, 255, 255), (sx, sy - 4), (sx, sy + 4), 1)
    else:
        tau = t - SHATTER_AT
        ice = assets.tinted(victimSurf, ('ice', 4), (135, 207, 255), pygame.BLEND_RGB_MULT)
        ice = assets.tinted(ice, ('ice+', 4), (72, 136, 192), pygame.BLEND_RGB_ADD)
        _drawChunks(screen, ice, left, top, ground, tau, seed, power=1.6, upward=1.1, fade=60)
        if tau < 12:
            _glow(screen, cx, top + body.y + 50, 30 + tau * 5, (220, 250, 255), 200 - tau * 15)


FIRE_AT = 66        # toasty: o fogo sai da boca da caveira (índice 8 da animação)
FIRE_TRAVEL = 18    # ticks do fogo indo da boca até a vítima


def drawFireBreath(screen, t, victimSurf, left, top, ground, seed, winnerX):
    """Toasty (Scorpion, MK2): tira a máscara e cospe fogo; a vítima é tomada por
    uma coluna de fogo, fica carbonizada e desmancha em cinzas."""
    w, h = victimSurf.get_size()
    body = victimSurf.get_bounding_rect()
    cx = left + body.centerx
    facing = 1 if cx > winnerX else -1
    hitT = FIRE_AT + FIRE_TRAVEL
    burnEnd = hitT + 100
    if t < burnEnd:
        img = victimSurf
        if t >= hitT:   # queimando: vai escurecendo e treme
            k = min(4, (t - hitT) // 18 + 1)
            dark = 255 - 45 * k
            img = assets.tinted(victimSurf, ('burn', k), (255, dark, max(0, dark - 60)), pygame.BLEND_RGB_MULT)
        screen.blit(img, (left + ((t % 3) - 1 if hitT <= t else 0), top))
    else:
        tau = t - burnEnd
        ash = assets.tinted(victimSurf, ('burn', 5), (40, 30, 25), pygame.BLEND_RGB_MULT)
        _drawChunks(screen, ash, left, top, ground, tau, seed, power=0.25, upward=0.15, spin=False)
    mouthX = winnerX + facing * 30
    mouthY = top + body.y + 18
    if FIRE_AT <= t < hitT:          # o fogo sai da boca e voa até a vítima
        f = (t - FIRE_AT) / FIRE_TRAVEL
        frame = min(FIRE_FX[1] - 1, int(f * FIRE_FX[1]))
        _fxCentered(screen, FIRE_FX[0], FIRE_FX[1], frame, mouthX + (cx - mouthX) * f,
                    mouthY + (top + body.y + body.h * 0.45 - mouthY) * f, facing)
    if hitT <= t < burnEnd + 10:     # bola de fogo -> coluna de fogo -> caveira de fogo (MK2)
        n = BURN_FX[1]
        frame = min(n - 1, (t - hitT) // 12)
        if frame >= n - 2:            # as duas últimas (caveira) alternam enquanto queima
            frame = n - 2 + (t // 6) % 2
        sh = assets.fxSheet(BURN_FX[0], n)
        img = sh.frame(frame, facing)
        br = img.get_bounding_rect()
        screen.blit(img, (int(cx - br.centerx), int(ground - br.bottom)))


def _soulFrame(screen, frame, cx, cy, facing):
    # sprites da alma (MK2): desenhados pelo centro do contorno
    sh = assets.fxSheet('soul', 10)
    img = sh.frame(frame, facing)
    br = img.get_bounding_rect()
    screen.blit(img, (int(cx - br.centerx), int(cy - br.centery)))


def drawSoulSteal(screen, t, victimSurf, left, top, ground, seed, winnerX):
    """Soul steal (Shang Tsung): a alma verde sai da vítima, voa até a mão dele e
    é absorvida; o corpo vazio escurece e desmancha em cinzas."""
    w, h = victimSurf.get_size()
    body = victimSurf.get_bounding_rect()
    cx = left + body.centerx
    cy = top + body.centery
    facing = 1 if winnerX < cx else -1     # os sprites da alma voam para a esquerda
    handX, handY = winnerX + (55 if winnerX < cx else -55), ground - 100
    if t < 150:
        k = 0 if t < 20 else min(3, (t - 20) // 15 + 1)
        img = victimSurf
        if k:  # vai perdendo a cor enquanto a alma sai
            img = assets.tinted(victimSurf, ('soul', k), (255 - 45 * k, 255 - 25 * k, 255 - 45 * k), pygame.BLEND_RGB_MULT)
        screen.blit(img, (left + ((t % 3) - 1 if 20 <= t < 60 else 0), top))
    else:
        tau = t - 150
        ash = assets.tinted(victimSurf, ('soul', 4), (70, 80, 70), pygame.BLEND_RGB_MULT)
        _drawChunks(screen, ash, left, top, ground, tau, seed, power=0.3, upward=0.2, spin=False)
    if 20 <= t < 60:            # a alma se levanta do corpo
        _soulFrame(screen, min(2, (t - 20) // 13), cx, cy - (t - 20) * 0.6, facing)
    elif 60 <= t < 100:         # voa em arco até a mão do Shang Tsung
        f = (t - 60) / 40
        x = cx + (handX - cx) * f
        y = (cy - 24) + (handY - cy + 24) * f - math.sin(f * math.pi) * 40
        _soulFrame(screen, 3 if f < 0.5 else 4, x, y, facing)
    elif 100 <= t < 140:        # é absorvida
        _soulFrame(screen, 5 + min(4, (t - 100) // 8), handX, handY, facing)
        _glow(screen, handX, handY, 18 + (t - 100) // 2, (120, 255, 120), max(0, 160 - (t - 100) * 4))


def drawHatSplit(screen, t, victimSurf, left, top, ground, seed, winnerX):
    """Hat slice (Kung Lao): o chapéu passa girando e corta a vítima ao meio, de
    cima a baixo; as duas metades caem cada uma para um lado."""
    w, h = victimSurf.get_size()
    body = victimSurf.get_bounding_rect()
    cx = left + body.centerx
    dirx = 1 if cx > winnerX else -1          # o chapéu vem do lado do Kung Lao
    cut = body.centerx                        # corte vertical no meio do corpo
    hitT = 60
    if t < hitT + 4:
        screen.blit(victimSurf, (left, top))
    else:
        tau = t - hitT - 4
        near = victimSurf.subsurface((0, 0, cut, h)) if dirx > 0 else victimSurf.subsurface((cut, 0, w - cut, h))
        far = victimSurf.subsurface((cut, 0, w - cut, h)) if dirx > 0 else victimSurf.subsurface((0, 0, cut, h))
        nearX = left if dirx > 0 else left + cut
        farX = left + cut if dirx > 0 else left
        # cada metade tomba para o próprio lado, girando no pé
        for img, x0, side in ((near, nearX, -dirx), (far, farX, dirx)):
            k = min(90, max(0, tau - 8) * 4)
            rot = pygame.transform.rotate(img, -k * side)
            br = rot.get_bounding_rect()
            px = x0 + img.get_width() / 2 + side * k / 90 * 40
            screen.blit(rot, (int(px - br.centerx), int(ground - br.bottom)))
        _blood(screen, cx, top + body.y + 30, ground, tau, seed, 80, 3, 12)
        _blood(screen, cx, top + body.y + 80, ground, tau, seed + 1, 50, 3, 8)
    # o chapéu: atravessa a vítima e volta para a mão
    if 30 <= t < 120:
        sh = assets.fxSheet('hat', 3)
        img = sh.frame((t // 3) % 3, 1)
        startX = winnerX + dirx * 40
        endX = cx + dirx * 140
        if t < hitT + 20:
            k = (t - 30) / (hitT + 20 - 30)
            hx = startX + (endX - startX) * k
        else:
            k = (t - hitT - 20) / (120 - hitT - 20)
            hx = endX + (startX - endX) * k
        hy = top + body.y + body.h * (0.15 + 0.7 * min(1.0, max(0.0, (t - 30) / (hitT - 30))))
        screen.blit(img, (int(hx - sh.w // 2), int(hy - sh.h // 2)))


def _skyBolt(screen, x, ground, frame):
    """Raio do Raiden (sprite do MK2) caindo do céu até o chão em x."""
    sh = assets.fxSheet('raidenbolt', 2, None)
    img = sh.frame(frame, 1)
    key = ('bolt', frame, ground)
    tall = _tiles.get(key)
    if tall is None:
        tall = pygame.transform.scale(img, (img.get_width(), ground))
        _tiles[key] = tall
    screen.blit(tall, (x - sh.w // 2, 0))


def drawElectro(screen, t, victimSurf, left, top, ground, seed):
    """Electrocution (Raiden): três raios na vítima, que fica branca e explode."""
    w, h = victimSurf.get_size()
    cx = left + w // 2
    body = victimSurf.get_bounding_rect()
    strikes = (40, 75, 110)
    if t < 150:
        dark = pygame.Surface(screen.get_size())
        dark.fill((5, 5, 30))
        dark.set_alpha(min(140, t * 4))
        screen.blit(dark, (0, 0))
        img = victimSurf
        shocked = t >= strikes[0]
        if shocked and (t // 3) % 2 == 0:  # pisca em silhueta branca (como no MK2)
            img = assets.tinted(victimSurf, 'electro', (255, 255, 255), pygame.BLEND_RGB_ADD)
        elif shocked:
            img = assets.tinted(victimSurf, 'electro2', (60, 110, 160), pygame.BLEND_RGB_ADD)
        screen.blit(img, (left + ((t % 3) - 1 if shocked else 0), top))
        if shocked:
            rng = random.Random(seed + t // 2)
            for _ in range(3):  # faíscas pelo corpo
                x0 = left + body.x + rng.randint(0, body.w)
                y0 = top + body.y + rng.randint(0, body.h)
                pygame.draw.line(screen, (200, 240, 255), (x0, y0),
                                 (x0 + rng.randint(-14, 14), y0 + rng.randint(-14, 14)), 2)
        for b in strikes:
            if b <= t < b + 9:
                _skyBolt(screen, cx, ground, 0 if t < b + 5 else 1)
                flash = pygame.Surface(screen.get_size())
                flash.fill((220, 240, 255))
                flash.set_alpha(130 - (t - b) * 14)
                screen.blit(flash, (0, 0))
    else:
        tau = t - 150
        white = assets.tinted(victimSurf, 'electro', (255, 255, 255), pygame.BLEND_RGB_ADD)
        _drawChunks(screen, victimSurf if tau > 6 else white, left, top, ground, tau, seed, power=1.4)
        _blood(screen, cx, top + body.y + 50, ground, tau, seed, 80, 8, 11)
        if tau < 8:
            flash = pygame.Surface(screen.get_size())
            flash.fill((235, 245, 255))
            flash.set_alpha(220 - tau * 25)
            screen.blit(flash, (0, 0))
            _glow(screen, cx, top + body.y + 50, 40 + tau * 6, (180, 230, 255), 220 - tau * 20)
