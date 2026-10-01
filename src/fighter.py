# Lutador: máquina de estados por frame (60 ticks/s, passo fixo).
#
# Tudo aqui é lógico (posição, estado, animação atual); o desenho fica em
# render.py a partir do snapshot. Isso deixa a simulação idêntica no jogo
# local, contra a CPU e online (o host simula e manda o snapshot ao convidado).
from inputs import UP, DOWN, LEFT, RIGHT, LP, HP, LK, HK, BLOCK, SPECIAL

GRAVITY = 0.62
JUMP_VY = 13.5
JUMP_VX = 4.4
WALK_F = 3.4
WALK_B = 2.8
BODY_HALF = 26          # meia largura da "caixa de empurrão"
STAGE_MIN = 40
STAGE_MAX = 760
HOLD = 9999             # duração "infinita" (segura o último frame)


def A(sheet, seq, dur, loop=False, ax=None):
    seq = list(seq)
    if not isinstance(dur, (list, tuple)):
        dur = [dur] * len(seq)
    return {'sheet': sheet, 'seq': seq, 'dur': list(dur), 'loop': loop, 'ax': ax}


COMMON_ANIMS = {
    'idle': A('dance', [0, 1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1], 5, True),
    'walk': A('walk', range(9), 4, True),
    'walkb': A('walk', range(8, -1, -1), 4, True),
    'crouch': A('crouch', [0, 1, 2], [2, 2, HOLD]),
    'stand': A('crouch', [1, 0], 2),
    'prejump': A('jump', [0], 3),
    'jump': A('jump', [1], HOLD),
    'flip': A('spin', range(1, 8), HOLD),
    'land': A('jump', [0], 4),
    'lp': A('Apunch', [0, 1, 2, 2, 1, 0], [2, 2, 5, 2, 2, 2]),
    'hp': A('Bpunch', [6, 7, 8, 8, 7, 6], [3, 3, 5, 3, 3, 3]),
    'lk': A('Akick', [1, 2, 3, 4, 5, 6, 6, 5, 3, 1], [2, 2, 2, 2, 2, 5, 3, 2, 2, 2]),
    'hk': A('Bkick', range(9), [2, 2, 2, 3, 3, 6, 3, 3, 3]),
    'clp': A('Cpunch', [0, 1, 2, 2, 1, 0], [2, 2, 5, 2, 2, 2]),
    'clk': A('Ckick', [2, 3, 4, 5, 6, 6, 5, 4, 3], [2, 2, 2, 2, 5, 2, 2, 2, 2]),
    'upper': A('Dpunch', [0, 1, 2, 3, 4, 4], [3, 3, 3, 5, 6, 6]),
    'sweep': A('Dkick', [0, 1, 2, 3, 3, 4, 5], [2, 2, 2, 6, 3, 3, 4]),
    'jk': A('Ekick', [0, 1, 2], [3, 3, HOLD]),
    'jp': A('Epunch', [0, 1, 2], [3, 3, HOLD]),
    'hit_hi': A('Ahit', [0, 1, 2, 1, 0], [2, 3, 6, 3, 2]),
    'hit_mid': A('Bhit', [0, 1, 2, 1, 0], [2, 3, 6, 3, 2]),
    'hit_heavy': A('Chit', range(6), [3, 3, 4, 4, 4, 4]),
    'hit_crouch': A('Ehit', [0, 1, 2, 1, 0], [2, 3, 5, 3, 2]),
    'fall': A('Fhit', range(7), [3, 4, 4, 4, 4, 4, HOLD]),
    'getup': A('Fhit', range(7, 14), 4),
    'sweepfall': A('Ghit', range(6), [3, 4, 4, 4, 4, HOLD]),
    'sweepup': A('Ghit', range(6, 11), 4),
    'block': A('Ablock', [0, 1, 2], [2, 2, HOLD]),
    'cblock': A('Bblock', [0, 1, 2], [2, 2, HOLD]),
    'dizzy': A('dizzy', [0, 1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1], 7, True),
    'slide': A('Dkick', [2, 3], [3, HOLD]),
    'tele_punch': A('Bpunch', [7, 8, 8, 7, 6], [3, 6, 4, 3, 3]),
    'victim_split': A('fatalityhit', range(10), [6] * 9 + [HOLD]),
}
BASE_ANIMS = {
    'Sub-Zero': {
        # rajada com as duas mãos: o projétil sai no índice 3
        'special': A('Special', [0, 1, 2, 3, 4, 5, 6, 7, 2, 1, 0], [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]),
        'pulled': A('hitSpecial', [0, 1, 2, 1], 5, True),
        'win': A('win', [0, 1, 2], [8, 8, HOLD]),
        'cast': A('Special', [0, 1, 2, 3, 4], [4, 4, 4, 4, HOLD]),
        'fatal': A('fatality', range(17), [6] * 16 + [HOLD]),
    },
    'Scorpion': {
        # arremesso: projétil no índice 3; segura o frame 3 enquanto o arpão voa
        'special': A('Special', [0, 1, 2, 3, 4, 5, 6], [3, 3, 3, 6, 3, 3, 3]),
        'pulled': A('Chit', [0, 1, 2, 1], 5, True),
        'win': A('fatality', [16, 17, 18, 19], [7, 7, 7, HOLD], ax=100),
        'cast': A('Special', [0, 1, 2, 3], [4, 4, 4, HOLD]),
        'fatal': A('fatality', range(20), [6] * 19 + [HOLD]),
    },
}
SPECIAL_SPAWN = 3                  # índice da sequência em que o projétil sai
FATAL_SPLIT_FRAME = {'Sub-Zero': 13, 'Scorpion': 13}  # quando a vítima se parte

# golpes normais: anim, dano, altura (high/mid/low), reação, janela ativa (índices da seq)
MOVES = {
    'lp': dict(dmg=4, level='high', react='hi', active=(2, 3), stun=14, push=1.2),
    'hp': dict(dmg=7, level='high', react='mid', active=(2, 3), stun=17, push=5.0),
    'lk': dict(dmg=6, level='high', react='mid', active=(5, 6), stun=16, push=5.0),
    'hk': dict(dmg=9, level='high', react='heavy', active=(5, 6), stun=22, push=6.5),
    'clp': dict(dmg=3, level='mid', react='hi', active=(2, 3), stun=12, push=1.5),
    'clk': dict(dmg=4, level='low', react='hi', active=(4, 5), stun=13, push=3.0),
    'upper': dict(dmg=13, level='mid', react='launch', active=(3, 4), stun=0, push=4.0),
    'sweep': dict(dmg=8, level='low', react='sweep', active=(3, 4), stun=0, push=2.0),
    'jk': dict(dmg=9, level='high', react='heavy', active=(2, 2), stun=20, push=5.0, air=True),
    'jp': dict(dmg=7, level='high', react='mid', active=(2, 2), stun=17, push=4.0, air=True),
    'slide': dict(dmg=9, level='low', react='sweep', active=(1, 1), stun=0, push=3.0, special=True),
    'tele_punch': dict(dmg=10, level='high', react='launch', active=(1, 2), stun=0, push=4.0, special=True),
}
CROUCH_MOVES = {'clp', 'clk', 'upper', 'sweep'}

NEUTRAL = ('idle', 'walk', 'crouch', 'block', 'cblock', 'land', 'stand')


def anim(base, name):
    a = BASE_ANIMS[base].get(name)
    return a if a is not None else COMMON_ANIMS[name]


class Fighter:
    def __init__(self, idx, char, alt, x, facing):
        self.idx = idx
        self.char = char
        self.base = char.base
        self.alt = alt
        self.reset(x, facing)

    def reset(self, x, facing):
        self.x = float(x)
        self.y = 0.0             # altura acima do chão
        self.vx = 0.0
        self.vy = 0.0
        self.push = 0.0          # empurrão (recuo de golpe), decai
        self.facing = facing
        self.life = 100.0
        self.state = 'idle'
        self.t = 0
        self.move = None
        self.hitDone = False
        self.airAttack = False
        self.flip = False
        self.stun = 0
        self.combo = 0
        self.flash = 0
        self.invisible = False
        self.invuln = False
        self.doomed = False      # perdeu a luta: ficará tonto (FINISH HIM)
        self.dead = False
        self.prevHeld = 0
        self.pending = 0         # botões apertados durante o hitstop
        self.buf = []            # histórico de direções (tick, token)
        self.lastToken = 'n'
        self.projectile = None
        self.puller = None
        self.specialKind = None
        self.tele = 0
        self.frozenFrame = None
        self.spawned = False
        self.lastFall = 'fall'
        self.jumpDir = 0
        self.blockState = 'block'
        self.setAnim('idle')

    # ------------------------------------------------------------ animação
    def setAnim(self, name, restart=True):
        if not restart and getattr(self, 'animName', None) == name:
            return
        self.animName = name
        self.animDef = anim(self.base, name)
        self.ai = 0
        self.at = 0
        self.animDone = False

    def stepAnim(self):
        a = self.animDef
        self.at += 1
        if self.at >= a['dur'][self.ai]:
            self.at = 0
            if self.ai + 1 < len(a['seq']):
                self.ai += 1
            elif a['loop']:
                self.ai = 0
            else:
                self.animDone = True
                self.at = a['dur'][self.ai]

    def sheetFrame(self):
        a = self.animDef
        if self.animName == 'flip':  # cambalhota: frame pela fase do pulo
            prog = max(0.0, min(0.999, self.t / (2 * JUMP_VY / GRAVITY)))
            return a['sheet'], 1 + int(prog * 7)
        if self.animName == 'jump':  # sobe/desce esticado; encolhido no alto
            return a['sheet'], 2 if abs(self.vy) < 3.2 else 1
        return a['sheet'], a['seq'][self.ai]

    def setState(self, state, animName=None):
        self.state = state
        self.t = 0
        if animName is not None:
            self.setAnim(animName)

    # ------------------------------------------------------------ helpers
    def grounded(self):
        return self.y <= 0 and self.state not in ('jump', 'prejump', 'fall', 'tele')

    def crouching(self):
        return self.state in ('crouch', 'cblock') or (self.state == 'attack' and self.move in CROUCH_MOVES) \
            or (self.state == 'hitstun' and self.animName == 'hit_crouch')

    def canAct(self):
        return self.state in NEUTRAL

    def faceTowards(self, other):
        dx = other.x - self.x
        if abs(dx) > 4:
            self.facing = 1 if dx > 0 else -1

    def _token(self, held):
        fwd = RIGHT if self.facing > 0 else LEFT
        back = LEFT if self.facing > 0 else RIGHT
        t = ''
        if held & UP:
            t += 'u'
        if held & DOWN:
            t += 'd'
        if held & fwd:
            t += 'f'
        elif held & back:
            t += 'b'
        return t or 'n'

    def motion(self, tick, seq, window=20):
        """True se a sequência de direções (ex. ['d','df','f']) aconteceu há pouco."""
        recent = [tok for (tk, tok) in self.buf if tick - tk <= window]
        i = 0
        for tok in recent:
            if tok == seq[i]:
                i += 1
                if i == len(seq):
                    return True
        return False

    def holdingBack(self, held):
        return bool(held & (LEFT if self.facing > 0 else RIGHT))

    def holdingFwd(self, held):
        return bool(held & (RIGHT if self.facing > 0 else LEFT))

    # ------------------------------------------------------------ comandos
    def update(self, held, pressed, match):
        tick = match.tick
        tok = self._token(held)
        if tok != self.lastToken:
            self.lastToken = tok
            self.buf.append((tick, tok))
            if len(self.buf) > 16:
                self.buf.pop(0)
        self.t += 1
        if self.flash > 0:
            self.flash -= 1
        controllable = match.controlsEnabled(self)

        if self.state in NEUTRAL and controllable:
            self._neutral(held, pressed, match)
        elif self.state in NEUTRAL:
            if self.state not in ('idle', 'crouch'):
                self.setState('idle', 'idle')
        self._advance(held, pressed, match)
        self.stepAnim()
        self._physics(match)

    def _neutral(self, held, pressed, match):
        tick = match.tick
        # 1) especiais (botão dedicado ou meia-lua + botão)
        if self.projectile is None and self.state != 'land':
            sp = None
            if pressed & SPECIAL:
                sp = 2 if self.holdingBack(held) else 1
            elif pressed & LP and self.motion(tick, ['d', 'df', 'f']):
                sp = 1
            elif pressed & LK and self.motion(tick, ['d', 'db', 'b']):
                sp = 2
            if sp is not None:
                self.startSpecial(sp, match)
                return
        # 2) pulo
        if held & UP and self.state != 'land':
            self.jumpDir = (1 if held & RIGHT else -1 if held & LEFT else 0)
            self.setState('prejump', 'prejump')
            return
        # 3) agachado
        if held & DOWN:
            if pressed & LP:
                return self.startAttack('clp')
            if pressed & HP:
                return self.startAttack('upper')
            if pressed & LK:
                return self.startAttack('clk')
            if pressed & HK:
                return self.startAttack('sweep')
            if held & BLOCK:
                if self.state != 'cblock':
                    self.setState('cblock', 'cblock')
                return
            if self.state != 'crouch':
                self.setState('crouch', 'crouch')
            return
        if self.state in ('crouch', 'cblock'):
            self.setState('stand', 'stand')
            return
        # 4) defesa em pé
        if held & BLOCK:
            if self.state != 'block':
                self.setState('block', 'block')
            return
        # 5) golpes
        for bit, mv in ((LP, 'lp'), (HP, 'hp'), (LK, 'lk'), (HK, 'hk')):
            if pressed & bit:
                return self.startAttack(mv)
        if self.state == 'stand' and not self.animDone:
            return
        # 6) andar (de costas a animação roda ao contrário)
        if held & (LEFT | RIGHT):
            name = 'walk' if self.holdingFwd(held) else 'walkb'
            if self.state != 'walk':
                self.setState('walk', name)
            else:
                self.setAnim(name, restart=False)
            return
        if self.state != 'idle' and (self.state != 'land' or self.animDone):
            self.setState('idle', 'idle')

    def startAttack(self, mv):
        self.move = mv
        self.hitDone = False
        self.setState('attack', mv)

    def startSpecial(self, which, match):
        kind = self.char.special if which == 1 else self.char.special2
        if kind == 'slide':
            self.move = 'slide'
            self.hitDone = False
            self.setState('slide', 'slide')
            match.sound('block', 0.5)
        elif kind == 'teleport':
            self.setState('tele', 'stand')
            self.invuln = True
            match.event('tele', int(self.x), int(self.y), self.idx)
        else:
            if kind == 'mimic':
                kind = match.rng.choice(match.mimicSpecials)
            self.specialKind = kind
            self.spawned = False
            self.setState('special', 'special')

    # ------------------------------------------------------------ estados
    def _advance(self, held, pressed, match):
        st = self.state
        if st == 'attack':
            mv = MOVES[self.move]
            if mv.get('air'):
                return  # golpe aéreo é tratado em _physics (fica até aterrissar)
            # cancelamento: golpe que acertou pode emendar em outro (combo)
            if self.hitDone and self.ai > mv['active'][1] and pressed & (LP | HP | LK | HK):
                down = held & DOWN
                for bit, a, c in ((LP, 'lp', 'clp'), (HP, 'hp', 'upper'), (LK, 'lk', 'clk'), (HK, 'hk', 'sweep')):
                    if pressed & bit:
                        return self.startAttack(c if down else a)
            if self.animDone:
                wasCrouch = self.move in CROUCH_MOVES
                self.move = None
                if held & DOWN:
                    self.setState('crouch', 'crouch')
                    self.ai = 2
                elif wasCrouch:
                    self.setState('stand', 'stand')
                else:
                    self.setState('idle', 'idle')
        elif st == 'prejump':
            if self.t >= 3:
                self.vy = JUMP_VY
                self.vx = self.jumpDir * JUMP_VX
                self.flip = self.jumpDir != 0
                self.airAttack = False
                self.setState('jump', 'flip' if self.flip else 'jump')
                self.move = None
        elif st == 'jump':
            if not self.airAttack and pressed & (LP | HP | LK | HK):
                self.airAttack = True
                self.move = 'jk' if pressed & (LK | HK) else 'jp'
                self.hitDone = False
                self.setAnim(self.move)
        elif st in ('hitstun', 'blockstun'):
            self.stun -= 1
            if self.stun <= 0:
                self.combo = 0 if st == 'hitstun' else self.combo
                if self.doomed:
                    self.setState('dizzy', 'dizzy')
                elif st == 'blockstun':
                    self.setState(self.blockState, self.blockState)
                    self.ai = 2
                elif self.animName == 'hit_crouch':
                    self.setState('crouch', 'crouch')
                    self.ai = 2
                else:
                    self.setState('idle', 'idle')
        elif st == 'lying':
            if self.t > 26 and not self.dead:
                if self.doomed:
                    self.setState('getup_dizzy', 'getup' if self.lastFall == 'fall' else 'sweepup')
                else:
                    self.setState('getup', 'getup' if self.lastFall == 'fall' else 'sweepup')
                self.invuln = True
        elif st in ('getup', 'getup_dizzy'):
            if self.animDone:
                self.invuln = False
                self.combo = 0
                if st == 'getup_dizzy' or self.doomed:
                    self.setState('dizzy', 'dizzy')
                else:
                    self.setState('idle', 'idle')
        elif st == 'sweepfall':
            if self.ai == len(self.animDef['seq']) - 1 and self.at >= 6:
                self.lastFall = 'sweep'
                self.setState('lying')
        elif st == 'frozen':
            self.stun -= 1
            if self.stun <= 0:
                self.frozenFrame = None
                self.setState('dizzy' if self.doomed else 'idle', 'dizzy' if self.doomed else 'idle')
        elif st == 'pulled':
            p = self.puller
            target = p.x + p.facing * 72
            d = target - self.x
            step = 15
            if abs(d) <= step:
                self.x = target
                self.stun = 70
                self.setState('stunned', 'dizzy')
            else:
                self.x += step if d > 0 else -step
        elif st == 'stunned':
            self.stun -= 1
            if self.stun <= 0:
                self.setState('dizzy' if self.doomed else 'idle', 'dizzy' if self.doomed else 'idle')
        elif st == 'special':
            kind = self.specialKind
            if self.ai == SPECIAL_SPAWN and not self.spawned:
                self.spawned = True
                match.spawnProjectile(self, kind)
            if kind == 'spear' and self.projectile is not None and self.ai >= SPECIAL_SPAWN:
                self.ai = SPECIAL_SPAWN  # segura o braço esticado até o arpão voltar
                self.at = 0
            if self.animDone:
                self.setState('idle', 'idle')
        elif st == 'slide':
            if self.t < 22:
                self.x += self.facing * (9.0 if self.t < 16 else 4.0)
            if self.t >= 30:
                self.move = None
                self.setState('crouch', 'crouch')
                self.ai = 2
        elif st == 'tele':
            # some, reaparece do outro lado do oponente e soca
            if self.t == 6:
                self.invisible = True
            if self.t == 16:
                opp = match.other(self)
                side = 1 if self.x < opp.x else -1      # lado em que eu estava
                nx = max(STAGE_MIN, min(STAGE_MAX, opp.x + side * 70))
                if abs(nx - opp.x) < 50:  # sem espaço atrás (canto): fica na frente
                    nx = max(STAGE_MIN, min(STAGE_MAX, opp.x - side * 70))
                self.x = nx
                self.faceTowards(opp)
                self.invisible = False
                self.invuln = False
                match.event('tele', int(self.x), int(self.y), self.idx)
                self.move = 'tele_punch'
                self.hitDone = False
                self.setState('attack', 'tele_punch')
        elif st == 'win':
            pass
        elif st == 'dead':
            pass

    # ------------------------------------------------------------ física
    def _physics(self, match):
        if self.state in ('jump', 'fall') or (self.state == 'attack' and MOVES[self.move].get('air')):
            self.x += self.vx
            self.y += self.vy
            self.vy -= GRAVITY
            if self.y <= 0 and self.vy < 0:
                self.y = 0.0
                self.vy = 0.0
                self.vx = 0.0
                if self.state == 'fall':
                    self.lastFall = 'fall'
                    match.event('land', int(self.x), 0, self.idx)
                    match.shakeScreen(5)
                    if self.dead:
                        self.setState('dead')
                    else:
                        self.setState('lying')
                else:
                    self.move = None
                    self.airAttack = False
                    self.setState('land', 'land')
        if self.push:
            self.x += self.push
            self.push *= 0.78
            if abs(self.push) < 0.2:
                self.push = 0.0
        if self.state == 'walk' and match.controlsEnabled(self):
            held = self.prevHeld
            if self.holdingFwd(held):
                self.x += self.facing * WALK_F
            elif self.holdingBack(held):
                self.x -= self.facing * WALK_B
        self.x = max(STAGE_MIN, min(STAGE_MAX, self.x))

    # ------------------------------------------------------------ reações
    def knockdown(self, dirX, launch=True, dead=False):
        self.dead = dead or self.dead
        self.move = None
        self.invuln = False
        if launch:
            self.vy = 9.5 if self.y <= 0 else max(self.vy, 5.0)
            self.vx = dirX * 4.2
            self.setState('fall', 'fall')
        else:
            self.setState('sweepfall', 'sweepfall')
            self.push = dirX * 3.0

    def hitBoxes(self):
        """(sheet, frame, facing, topleft) do frame atual."""
        return self.sheetFrame()
