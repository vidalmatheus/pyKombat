# Fatalities procedurais: tudo é função do tempo t (+ semente), sem estado —
# assim o convidado online desenha exatamente o mesmo que o host.
import math
import random
import pygame
import assets

G = 0.5
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


def _bolt(screen, x0, y0, x1, y1, seed, color=(230, 220, 255)):
    rng = random.Random(seed)
    pts = [(x0, y0)]
    n = 9
    for i in range(1, n):
        f = i / n
        pts.append((x0 + (x1 - x0) * f + rng.uniform(-28, 28), y0 + (y1 - y0) * f))
    pts.append((x1, y1))
    pygame.draw.lines(screen, (120, 80, 255), False, pts, 7)
    pygame.draw.lines(screen, color, False, pts, 3)


def draw(screen, kind, t, victimSurf, left, top, ground, seed, winnerX):
    """Desenha a vítima + efeito da fatality `kind` no tick t."""
    w, h = victimSurf.get_size()
    cx = left + w // 2
    body = victimSurf.get_bounding_rect()
    bodyTop = top + body.y

    if kind == 'melt':
        if t < 40:
            k = min(3, t // 10)
            img = assets.tinted(victimSurf, ('melt', k), (255 - 50 * k, 255, 255 - 60 * k), pygame.BLEND_RGB_MULT) if k else victimSurf
            screen.blit(img, (left, top))
        squash = 0.0 if t < 40 else min(1.0, (t - 40) / 120)
        pw = int(40 + 120 * squash)
        pygame.draw.ellipse(screen, (60, 150, 20), (cx - pw // 2, ground - 8, pw, 14))
        pygame.draw.ellipse(screen, (120, 230, 40), (cx - pw // 2 + 6, ground - 6, pw - 12, 8))
        if 40 <= t < 165:
            src = assets.tinted(victimSurf, ('melt', 3), (105, 255, 75), pygame.BLEND_RGB_MULT)
            crop = src.subsurface(body)
            nh = max(4, int(body.h * (1 - 0.95 * squash)))
            nw = int(body.w * (1 + 0.6 * squash))
            img = pygame.transform.scale(crop, (nw, nh))
            screen.blit(img, (cx - nw // 2 + (body.centerx - w // 2), ground - nh))
        rng = random.Random(seed + t // 6)
        for _ in range(4 if t > 30 else 0):
            bx = cx + rng.randint(-pw // 2 + 4, pw // 2 - 4)
            pygame.draw.circle(screen, (170, 255, 90), (bx, ground - rng.randint(2, 14)), rng.randint(2, 5), 1)
        if t > 170:  # sobrou a caveira
            pygame.draw.circle(screen, (235, 230, 210), (cx, ground - 12), 10)
            pygame.draw.circle(screen, (20, 20, 20), (cx - 4, ground - 13), 3)
            pygame.draw.circle(screen, (20, 20, 20), (cx + 4, ground - 13), 3)
            pygame.draw.line(screen, (235, 230, 210), (cx + 14, ground - 4), (cx + 34, ground - 8), 4)

    elif kind == 'bomb':
        if t < 70:
            shake = (t % 4 - 2) if t > 40 else 0
            screen.blit(victimSurf, (left + shake, top))
            rng = random.Random(seed)
            for i in range(14):
                a = rng.uniform(0, 6.28) + t * 0.08 * (1 if i % 2 else -1)
                rad = 60 - t * 0.5 + rng.uniform(-8, 8)
                px = cx + math.cos(a) * rad
                py = bodyTop + body.h / 2 + math.sin(a) * rad * 1.2
                _glow(screen, px, py, 12 + i % 4 * 3, (150, 150, 155), min(200, t * 4))
        else:
            tau = t - 70
            _drawChunks(screen, victimSurf, left, top, ground, tau, seed, power=1.3)
            _blood(screen, cx, bodyTop + 60, ground, tau, seed, 90, 9, 12)
            if tau < 6:
                flash = pygame.Surface(screen.get_size())
                flash.fill((255, 250, 235))
                flash.set_alpha(220 - tau * 35)
                screen.blit(flash, (0, 0))
            if tau < 24:
                for rr, col in ((46, (255, 120, 20)), (30, (255, 210, 80)), (14, (255, 255, 220))):
                    _glow(screen, cx, bodyTop + 60, rr + tau, col, max(0, 230 - tau * 10))
                for i in range(10):
                    _glow(screen, cx + math.cos(i) * tau * 3, bodyTop + 60 + math.sin(i * 2) * tau * 2,
                          20, (90, 90, 95), max(0, 180 - tau * 6))

    elif kind == 'slice':
        cutY = body.y + int(body.h * 0.42)
        if t < 40:
            screen.blit(victimSurf, (left, top))
            if 20 <= t < 40:
                a = (t - 20) / 20
                x1 = left + body.x - 20
                x2 = int(x1 + (body.w + 40) * a)
                pygame.draw.line(screen, (200, 160, 255), (x1, top + cutY), (x2, top + cutY - 6), 4)
                pygame.draw.line(screen, (255, 255, 255), (x1, top + cutY), (x2, top + cutY - 6), 1)
        else:
            tau = t - 40
            upper = victimSurf.subsurface((0, 0, w, cutY))
            lower = victimSurf.subsurface((0, cutY, w, h - cutY))
            # metade de cima escorrega e cai girando
            dirx = 1 if cx > winnerX else -1
            ux = left + dirx * min(tau, 45) * 2.2
            uy = top + min(0.5 * G * tau * tau * 0.6, (h - cutY) - 18)
            ang = min(85, tau * 3) * -dirx
            img = pygame.transform.rotate(upper, ang)
            screen.blit(img, (int(ux), int(uy)))
            if tau < 50:
                screen.blit(lower, (left, top + cutY))
            else:
                img = pygame.transform.rotate(lower, min(90, (tau - 50) * 6) * dirx)
                screen.blit(img, (left + (w - img.get_width()) // 2, ground - img.get_height()))
            _blood(screen, cx, top + cutY, ground, tau, seed, 70, 4, 11)

    elif kind == 'slam':
        def lift(tt):
            if tt < 60:
                return tt / 60 * 160
            if tt < 70:
                return 160 - (tt - 60) / 10 * 160
            if tt < 110:
                return (tt - 70) / 40 * 130
            if tt < 120:
                return 130 - (tt - 110) / 10 * 130
            if tt < 160:
                return (tt - 120) / 40 * 90
            return 90
        if t < 165:
            dy = int(lift(t))
            img = assets.tinted(victimSurf, 'slam', (255, 120, 110), pygame.BLEND_RGB_MULT)
            _glow(screen, cx, top + body.centery - dy, 70, (255, 40, 40), 70)
            if t < 120:
                img = pygame.transform.rotate(img, 0 if t < 60 else 180 if t < 70 else 0)
            screen.blit(img, (left, top - dy))
            if t in range(70, 80) or t in range(120, 130):
                _blood(screen, cx, ground - 20, ground, t % 70 if t < 100 else t - 120, seed + t // 50, 20, 6, 6)
        else:
            tau = t - 165
            _drawChunks(screen, victimSurf, left, top - 90, ground, tau, seed, power=1.1, tint=('slam', (255, 120, 110), pygame.BLEND_RGB_MULT))
            _blood(screen, cx, top - 30, ground, tau, seed + 7, 80, 8, 8)

    elif kind == 'thunder':
        dark = pygame.Surface(screen.get_size())
        dark.fill((10, 0, 30))
        dark.set_alpha(min(150, t * 5))
        screen.blit(dark, (0, 0))
        level = sum(1 for b in (40, 70, 100) if t >= b)
        if t < 130:
            img = victimSurf
            if level:
                img = assets.tinted(victimSurf, ('char', level), (255 - 70 * level,) * 3, pygame.BLEND_RGB_MULT)
            screen.blit(img, (left + ((t % 3) - 1 if level else 0), top))
        else:
            tau = t - 130
            ash = assets.tinted(victimSurf, ('char', 3), (45, 45, 45), pygame.BLEND_RGB_MULT)
            _drawChunks(screen, ash, left, top, ground, tau, seed, power=0.25, upward=0.15, spin=False)
        for b in (40, 70, 100):
            if b <= t < b + 8:
                _bolt(screen, cx + random.Random(seed + b).randint(-120, 120), 0, cx, bodyTop + 10, seed + b + t)
                flash = pygame.Surface(screen.get_size())
                flash.fill((230, 220, 255))
                flash.set_alpha(120 - (t - b) * 14)
                screen.blit(flash, (0, 0))

    elif kind == 'quake':
        sink = 0 if t < 40 else min(h + 10, (t - 40) * 1.4)
        crack = min(150, t * 3) if t < 180 else max(0, 150 - (t - 180) * 4)
        if crack:
            rng = random.Random(seed)
            pts = [(cx - crack // 2, ground)]
            for i in range(1, 8):
                pts.append((cx - crack // 2 + crack * i // 8, ground + rng.randint(6, 26)))
            pts.append((cx + crack // 2, ground))
            pygame.draw.polygon(screen, (25, 12, 5), pts)
        if sink < h:
            visible = max(0, h - int(sink))
            part = victimSurf.subsurface((0, 0, w, visible))
            screen.blit(part, (left + ((t % 4) - 2 if t < 170 else 0), top + int(sink)))
        if 40 <= t < 170:
            rng = random.Random(seed + t // 3)
            for _ in range(6):
                _glow(screen, cx + rng.randint(-80, 80), ground - rng.randint(0, 30), rng.randint(6, 14), (140, 110, 80), 120)
            if t in range(40, 60):
                _blood(screen, cx, ground - 10, ground, t - 40, seed, 30, 5, 7)

    elif kind == 'shatter':
        if t < 90:
            k = min(4, t // 12)
            img = victimSurf
            if k:
                img = assets.tinted(victimSurf, ('ice', k), (30 * k, 50 * k, 60 * k), pygame.BLEND_RGB_ADD)
            screen.blit(img, (left, top))
            if t > 50:
                rng = random.Random(seed)
                for _ in range(10):
                    sx = left + body.x + rng.randint(0, body.w)
                    sy = top + body.y + rng.randint(0, body.h)
                    pygame.draw.line(screen, (240, 255, 255), (sx - 4, sy), (sx + 4, sy), 1)
                    pygame.draw.line(screen, (240, 255, 255), (sx, sy - 4), (sx, sy + 4), 1)
        else:
            tau = t - 90
            ice = assets.tinted(victimSurf, ('ice', 4), (120, 200, 240), pygame.BLEND_RGB_ADD)
            _drawChunks(screen, ice, left, top, ground, tau, seed, power=1.6, upward=0.6, fade=50)
            if tau < 12:
                _glow(screen, cx, bodyTop + 60, 30 + tau * 5, (220, 250, 255), 200 - tau * 15)
