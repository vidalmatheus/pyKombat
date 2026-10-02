# Helpers de interface: texto com a fonte do MK2, caixas, dicas de tecla.
import pygame
import assets

RED = (196, 30, 30)
WHITE = (232, 232, 232)
GOLD = (255, 200, 60)
GRAY = (150, 150, 150)
DARK = (12, 8, 8)


def text(surf, msg, size, pos, color=WHITE, center=True, shadow=True, alpha=None, outline=False):
    f = assets.font(size)
    img = f.render(msg, True, color)
    x, y = pos
    if center:
        x -= img.get_width() // 2
    if outline:
        o = f.render(msg, True, (0, 0, 0))
        for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, 2), (-2, 2), (2, -2)):
            surf.blit(o, (x + dx, y + dy))
    elif shadow:
        sh = f.render(msg, True, (0, 0, 0))
        surf.blit(sh, (x + 2, y + 2))
    if alpha is not None:
        img.set_alpha(alpha)
    surf.blit(img, (x, y))
    return img.get_width()


def textWidth(msg, size):
    return assets.font(size).size(msg)[0]


def panel(surf, rect, alpha=170, border=RED):
    s = pygame.Surface(rect.size, pygame.SRCALPHA)
    s.fill((0, 0, 0, alpha))
    surf.blit(s, rect.topleft)
    if border:
        pygame.draw.rect(surf, border, rect, 2)


def dim(surf, alpha=150):
    s = pygame.Surface(surf.get_size())
    s.fill((0, 0, 0))
    s.set_alpha(alpha)
    surf.blit(s, (0, 0))


def backHint(surf, label='ESC / BACKSPACE: BACK'):
    text(surf, label, 14, (400, 478), GRAY)


def tapItem(taps, ys, size, x0=140, x1=660):
    """Índice do item de menu (texto no topo y, altura `size`) tocado/clicado, ou None."""
    for x, y in taps:
        if x0 <= x <= x1:
            for i, top in enumerate(ys):
                if top - 10 <= y <= top + size + 10:
                    return i
    return None
