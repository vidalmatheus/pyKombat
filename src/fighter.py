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
TELE_GAP = 2 * BODY_HALF + 2   # distância do oponente ao reaparecer do teleporte
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
    'hp2': A('Bpunch', [3, 4, 5, 5, 4, 3], [3, 3, 5, 3, 3, 3]),   # soco forte com o outro braço (alterna)
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
    'hit_low': A('Bhit', [0, 1, 2, 1, 0], [2, 3, 6, 3, 2]),   # chute baixo em quem está em pé
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
    # especiais extras: animação genérica (cada lutador pode ter a sua em BASE_ANIMS)
    'fanswipe': A('Bpunch', [6, 7, 8, 8, 7, 6], [3, 3, 3, 6, 4, 3]),
    'bladeswipe': A('Bpunch', [3, 4, 5, 5, 4, 3], [3, 3, 3, 6, 4, 3]),
    'splitpunch': A('Cpunch', [0, 1, 2, 2, 2, 1], [3, 3, 3, 8, 4, 3]),
    'gotcha': A('Bpunch', [6, 7, 8, 7, 8, 6], [4, 4, 5, 5, 6, 4]),
    'shadowup': A('Dpunch', [1, 2, 3, 4, 4], [3, 3, 4, 8, 6]),
    'special3': A('Special', range(6), [3, 4, 4, 10, 5, 4]),
    'special4': A('Special', range(6), [3, 4, 4, 10, 5, 4]),
}
BASE_ANIMS = {
    # --- tiras de tools/mk2_sprites.py (MK2 SNES); o projétil sai no índice 3
    'Sub-Zero': {
        'idle': A('dance', [0, 1, 2, 3, 4, 5, 4, 3, 2, 1], 6, True),
        'dizzy': A('dizzy', [0, 1, 2, 3, 4, 3, 2, 1], 7, True),
        'special': A('Special', range(6), [3, 4, 4, 10, 5, 4]),
        'slide': A('Fkick', [0, 1], [3, HOLD]),
        'pulled': A('Chit', [0, 1, 2, 1], 5, True),
        'win': A('win', range(3), [8, 8, HOLD]),
        'cast': A('Special', [0, 1, 2], [4, 4, HOLD]),
        # bola de gelo (0-7), arremesso no 10 (a vítima congela), uppercut no 16 (estilhaça):
        # mesmos tempos de fatalfx.FREEZE_AT / SHATTER_AT
        'special3': A('Special3', range(6), [3, 4, 4, 10, 5, 4]),
        'fatal': A('fatality', range(19), [6] * 8 + [6, 6, 10, 10, 10, 8, 6, 6, 8, 8, HOLD]),
    },
    'Scorpion': {
        'idle': A('dance', [0, 1, 2, 3, 4, 5, 4, 3, 2, 1], 6, True),
        'dizzy': A('dizzy', [0, 1, 2, 3, 4, 3, 2, 1], 7, True),
        # arremesso: projétil no índice 3; segura o braço esticado enquanto o arpão voa
        'special': A('Special', range(6), [3, 4, 4, 6, 4, 4]),
        'pulled': A('Chit', [0, 1, 2, 1], 5, True),
        'win': A('win', range(4), [7, 8, 8, HOLD]),
        'cast': A('Special', [0, 1, 2], [4, 4, HOLD]),
        # tira a máscara e cospe fogo a partir do índice 8 (fatalfx.FIRE_AT)
        'fatal': A('fatality', range(14), [6, 8, 8, 8, 10, 10, 10, 6] + [12] * 5 + [HOLD]),
    },
    'LiuKang': {
        'idle': A('dance', [0, 1, 2, 3, 4, 5, 4, 3, 2, 1], 6, True),
        'dizzy': A('dizzy', [0, 1, 2, 3, 4, 5, 4, 3, 2, 1], 7, True),
        'special': A('Special', range(6), [3, 4, 4, 10, 5, 4]),
        'dash': A('Fkick', [0, 1], [5, HOLD]),
        'pulled': A('Chit', [0, 1, 2, 1], 5, True),
        'win': A('win', [0, 1, 2, 3], [8, 8, 8, HOLD]),
        'cast': A('Special', [0, 1, 2], [4, 4, HOLD]),
        # vira dragão (0-11), morde no 11 e volta a ser o Liu Kang
        'special3': A('Special3', range(6), [3, 4, 4, 10, 5, 4]),
        'dash_bicycle': A('Fkick2', range(6), 3, True),
        'fatal': A('fatality', list(range(12)) + list(range(10, -1, -1)),
                   [8, 8, 7, 7, 6, 6, 6, 6, 6, 6, 5, 30] + [5] * 10 + [HOLD]),
    },
    'Kitana': {
        'idle': A('dance', [0, 1, 2, 3, 4, 3, 2, 1], 7, True),
        'walk': A('walk', range(8), 5, True),
        'walkb': A('walk', range(7, -1, -1), 5, True),
        'dizzy': A('dizzy', [0, 1, 2, 3, 4, 3, 2, 1], 7, True),
        'special': A('Special', range(6), [3, 4, 4, 10, 5, 4]),
        'special2': A('Special2', range(6), [3, 4, 4, 10, 5, 4]),
        'pulled': A('Chit', [0, 1, 2, 1], 5, True),
        'win': A('win', [0, 1, 2, 3], [8, 8, 8, HOLD]),
        'cast': A('Special', [0, 1, 2], [4, 4, HOLD]),
        # gira o leque e corta no índice 6
        'fanswipe': A('Swipe', range(6), [3, 3, 3, 6, 4, 3]),
        'dash_squarewave': A('Fkick', [0, 1, 2], [4, 4, HOLD]),
        'fatal': A('fatality', range(8), [8, 7, 6, 6, 5, 4, 30, HOLD]),
    },
    'Raiden': {
        'idle': A('dance', [0, 1, 2, 3, 4, 5, 6, 7, 6, 5, 4, 3, 2, 1], 5, True),
        'walk': A('walk', range(8), 5, True),
        'walkb': A('walk', range(7, -1, -1), 5, True),
        'dizzy': A('dizzy', [0, 1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1], 6, True),
        'special': A('Special', range(6), [3, 4, 4, 10, 5, 4]),
        'dash': A('Fkick', [0, 1], [5, HOLD]),
        'pulled': A('Chit', [0, 1, 2, 1], 5, True),
        'win': A('win', [0, 1, 2, 3, 4], [7, 7, 7, 8, HOLD]),
        'cast': A('Special', [0, 1, 2], [4, 4, HOLD]),
        'fatal': A('fatality', [0, 1, 2], [8, 8, HOLD]),   # braços para o céu: o raio cai (fatalfx)
    },
    'KungLao': {
        'idle': A('dance', [0, 1, 2, 3, 4, 5, 4, 3, 2, 1], 6, True),
        'dizzy': A('dizzy', [0, 1, 2, 3, 4, 5, 4, 3, 2, 1], 7, True),
        'special': A('Special', range(6), [3, 4, 5, 8, 5, 4]),
        'pulled': A('Chit', [0, 1, 2, 1], 5, True),
        'win': A('win', range(6), [7, 7, 7, 7, 8, HOLD]),
        'cast': A('Special', [0, 1, 2], [4, 4, HOLD]),
        # tira o chapéu e arremessa; segura o braço esticado enquanto o chapéu corta (fatalfx)
        'dash_spin': A('Fkick', range(6), 2, True),
        'fatal': A('fatality', range(10), [6, 6, 6, 6, 6, 6, 6, 6, 6, HOLD]),
    },
    'JohnnyCage': {
        'idle': A('dance', [0, 1, 2, 3, 4, 3, 2, 1], 6, True),
        'walk': A('walk', range(8), 5, True),
        'walkb': A('walk', range(7, -1, -1), 5, True),
        'dizzy': A('dizzy', [0, 1, 2, 3, 4, 5, 4, 3, 2, 1], 7, True),
        'special': A('Special', range(6), [3, 4, 4, 10, 5, 4]),
        'dash': A('Fkick', [0, 1], [5, HOLD]),
        'pulled': A('Chit', [0, 1, 2, 1], 5, True),
        'win': A('win', range(5), [8, 8, 8, 8, HOLD]),
        'cast': A('Special', [0, 1, 2], [4, 4, HOLD]),
        # agacha e solta o uppercut: a cabeça voa no índice 4
        'shadowup': A('Upper2', [0, 1, 2, 3, 3], [3, 3, 4, 8, 6]),
        'splitpunch': A('Split', range(6), [3, 3, 3, 8, 4, 3]),
        'fatal': A('fatality', range(7), [10, 8, 6, 5, 30, 20, HOLD]),
    },
    'Baraka': {
        'idle': A('dance', range(6), 7, True),
        'dizzy': A('dizzy', [0, 1, 2, 3, 4, 3, 2, 1], 7, True),
        'special': A('Special', range(6), [3, 4, 4, 10, 5, 4]),
        'dash': A('Fkick', [0, 1, 2, 3, 2, 1, 2, 3, 2, 1], 3, True),   # lâminas girando
        'pulled': A('Chit', [0, 1, 2, 1], 5, True),
        'win': A('win', range(4), [8, 8, 8, HOLD]),
        'cast': A('Special', [0, 1, 2], [4, 4, HOLD]),
        'bladeswipe': A('Swipe', range(6), [3, 3, 3, 6, 4, 3]),
        'fatal': A('fatality', range(11), [10, 8, 5, 4, 30, 4, 4, 4, 5, 8, HOLD]),
    },
    'Mileena': {
        'idle': A('dance', list(range(10)) + list(range(8, 0, -1)), 4, True),
        'walk': A('walk', range(8), 5, True),
        'walkb': A('walk', range(7, -1, -1), 5, True),
        'dizzy': A('dizzy', [0, 1, 2, 3, 4, 3, 2, 1], 7, True),
        'special': A('Special', range(6), [3, 4, 4, 10, 5, 4]),
        'dash': A('Fkick', [0] + [1, 2, 3, 4, 5, 6, 7] * 4, 2, True),   # rola pelo chão
        'pulled': A('Chit', [0, 1, 2, 1], 5, True),
        'win': A('win', range(6), [8, 8, 8, 8, 8, HOLD]),
        'cast': A('Special', [0, 1, 2], [4, 4, HOLD]),
        'tele_out': A('Telekick', [0, 1, 2], [4, 4, HOLD]),
        'telejk': A('Telekick', [3, 4, 4], [4, 4, HOLD]),
        'fatal': A('fatality', range(14), [8, 5, 5, 5, 5, 5, 5, 5, 6, 10, 8, 8, 20, HOLD]),
    },
    'ShangTsung': {
        'idle': A('dance', [0, 1, 2, 3, 4, 3, 2, 1], 7, True),
        'dizzy': A('dizzy', [0, 1, 2, 3, 4, 3, 2, 1], 7, True),
        'special': A('Special', range(6), [3, 4, 4, 10, 5, 4]),
        'special2': A('Special2', range(6), [3, 5, 5, 14, 6, 4]),
        'pulled': A('Chit', [0, 1, 2, 1], 5, True),
        'win': A('win', range(4), [7, 7, 8, HOLD]),
        'cast': A('Special', [0, 1, 2], [4, 4, HOLD]),
        # guarda, estende a mão (segura enquanto a alma sai), puxa, ergue os braços
        'fatal': A('fatality', range(5), [12, 90, 10, 10, HOLD]),
    },
    'Jax': {
        'idle': A('dance', [0, 1, 2, 3, 4, 3, 2, 1], 7, True),
        'dizzy': A('dizzy', [0, 1, 2, 3, 4, 3, 2, 1], 7, True),
        'special': A('Special', range(6), [3, 4, 4, 10, 5, 4]),
        'special2': A('Special2', range(6), [4, 4, 4, 8, 8, 5]),
        'pulled': A('Chit', [0, 1, 2, 1], 5, True),
        'win': A('win', range(6), [7, 7, 7, 7, 8, HOLD]),
        'cast': A('Special', [0, 1, 2], [4, 4, HOLD]),
        # agarra (1), puxa os braços (2-5): o sangue espirra no índice 5
        'gotcha': A('Grab', range(6), [4, 4, 5, 5, 6, 4]),
        'fatal': A('fatality', range(10), [10, 12, 8, 8, 8, 25, 10, 10, 10, HOLD]),
    },
}
SPECIAL_SPAWN = 3                  # índice da sequência em que o projétil sai
# quando a vítima se parte (fatality 'anim'): índice da sequência do vencedor
FATAL_SPLIT_FRAME = {'LiuKang': 11, 'Kitana': 6, 'JohnnyCage': 4,
                     'Baraka': 4, 'Mileena': 2, 'Jax': 5}
# especiais em que o lutador avança reto para a frente -> altura do voo
# (o sprite é desenhado acima do chão; 0 = vai pelo chão)
DASH_KINDS = {'flykick': 34, 'torpedo': 34, 'shadowkick': 20, 'bladefury': 0, 'roll': 0,
              'bicycle': 30, 'squarewave': 40, 'spin': 0}
# especiais de corpo a corpo (golpe com animação própria; a tabela MOVES diz o dano)
MELEE_SPECIALS = ('fanswipe', 'bladeswipe', 'splitpunch', 'gotcha', 'shadowup')
# especiais 3 e 4: comandos (além do botão SPECIAL com baixo / para a frente)
SPECIAL3_MOTION = ['b', 'f']    # trás, frente + soco forte
SPECIAL4_MOTION = ['f', 'b']    # frente, trás + chute forte

# golpes normais: anim, dano, altura (high/mid/low), reação, janela ativa (índices da seq)
MOVES = {
    'lp': dict(dmg=4, level='high', react='hi', active=(2, 3), stun=14, push=1.2),
    'hp': dict(dmg=7, level='high', react='mid', active=(2, 3), stun=17, push=5.0),
    'hp2': dict(dmg=7, level='high', react='mid', active=(2, 3), stun=17, push=5.0),
    'lk': dict(dmg=6, level='high', react='mid', active=(5, 6), stun=16, push=5.0),
    'hk': dict(dmg=9, level='high', react='heavy', active=(5, 6), stun=22, push=6.5),
    'clp': dict(dmg=3, level='mid', react='hi', active=(2, 3), stun=12, push=1.5),
    'clk': dict(dmg=4, level='low', react='hi', active=(4, 5), stun=13, push=3.0),
    'upper': dict(dmg=13, level='mid', react='launch', active=(3, 4), stun=0, push=4.0),
    'sweep': dict(dmg=8, level='low', react='sweep', active=(3, 4), stun=0, push=2.0),
    'jk': dict(dmg=9, level='high', react='heavy', active=(2, 2), stun=20, push=5.0, air=True),
    'jp': dict(dmg=7, level='high', react='mid', active=(2, 2), stun=17, push=4.0, air=True),
    'slide': dict(dmg=9, level='low', react='sweep', active=(1, 1), stun=0, push=3.0, special=True),
    'tele_punch': dict(dmg=10, level='high', react='launch', active=(1, 2), stun=0, push=4.0, special=True,
                       advance=2.0),
    'dash': dict(dmg=10, level='high', react='launch', active=(1, 1), stun=0, push=4.0, special=True),
    # especiais de corpo a corpo (advance: px/tick para a frente até o fim da janela ativa)
    'fanswipe': dict(dmg=10, level='high', react='heavy', active=(3, 3), stun=24, push=6.0, special=True,
                     advance=2.5),
    'bladeswipe': dict(dmg=11, level='high', react='heavy', active=(3, 3), stun=24, push=6.0, special=True),
    'splitpunch': dict(dmg=10, level='low', react='heavy', active=(3, 3), stun=28, push=3.0, special=True),
    'gotcha': dict(dmg=13, level='high', react='heavy', active=(2, 4), stun=26, push=4.0, special=True,
                   advance=3.0),
    'shadowup': dict(dmg=12, level='mid', react='launch', active=(1, 3), stun=0, push=4.0, special=True,
                     advance=7.0),
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
        self.flipBack = False
        self.lastFall = 'fall'
        self.jumpDir = 0
        self.blockState = 'block'
        self.hpAlt = True        # o próximo soco forte usa o braço da frente
        self.dashKind = None
        self.teleKick = False
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
            step = int(prog * 7)
            # pulo para trás: a cambalhota gira no sentido contrário
            return a['sheet'], (7 - step) if self.flipBack else (1 + step)
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
        return self.y <= 0 and self.state not in ('jump', 'prejump', 'fall', 'tele', 'dash')

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
            extra = len(self.char.extra)
            if pressed & SPECIAL:
                if self.holdingBack(held):
                    sp = 2
                elif held & DOWN and extra >= 1:
                    sp = 3
                elif self.holdingFwd(held) and extra >= 2:
                    sp = 4
                else:
                    sp = 1
            elif pressed & LP and self.motion(tick, ['d', 'df', 'f']):
                sp = 1
            elif pressed & LK and self.motion(tick, ['d', 'db', 'b']):
                sp = 2
            elif extra >= 1 and pressed & HP and self.motion(tick, SPECIAL3_MOTION, 16):
                sp = 3
            elif extra >= 2 and pressed & HK and self.motion(tick, SPECIAL4_MOTION, 16):
                sp = 4
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
        if mv == 'hp':  # socos fortes seguidos alternam os braços
            self.hpAlt = not self.hpAlt
            if self.hpAlt:
                mv = 'hp2'
        self.move = mv
        self.hitDone = False
        self.setState('attack', mv)

    def startSpecial(self, which, match):
        kinds = [self.char.special, self.char.special2] + [k for k, _ in self.char.extra]
        kind = kinds[which - 1]
        own = BASE_ANIMS.get(self.base, {})
        if kind == 'slide':
            self.move = 'slide'
            self.hitDone = False
            self.setState('slide', 'slide')
            match.sound('block', 0.5)
        elif kind in ('teleport', 'telekick'):
            self.teleKick = kind == 'telekick'
            self.setState('tele', 'tele_out' if self.teleKick and 'tele_out' in own else 'stand')
            self.invuln = True
            match.event('tele', int(self.x), int(self.y), self.idx)
        elif kind in DASH_KINDS:
            self.dashKind = kind
            self.move = 'dash'
            self.hitDone = False
            # voadora própria do golpe ('dash_<kind>') ou a padrão do lutador
            name = 'dash_' + kind if 'dash_' + kind in own else 'dash' if 'dash' in own else 'hk'
            self.setState('dash', name)
            match.sound('block', 0.5)
        elif kind in MELEE_SPECIALS:
            self.startAttack(kind)
        else:
            self.specialKind = kind
            self.spawned = False
            # especial com animação própria (special2/3/4); senão a do especial 1
            name = 'special%d' % which if which > 1 and 'special%d' % which in own else 'special'
            self.setState('special', name)

    # ------------------------------------------------------------ estados
    def _advance(self, held, pressed, match):
        st = self.state
        if st == 'attack':
            mv = MOVES[self.move]
            if mv.get('air'):
                return  # golpe aéreo é tratado em _physics (fica até aterrissar)
            if mv.get('advance') and not self.hitDone and self.ai <= mv['active'][1]:
                self.x += self.facing * mv['advance']
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
                self.flipBack = self.jumpDir == -self.facing
                self.airAttack = False
                self.setState('jump', 'flip' if self.flip else 'jump')
                self.move = None
        elif st == 'jump':
            if not self.airAttack and pressed & (LP | HP | LK | HK):
                self.faceTowards(match.other(self))
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
        elif st == 'dash':
            # voadora / torpedo: sobe um pouco, cruza a tela reto e cai em pé
            height = DASH_KINDS[self.dashKind]
            if self.t < 6:
                self.y = height * self.t / 6
            elif self.t < 30 and not self.hitDone:
                self.x += self.facing * (11.0 if height else 7.0)
                self.y = height
            else:
                self.y = max(0.0, self.y - 6)
                if self.y <= 0:
                    self.move = None
                    self.setState('land', 'land')
        elif st == 'tele':
            # some, reaparece do outro lado do oponente e soca
            if self.t == 6:
                self.invisible = True
            if self.t == 16:
                opp = match.other(self)
                side = 1 if self.x < opp.x else -1      # lado em que eu estava
                # reaparece colado nas costas (a 70 px o soco não alcançava)
                nx = max(STAGE_MIN, min(STAGE_MAX, opp.x + side * TELE_GAP))
                if abs(nx - opp.x) < TELE_GAP - 6:  # sem espaço atrás (canto): fica na frente
                    nx = max(STAGE_MIN, min(STAGE_MAX, opp.x - side * TELE_GAP))
                self.x = nx
                self.faceTowards(opp)
                self.invisible = False
                self.invuln = False
                match.event('tele', int(self.x), int(self.y), self.idx)
                self.hitDone = False
                if self.teleKick:   # reaparece no alto e cai chutando
                    self.y = 120.0
                    self.vy = 0.0
                    self.vx = self.facing * 2.5
                    self.flip = False
                    self.airAttack = True
                    self.move = 'jk'
                    self.setState('jump', 'telejk' if 'telejk' in BASE_ANIMS.get(self.base, {}) else 'jk')
                    self.ai = 1
                else:
                    self.move = 'tele_punch'
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
