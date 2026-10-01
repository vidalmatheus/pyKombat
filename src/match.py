# Partida: dois lutadores, projéteis, rounds (melhor de 3), FINISH HIM e
# fatalities. Roda em passo fixo (step() = 1 tick de 1/60 s) e produz um
# snapshot serializável — o que é desenhado na tela (e enviado pela rede no
# modo online) é sempre o snapshot.
import random
import pygame
import assets
import characters
import fighter as F
from fighter import Fighter, MOVES, NEUTRAL
from inputs import LP, HP, LK, HK, FATAL, START

TICKS = 60
ROUND_TIME = 99
FINISH_WINDOW = 6 * TICKS
WINS_NEEDED = 2

# chão (pés) de cada cenário — mesmos ajustes do jogo original (centro + 82)
STAGE_GROUND = {1: 432, 2: 452, 3: 482, 4: 452, 5: 462, 6: 462, 7: 442, 8: 477}

PROJ = {
    'ice':    dict(speed=8.5, dmg=6, effect='freeze', freeze=100, r=13, color=(140, 210, 255), core=(240, 252, 255)),
    'shard':  dict(speed=10.5, dmg=5, effect='freeze', freeze=65, r=10, color=(200, 245, 255), core=(255, 255, 255)),
    'acid':   dict(speed=6.0, dmg=11, effect='heavy', r=12, color=(100, 240, 50), core=(220, 255, 170)),
    'shadow': dict(speed=12.5, dmg=7, effect='mid', r=12, color=(50, 35, 80), core=(150, 130, 210)),
    'soul':   dict(speed=7.5, dmg=9, effect='launch', r=15, color=(60, 230, 90), core=(220, 255, 210)),
    'bolt':   dict(speed=9.5, dmg=9, effect='launch', r=12, color=(170, 110, 255), core=(255, 245, 255)),
    'rock':   dict(speed=7.0, dmg=11, effect='heavy', r=15, color=(150, 112, 74), core=(215, 180, 130)),
    'spear':  dict(speed=17.0, dmg=6, effect='pull', r=6, color=(200, 200, 200), core=(255, 255, 255)),
}
PROJ_SOUND = {'ice': 'IceSound', 'shard': 'IceSound2', 'spear': 'GetOverHere', 'acid': 'HitLongo',
              'shadow': 'HitLongo', 'soul': 'HitLongo', 'bolt': 'IceSound2', 'rock': 'HitLongo'}
PROJ_HEIGHT = 98
SPEAR_RANGE = 440

FATALITY_LEN = {'melt': 230, 'bomb': 200, 'slice': 200, 'slam': 230, 'thunder': 230,
                'quake': 230, 'shatter': 200}
FATAL_GAP = 112      # distância entre os lutadores na fatality original (arpão)


class Projectile:
    def __init__(self, kind, owner, x):
        self.kind = kind
        self.cfg = PROJ[kind]
        self.owner = owner
        self.facing = owner.facing
        self.x = float(x)
        self.y = PROJ_HEIGHT
        self.t = 0
        self.alive = True
        self.length = 0.0        # arpão: comprimento da corda
        self.retract = False
        self.hooked = False

    def headX(self):
        if self.kind == 'spear':
            return self.owner.x + self.facing * (40 + self.length)
        return self.x


_circleMasks = {}


def circleMask(r):
    m = _circleMasks.get(r)
    if m is None:
        s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, 255), (r, r), r)
        m = pygame.mask.from_surface(s)
        _circleMasks[r] = m
    return m


class Match:
    def __init__(self, c1, c2, stage, seed=None, alt2=None):
        self.chars = [c1, c2]
        self.charIdx = [characters.ROSTER.index(c1), characters.ROSTER.index(c2)]
        alt2 = (c1 is c2) if alt2 is None else alt2
        self.alts = [False, alt2]
        self.stage = stage
        self.ground = STAGE_GROUND.get(stage, 450)
        self.seed = seed if seed is not None else random.randrange(1 << 30)
        self.rng = random.Random(self.seed)
        self.mimicSpecials = characters.MIMIC_SPECIALS
        self.fighters = [Fighter(0, c1, False, 250, 1), Fighter(1, c2, alt2, 550, -1)]
        for f in self.fighters:
            assets.preload(f.char, f.alt)
            assets.sheet(f.char, 'spin', f.alt)
        self.projectiles = []
        self.tick = 0
        self.round = 1
        self.wins = [0, 0]
        self.timer = ROUND_TIME * TICKS
        self.phase = 'intro'
        self.pt = 0
        self.hitstop = 0
        self.shake = 0
        self.events = []
        self.winner = None
        self.loser = None
        self.fatal = None
        self.fatalDone = False
        self.finished = False
        self.result = None
        self.flawless = False
        self.roundWinner = None

    # ------------------------------------------------------------ util
    def other(self, f):
        return self.fighters[1 - f.idx]

    def event(self, *ev):
        self.events.append(list(ev))

    def sound(self, name, vol=1.0):
        self.events.append(['snd', name, vol])

    def shakeScreen(self, n):
        self.shake = max(self.shake, n)

    def controlsEnabled(self, f):
        if self.phase == 'fight':
            return True
        if self.phase == 'finish':
            return f is self.winner
        return False

    def frameInfo(self, f):
        sheetName, frame = f.sheetFrame()
        sh = assets.sheet(f.char, sheetName, f.alt)
        ax = f.animDef.get('ax')
        if ax is None:
            ax = sh.anchor(f.facing)
        elif f.facing < 0:
            ax = sh.w - ax
        left = int(f.x - ax)
        top = int(self.ground - f.y - sh.h)
        return sh, frame, left, top

    # ------------------------------------------------------------ passo
    def step(self, helds):
        self.tick += 1
        fs = self.fighters
        presses = []
        for f, held in zip(fs, helds):
            pressed = held & ~f.prevHeld
            f.prevHeld = held
            presses.append(pressed | f.pending)
        if self.shake > 0:
            self.shake -= 1
        if self.hitstop > 0:
            self.hitstop -= 1
            for f, p in zip(fs, presses):
                f.pending = p
            return
        for f in fs:
            f.pending = 0
        self.pt += 1
        self._phasePre(helds, presses)
        if self.phase == 'fatality':
            self._fatalityStep()
        else:
            for f, held, pressed in zip(fs, helds, presses):
                f.update(held, pressed, self)
            self._projectiles()
            self._melee()
            self._pushboxes()
        for f in fs:
            if f.state in NEUTRAL and self.phase in ('intro', 'fight', 'finish'):
                f.faceTowards(self.other(f))
        self._phasePost(presses)

    # ------------------------------------------------------------ fases
    def _phasePre(self, helds, presses):
        if self.phase == 'intro':
            if self.pt == 1:
                self.event('banner', 'round', self.round)
            if self.pt == 70:
                self.sound('Fight')
                self.event('banner', 'fight', 0)
            if self.pt >= 110:
                self.phase = 'fight'
                self.pt = 0
        elif self.phase == 'fight':
            self.timer -= 1
            if self.timer <= 0:
                self.timer = 0
                a, b = self.fighters
                if abs(a.life - b.life) < 0.5:
                    self._draw()
                else:
                    self._ko(a if a.life < b.life else b, timeUp=True)
        elif self.phase == 'finish':
            w, l = self.winner, self.loser
            if presses[w.idx] & FATAL or (presses[w.idx] & HP and w.motion(self.tick, ['d', 'df', 'f'])):
                if w.state in NEUTRAL and l.state == 'dizzy' and w.y <= 0:
                    self._startFatality()
                    return
            if self.pt > FINISH_WINDOW and l.state == 'dizzy':
                # ninguém finalizou: o perdedor cai
                l.knockdown(1 if l.x > w.x else -1, launch=True, dead=True)
                self._over(fatality=False)

    def _phasePost(self, presses):
        if self.phase == 'ko':
            w = self.roundWinner
            if self.pt == 80 and w is not None:
                self._winPose(w)
                self.event('banner', 'wins', w.idx)
                self.sound(w.char.voice)
            if self.pt == 150 and w is not None and self.flawless:
                self.sound('FlawlessVictory')
            if self.pt >= 230:
                self._nextRound()
        elif self.phase == 'over':
            w = self.winner
            if w.state in NEUTRAL and not self.fatalDone and self.pt > 50:
                self._winPose(w)
            if self.pt == 60 and not self.fatalDone:
                self.event('banner', 'wins', w.idx)
                self.sound(w.char.voice)
            if self.fatalDone and self.pt == 70:
                self.sound('Fatality')
            if self.pt == 140 and self.flawless and not self.fatalDone:
                self.sound('FlawlessVictory')
            if self.pt > 150:
                self.result = w.idx
                if self.pt > 200 and any(p & (LP | HP | LK | HK | START) for p in presses):
                    self.finished = True
                if self.pt > 900:
                    self.finished = True
        elif self.phase == 'finish':
            l = self.loser
            if l.state == 'idle':  # perdedor livre -> tonto
                l.setState('dizzy', 'dizzy')

    def _winPose(self, w):
        if w.state in NEUTRAL or w.state == 'attack':
            w.move = None
            w.setState('win', 'win')

    def _ko(self, loser, timeUp=False):
        w = self.other(loser)
        loser.life = max(0.0, loser.life)
        self.wins[w.idx] += 1
        self.roundWinner = w
        self.flawless = w.life >= 100
        self.projectiles = []
        for f in self.fighters:
            f.projectile = None
        if self.wins[w.idx] >= WINS_NEEDED:
            self.phase = 'finish'
            self.pt = 0
            self.winner, self.loser = w, loser
            loser.doomed = True
            if loser.state in NEUTRAL or loser.state in ('attack', 'special', 'slide', 'tele', 'frozen', 'stunned'):
                loser.invisible = False
                loser.setState('dizzy', 'dizzy')
            self.event('music', 'stop')
            self.sound('FinishHim')
            self.event('banner', 'finish', loser.idx)
        else:
            self.phase = 'ko'
            self.pt = 0
            loser.invisible = False
            if loser.state not in ('fall', 'lying', 'sweepfall'):
                loser.knockdown(1 if loser.x > w.x else -1, launch=True, dead=True)
            else:
                loser.dead = True
            if timeUp:
                self.event('banner', 'time', 0)

    def _draw(self):
        self.phase = 'ko'
        self.pt = 0
        self.roundWinner = None
        self.event('banner', 'draw', 0)

    def _nextRound(self):
        if self.roundWinner is not None:
            self.round += 1
        for f, x, facing in zip(self.fighters, (250, 550), (1, -1)):
            keep = f.prevHeld
            f.reset(x, facing)
            f.prevHeld = keep
        self.projectiles = []
        self.timer = ROUND_TIME * TICKS
        self.phase = 'intro'
        self.pt = 0

    def _over(self, fatality):
        self.phase = 'over'
        self.pt = 0
        self.fatalDone = fatality

    # ------------------------------------------------------------ fatality
    def _startFatality(self):
        w, l = self.winner, self.loser
        kind = w.char.fatality
        if kind == 'random':
            kind = self.rng.choice(characters.PROCEDURAL_FATALITIES)
        d = 1 if l.x > w.x else -1
        # reposiciona para o efeito caber na tela (e o arpão alcançar a vítima)
        gap = FATAL_GAP if kind == 'anim' else max(110, min(190, abs(l.x - w.x)))
        mid = max(130 + gap / 2, min(670 - gap / 2, (w.x + l.x) / 2))
        w.x = mid - d * gap / 2
        l.x = mid + d * gap / 2
        w.facing, l.facing = d, -d
        w.move = None
        w.setState('fatal', 'fatal' if kind == 'anim' else 'cast')
        l.setState('fatal_victim', 'dizzy')
        sheetName, frame = l.sheetFrame()
        self.fatal = {'kind': kind, 't': 0, 'seed': self.rng.randrange(1 << 20),
                      'vs': sheetName, 'vf': frame, 'vfacing': l.facing, 'vx': int(l.x)}
        self.phase = 'fatality'
        self.pt = 0
        self.projectiles = []
        self.event('fatal', kind)
        self.sound({'anim': 'GetOverHere' if w.char.special == 'spear' else 'IceSound',
                    'melt': 'HitLongo', 'bomb': 'BeforeFinish', 'slice': 'HitLongo', 'slam': 'HitLongo',
                    'thunder': 'IceSound2', 'quake': 'HitLongo', 'shatter': 'IceSound'}[kind])

    def _fatalityStep(self):
        fz = self.fatal
        fz['t'] += 1
        t = fz['t']
        w, l = self.winner, self.loser
        w.t += 1
        w.stepAnim()
        if fz['kind'] == 'anim':
            if l.animName != 'victim_split':
                l.stepAnim()
                if w.ai >= F.FATAL_SPLIT_FRAME[w.base]:
                    l.setAnim('victim_split')
                    self.sound('HitFatality')
                    self.event('blood', int(l.x), int(self.ground - 90), -l.facing, 40, t)
                    self.shakeScreen(10)
            else:
                l.stepAnim()
                if l.ai in (3, 5) and l.at == 0:
                    self.event('blood', int(l.x), int(self.ground - 60), 0, 25, t + l.ai)
                if l.ai == len(l.animDef['seq']) - 1 and w.ai == len(w.animDef['seq']) - 1:
                    fz.setdefault('endAt', t + 45)
                if t >= fz.get('endAt', 1 << 30):
                    self._endFatality()
        else:
            hits = {'melt': (40,), 'bomb': (70,), 'slice': (40,), 'slam': (70, 120, 165),
                    'thunder': (40, 70, 100), 'quake': (30,), 'shatter': (90,)}[fz['kind']]
            if t in hits:
                self.sound('HitFatality')
                self.shakeScreen(12 if fz['kind'] != 'quake' else 120)
            if t >= FATALITY_LEN[fz['kind']]:
                self._endFatality()

    def _endFatality(self):
        w = self.winner
        self._over(fatality=True)
        self.loser.dead = True
        self.event('banner', 'wins', w.idx)
        self.event('banner', 'fatality', w.idx)
        self.sound(w.char.voice)

    # ------------------------------------------------------------ projéteis
    def spawnProjectile(self, f, kind):
        p = Projectile(kind, f, f.x + f.facing * 62)
        f.projectile = p
        self.projectiles.append(p)
        self.sound(PROJ_SOUND.get(kind, 'HitLongo'))

    def _projectiles(self):
        for p in list(self.projectiles):
            p.t += 1
            owner = p.owner
            target = self.other(owner)
            if p.kind == 'spear':
                if owner.state not in ('special',) and not p.hooked:
                    p.retract = True
                if p.retract:
                    p.length -= 26
                    if p.length <= 0:
                        p.alive = False
                else:
                    p.length += p.cfg['speed']
                    if p.length >= SPEAR_RANGE:
                        p.retract = True
            else:
                p.x += p.facing * p.cfg['speed']
                if p.x < -40 or p.x > 840:
                    p.alive = False
            if p.alive and not p.retract and not p.hooked:
                if self._projectileHits(p, target):
                    if p.kind == 'spear':
                        p.retract = True
                    else:
                        p.alive = False
            if not p.alive:
                self.projectiles.remove(p)
                if owner.projectile is p:
                    owner.projectile = None
        # projétil contra projétil
        if len(self.projectiles) == 2:
            a, b = self.projectiles
            if a.owner is not b.owner and abs(a.headX() - b.headX()) < a.cfg['r'] + b.cfg['r'] + 6:
                for p in (a, b):
                    if p.kind == 'spear':
                        p.retract = True
                    else:
                        p.alive = False
                        self.projectiles.remove(p)
                        p.owner.projectile = None
                self.event('spark', int(a.headX()), int(self.ground - PROJ_HEIGHT), 1)
                self.sound('block')

    def _projectileHits(self, p, d):
        if d.invuln or d.invisible or d.dead or d.state in ('lying', 'getup', 'getup_dizzy', 'fatal_victim'):
            return False
        sh, frame, left, top = self.frameInfo(d)
        r = p.cfg['r']
        hx = int(p.headX())
        hy = int(self.ground - p.y)
        cm = circleMask(r)
        hit = sh.mask(frame, d.facing).overlap(cm, (hx - r - left, hy - r - top))
        if not hit:
            return False
        cfg = p.cfg
        a = p.owner
        effect = cfg['effect']
        if self.phase == 'finish':
            if d is self.loser:
                d.knockdown(1 if d.x > a.x else -1, launch=True, dead=True)
                self.event('blood', hx, hy, p.facing, 30, self.tick)
                self.sound('Hit0')
                self._over(fatality=False)
            return True
        if d.state == 'frozen' and effect == 'freeze':
            # congelar quem já está congelado: o gelo volta contra o atirador (MK!)
            self._freeze(a, cfg['freeze'])
            self.event('spark', hx, hy, 2)
            return True
        react = {'freeze': 'mid', 'pull': 'mid', 'heavy': 'heavy', 'mid': 'mid', 'launch': 'launch'}[effect]
        landed = self._applyHit(a, d, cfg['dmg'], 'mid', react, 18, 5.0, (hx, hy), special=True,
                                dirX=p.facing)
        if landed and d.life > 0 and self.phase == 'fight':
            if effect == 'freeze':
                self._freeze(d, cfg['freeze'])
            elif effect == 'pull':
                d.setState('pulled', 'pulled')
                d.puller = a
                d.push = 0
                p.hooked = True
                p.retract = True
                self.sound('ComeHere')
        return True

    def _freeze(self, f, ticks):
        f.frozenFrame = f.sheetFrame()
        f.move = None
        f.state = 'frozen'
        f.t = 0
        f.stun = ticks
        f.y = 0
        self.sound('IceSound2')

    # ------------------------------------------------------------ corpo a corpo
    def _melee(self):
        results = []
        for a in self.fighters:
            d = self.other(a)
            if a.state not in ('attack', 'slide') or a.hitDone or a.move is None:
                continue
            mv = MOVES[a.move]
            lo, hi = mv['active']
            if mv.get('air'):
                active = a.ai >= lo
            elif a.state == 'slide':
                active = a.t < 22
            else:
                active = lo <= a.ai <= hi
            if not active:
                continue
            if d.invuln or d.invisible or d.state in ('lying', 'getup', 'getup_dizzy', 'fatal_victim') or (d.dead and d.state != 'dizzy'):
                continue
            sh, frame, left, top = self.frameInfo(a)
            dsh, dframe, dleft, dtop = self.frameInfo(d)
            hm = sh.hitMask(frame, a.facing)
            pt = hm.overlap(dsh.mask(dframe, d.facing), (dleft - left, dtop - top))
            if pt:
                results.append((a, d, mv, (left + pt[0], top + pt[1])))
        for a, d, mv, point in results:
            a.hitDone = True
            if self.phase == 'finish':
                if d is self.loser:
                    d.knockdown(1 if d.x > a.x else -1, launch=True, dead=True)
                    self.event('blood', point[0], point[1], a.facing, 40, self.tick)
                    self.sound('Hit0')
                    self.hitstop = 8
                    self._over(fatality=False)
                continue
            self._applyHit(a, d, mv['dmg'], mv['level'], mv['react'], mv['stun'], mv['push'], point,
                           special=mv.get('special', False))
            if a.move == 'upper' and self.rng.random() < 0.12:
                self.event('toasty', 0)
                self.sound('Toasty')

    def _applyHit(self, a, d, dmg, level, react, stun, push, point, special=False, dirX=None):
        """Aplica um golpe; devolve True se acertou (False se foi defendido)."""
        if dirX is None:
            dirX = 1 if d.x > a.x else -1 if d.x < a.x else a.facing
        blocking = d.state in ('block', 'cblock') or d.state == 'blockstun'
        facingAttacker = d.facing == -dirX
        if blocking and facingAttacker and d.y <= 0:
            bs = d.blockState if d.state == 'blockstun' else d.state
            if bs == 'cblock' or level != 'low':
                d.blockState = bs
                d.state = 'blockstun'
                d.t = 0
                d.stun = 10 + (5 if special else 0)
                d.push = dirX * 4.5
                if special:
                    d.life -= 1
                self._cornerPush(a, d, dirX, 3.0)
                self.event('spark', point[0], point[1], 0)
                self.sound('block')
                self.hitstop = 3
                self._checkKO(d)
                return False
        d.combo += 1
        scale = max(0.5, 1.0 - 0.12 * (d.combo - 1))
        dmg = dmg * scale
        if d.state == 'frozen':
            d.frozenFrame = None
        d.life -= dmg
        d.flash = 5
        d.move = None
        d.invisible = False
        self.event('blood', point[0], point[1], dirX, int(6 + dmg * 2.2), self.tick)
        self.sound('Hit0')
        if self.rng.random() < 0.45:
            self.sound('Hit%d' % self.rng.randint(1, 12))
        self.hitstop = 4 + int(dmg // 3)
        if dmg >= 9:
            self.shakeScreen(6)
        if d.y > 0 or react == 'launch':
            d.knockdown(dirX, launch=True)
            if react == 'launch':
                d.vy = 11.0
        elif react == 'sweep':
            d.knockdown(dirX, launch=False)
        else:
            if d.crouching():
                name = 'hit_crouch'
            else:
                name = {'hi': 'hit_hi', 'mid': 'hit_mid', 'heavy': 'hit_heavy'}.get(react, 'hit_mid')
            d.setState('hitstun', name)
            d.stun = stun
            d.push = dirX * push
        self._cornerPush(a, d, dirX, push * 0.8)
        self._checkKO(d)
        return True

    def _cornerPush(self, a, d, dirX, amount):
        if (dirX > 0 and d.x >= F.STAGE_MAX - 2) or (dirX < 0 and d.x <= F.STAGE_MIN + 2):
            if a.y <= 0:
                a.push = -dirX * amount

    def _checkKO(self, d):
        if d.life <= 0 and self.phase == 'fight':
            d.life = 0
            self._ko(d)

    # ------------------------------------------------------------ empurrão
    def _pushboxes(self):
        a, b = self.fighters
        if a.invisible or b.invisible:
            return
        if abs(a.y - b.y) > 80:
            return  # um passa por cima do outro (pulo cruzado)
        dx = b.x - a.x
        minD = 2 * F.BODY_HALF
        overlap = minD - abs(dx)
        if overlap <= 0:
            return
        s = 1 if dx > 0 else -1 if dx < 0 else (1 if a.facing > 0 else -1)
        a.x -= s * overlap / 2
        b.x += s * overlap / 2
        for f, o, sign in ((a, b, -s), (b, a, s)):
            if f.x < F.STAGE_MIN or f.x > F.STAGE_MAX:
                f.x = max(F.STAGE_MIN, min(F.STAGE_MAX, f.x))
                o.x = f.x - sign * minD

    # ------------------------------------------------------------ snapshot
    def snapshot(self):
        fs = []
        for f in self.fighters:
            if f.state == 'frozen' and f.frozenFrame:
                sheetName, frame = f.frozenFrame
            else:
                sheetName, frame = f.sheetFrame()
            flags = 0
            if f.state == 'frozen':
                flags |= 1
            if f.invisible or (f.state == 'fatal_victim' and self.fatal and self.fatal['kind'] != 'anim'):
                flags |= 2
            if f.flash > 0:
                flags |= 4
            if f.state == 'tele' and f.t < 6:
                flags |= 8
            ax = f.animDef.get('ax') or 0
            fs.append([self.charIdx[f.idx], 1 if f.alt else 0, sheetName, frame, int(round(f.x)),
                       int(round(f.y)), f.facing, flags, ax, round(max(0.0, f.life), 1)])
        ps = []
        for p in self.projectiles:
            ps.append([p.kind, int(p.headX()), int(p.y), p.facing, p.t, p.owner.idx, int(p.length)])
        fz = 0
        if self.fatal is not None and self.phase in ('fatality', 'over') and self.fatal['kind'] != 'anim':
            z = self.fatal
            fz = [z['kind'], z['t'], self.winner.idx, self.loser.idx, z['seed'], z['vs'], z['vf'],
                  z['vfacing'], z['vx']]
        snap = {
            't': self.tick, 'ph': self.phase, 'pt': self.pt, 'r': self.round,
            'tm': (self.timer + TICKS - 1) // TICKS, 'w': list(self.wins), 'st': self.stage,
            'g': self.ground, 'f': fs, 'p': ps, 'fx': fz, 'sh': self.shake, 'ev': self.events,
            'res': self.result if self.result is not None else -1, 'fin': 1 if self.finished else 0,
            'rw': self.roundWinner.idx if self.roundWinner is not None else -1,
            'mw': self.winner.idx if self.winner is not None else -1,
            'fd': 1 if self.fatalDone else 0, 'fl': 1 if self.flawless else 0,
            'fn': self.fatal['kind'] if self.fatal else '',
        }
        self.events = []
        return snap
