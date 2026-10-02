"""Teste sem janela (SDL_VIDEODRIVER=dummy): lutas CPU x CPU até a fatality.

Para cada lutador testado, uma luta com ele de cada lado da tela (P1 à
esquerda e P2 à direita). O teste:
  * força os dois especiais dele e confere que o projétil sai da mão (à frente
    do corpo, na altura do braço) e que o lutador olha para o oponente;
  * deixa o oponente com pouca vida para a luta acabar nele e espera a CPU
    fazer a fatality;
  * grava screenshots (luta, especial 1 e 2, fatality, vitória) em <saída>/.

Também confere em todas as tiras que o sprite olha para a direita (a frente do
corpo — braços/mãos — fica à direita da âncora) e grava a tela de seleção.

Uso: SDL_VIDEODRIVER=dummy python3 tools/headless_test.py [saída] [LUTADOR ...]
"""
import os
import sys

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, 'src'))

import pygame  # noqa: E402

pygame.init()
try:
    pygame.mixer.init()
except pygame.error:
    pass
SCREEN = pygame.display.set_mode((800, 500))

import ai  # noqa: E402
import assets  # noqa: E402
import characters  # noqa: E402
import fighter  # noqa: E402
import menu  # noqa: E402
from inputs import SPECIAL, LEFT, RIGHT, DOWN  # noqa: E402
from match import Match  # noqa: E402
from render import Renderer  # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else 'shots'
NAMES = [a.upper().replace('_', ' ') for a in sys.argv[2:]] or [c.name for c in characters.ROSTER]
FAILS = []


def check(ok, msg):
    print(('ok    ' if ok else 'FALHA ') + msg)
    if not ok:
        FAILS.append(msg)


def shot(renderer, snap, name):
    renderer.draw(snap)
    pygame.image.save(SCREEN, os.path.join(OUT, name + '.png'))


def faces_right(char):
    """As tiras olham para a direita: somando os frames ativos de três golpes, o
    braço/perna esticado vai mais longe à frente da âncora do que o corpo vai
    para trás (um golpe sozinho pode enganar: o Jax estica o braço para trás no
    chute, as lâminas do Baraka saem pelas costas). Confere também o desenho
    espelhado (lado direito da tela)."""
    for facing in (1, -1):
        ahead = behind = 0
        for sheetName, frame in (('Bpunch', 8), ('Apunch', 2), ('Bkick', 5)):
            sh = assets.sheet(char, sheetName)
            m = sh.mask(frame, facing)
            ax = sh.anchor(facing)
            w, h = m.get_size()
            fa = fb = 0   # alcance: pixel mais distante à frente / atrás da âncora
            for y in range(0, h, 2):
                for x in range(0, w, 2):
                    if m.get_at((x, y)):
                        d = (x - ax) * facing
                        fa = max(fa, d)
                        fb = max(fb, -d)
            ahead += fa
            behind += fb
        check(ahead > behind + 20, '%s: olha para %s (golpes alcançam %d px à frente, %d atrás)' % (
            char.name, 'a direita' if facing > 0 else 'a esquerda', ahead, behind))


def fight(char, side, opponent, stage):
    tag = '%s_%s' % (char.name.lower().replace(' ', '_'), 'p1' if side == 0 else 'p2')
    chars = [char, opponent] if side == 0 else [opponent, char]
    m = Match(chars[0], chars[1], stage, seed=1234 + side)
    me, opp = m.fighters[side], m.fighters[1 - side]
    cpus = [ai.CPU('HARD', seed=7), ai.CPU('EASY', seed=8)]
    if side == 1:
        cpus.reverse()
    r = Renderer(SCREEN)
    shots = {}
    forced = []          # especiais forçados: (tick em que aperta, qual)
    spec = {}            # o que foi visto de cada especial
    fatalSeen = 0
    for tick in range(60 * 150):
        helds = [cpus[i].think(m, m.fighters[i]) for i in range(2)]
        # força os especiais no 1º round: especial 1 e, depois, especial 2 (trás + SPECIAL)
        if m.phase == 'fight' and m.round == 1:
            if 'sp1' not in spec and me.state in ('idle', 'walk') and not forced:
                forced.append((m.tick, 1))
            if 'sp1' in spec and 'sp2' not in spec and me.state in ('idle', 'walk') and len(forced) == 1 \
                    and me.projectile is None and m.tick > forced[0][0] + 90:
                forced.append((m.tick, 2))
            for t0, which in forced:
                if t0 <= m.tick < t0 + 3:
                    back = LEFT if me.facing > 0 else RIGHT
                    helds[side] = SPECIAL | (back if which == 2 else 0)
                    helds[1 - side] = 0
        m.step(helds)
        snap = m.snapshot()
        # olhar para o oponente quando está parado/andando
        if me.state in ('idle', 'walk') and abs(me.x - opp.x) > 10 and m.phase == 'fight':
            if (opp.x - me.x) * me.facing < 0 and not shots.get('backwards'):
                shots['backwards'] = True
                check(False, '%s: de costas para o oponente no tick %d' % (tag, m.tick))
        # especial 1: projétil saindo da mão
        p = me.projectile
        if p is not None and 'sp1' not in spec and p.t == 1:
            dx = (p.headX() - me.x) * me.facing
            spec['sp1'] = (dx, p.y)
            check(dx > 15, '%s: especial 1 (%s) sai à frente do corpo (%.0f px)' % (tag, p.kind, dx))
            check(40 < p.y < 150, '%s: especial 1 sai na altura das mãos (%.0f px do chão)' % (tag, p.y))
        if p is not None and p.t == 12 and 'sp1shot' not in shots:
            shots['sp1shot'] = True
            shot(r, snap, tag + '_special1')
            continue
        if 'sp1' in spec and 'sp2' not in spec and len(forced) == 2 and m.tick > forced[1][0] + 2:
            if me.state in ('dash', 'slide', 'tele', 'special'):
                spec['sp2'] = me.state
                check(True, '%s: especial 2 (%s) -> estado %s' % (tag, char.special2, me.state))
            elif m.tick > forced[1][0] + 10:
                spec['sp2'] = None
                check(False, '%s: especial 2 (%s) não saiu (estado %s)' % (tag, char.special2, me.state))
        if spec.get('sp2') and 'sp2shot' not in shots and len(forced) == 2 and m.tick == forced[1][0] + 14:
            shots['sp2shot'] = True
            shot(r, snap, tag + '_special2')
            continue
        if m.phase == 'fight' and m.pt == 90 and m.round == 1:
            shot(r, snap, tag + '_fight')
            continue
        # depois dos especiais, o oponente fica com pouca vida (a luta acaba nele)
        if m.phase == 'fight' and ('sp2' in spec or m.round > 1) and m.pt > 30:
            opp.life = min(opp.life, 1.0)
            me.life = max(me.life, 60.0)
        if m.phase == 'fatality':
            fatalSeen += 1
            t = m.fatal['t']
            if t in (25, 80, 130, 175):
                shot(r, snap, '%s_fatality_%03d' % (tag, t))
                continue
        if m.phase == 'over' and m.pt == 120:
            shot(r, snap, tag + '_wins')
            continue
        r.draw(snap)
        if m.finished or (m.phase == 'over' and m.pt > 160):
            break
    check(m.winner is me, '%s: venceu a luta' % tag)
    check(fatalSeen > 0 and m.fatalDone, '%s: fez a fatality (%s)' % (tag, char.fatalityName))


def extras(char, opponent):
    """Especiais 3 e 4 (baixo/frente + SPECIAL): saem e acertam o oponente parado."""
    tag = char.name.lower().replace(' ', '_')
    for i, (kind, label) in enumerate(char.extra):
        which = 3 + i
        m = Match(char, opponent, 1, seed=99 + i)
        me, opp = m.fighters
        while m.phase != 'fight':
            m.step([0, 0])
        far = kind not in fighter.MELEE_SPECIALS and kind not in fighter.DASH_KINDS
        me.x, opp.x = 300, 300 + (260 if far else 70)
        me.facing, opp.facing = 1, -1
        r = Renderer(SCREEN)
        life0 = opp.life
        states = set()
        for t in range(150):
            held = [0, 0]
            if t < 3:
                held[0] = SPECIAL | (DOWN if which == 3 else RIGHT)
            m.step(held)
            states.add(me.state)
            if t == 14:
                shot(r, m.snapshot(), '%s_special%d_%s' % (tag, which, kind))
            opp.life = max(opp.life, 1.0)
        ok = states & {'dash', 'slide', 'tele', 'special', 'attack'}
        check(bool(ok), '%s: especial %d (%s) saiu (%s)' % (tag, which, label, ','.join(sorted(states))))
        if kind != 'teleport':
            check(opp.life < life0, '%s: especial %d (%s) acertou (%.0f de dano)' % (tag, which, label, life0 - opp.life))


class _Game:
    def getDisplay(self):
        return SCREEN


def select_screen():
    scr = menu.CharacterSelect(_Game(), None, {'mode': 'cpu', 'chars': [0, 1]})
    scr.selPos = [None, None]
    n = len(characters.ROSTER)
    for name, cursor, ready in (('select', [n - 3, n - 2], [False, False]),
                                ('select_cpu', [n - 3, n - 1], [True, False])):
        for tick in range(30):
            scr.draw(cursor, ready, tick, 'cpu', 0)
        pygame.image.save(SCREEN, os.path.join(OUT, name + '.png'))


def sounds():
    """Todo som que o jogo toca existe e vai para o build web."""
    import match
    web = open('build_web.sh').read()
    names = {c.voice for c in characters.ROSTER} | set(match.PROJ_SOUND.values()) | \
        {'FinishHim', 'FinishHer', 'Fatality', 'FlawlessVictory', 'Fight'}
    for n in sorted(names):
        check(os.path.exists('res/Sound/%s.ogg' % n) and ' %s ' % n in web.replace('\\\n', ' ').replace(';', ' '),
              'som %s existe e está no build web' % n)


def main():
    os.makedirs(OUT, exist_ok=True)
    sounds()
    for c in characters.ROSTER:
        faces_right(c)
    select_screen()
    byName = {c.name: c for c in characters.ROSTER}
    for i, name in enumerate(NAMES):
        c = byName[name]
        opponent = byName['SUB-ZERO'] if name != 'SUB-ZERO' else byName['SCORPION']
        for side in (0, 1):
            fight(c, side, opponent, stage=1 + (i * 2 + side) % 8)
        extras(c, opponent)
    # página simples para ver os screenshots (publicada junto da prévia do PR)
    imgs = sorted(f for f in os.listdir(OUT) if f.endswith('.png'))
    with open(os.path.join(OUT, 'index.html'), 'w') as fh:
        fh.write('<!doctype html><meta charset="utf-8"><title>pyKombat - screenshots</title>'
                 '<body style="background:#111;color:#eee;font-family:sans-serif">'
                 '<h1>Teste headless (CPU x CPU)</h1><pre>%s</pre>' % ('\n'.join(FAILS) or 'tudo certo'))
        for f in imgs:
            fh.write('<figure style="display:inline-block;margin:6px"><img src="%s" width="400">'
                     '<figcaption>%s</figcaption></figure>' % (f, f[:-4]))
    print()
    print('%d falha(s)' % len(FAILS) if FAILS else 'tudo certo')
    for f in FAILS[:30]:
        print('  -', f)
    sys.exit(1 if FAILS else 0)


if __name__ == '__main__':
    main()
