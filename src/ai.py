# Oponente controlado pelo computador. Gera o mesmo bitmask de botões que um
# controle — o lutador da CPU obedece exatamente às mesmas regras do jogador.
#
# Como ela "pensa":
#   * vê o oponente com atraso (tempo de reação), nunca o estado exato do tick;
#   * monta planos curtos (listas de botões) e os executa em ordem;
#   * emenda combos só quando o golpe acertou (hit-confirm) e, se foi
#     defendido em pé, troca para um golpe baixo;
#   * pune erros: golpe que errou, projétil jogado de longe, pulo que aterrissa;
#   * guarda hábitos do oponente (pula muito? defende muito? só joga
#     projétil? vem para cima?) e muda o estilo de acordo.
# Tudo isso é dosado pelo nível (EASY quase não usa; HARD usa sempre).
import random
from inputs import UP, DOWN, LEFT, RIGHT, LP, HP, LK, HK, BLOCK, SPECIAL, FATAL
from fighter import NEUTRAL, MOVES, DASH_KINDS

LEVELS = {
    # react: atraso de reação (ticks)      block: chance de defender
    # idle: pausa entre ações (ticks)      special: uso de especial
    # anti: anti-aéreo                     combo: chance de emendar após acertar
    # punish: chance de punir um erro      adapt: quanto os hábitos do oponente pesam
    'EASY':   dict(react=24, block=0.20, idle=(18, 45), special=0.10, anti=0.15, combo=0.15, punish=0.10,
                   adapt=0.0),
    'NORMAL': dict(react=13, block=0.50, idle=(8, 26), special=0.22, anti=0.45, combo=0.55, punish=0.45,
                   adapt=0.5),
    'HARD':   dict(react=6, block=0.80, idle=(2, 12), special=0.30, anti=0.80, combo=0.90, punish=0.85,
                   adapt=1.0),
}
LEVEL_NAMES = ['EASY', 'NORMAL', 'HARD']

# combos: depois de acertar o golpe X, emenda Y (botão, segurando baixo?)
CHAIN = {
    'lp': (LP, False), 'clp': (LP, True),
    'hp': (HP, True), 'hp2': (HP, True),          # soco forte -> uppercut
    'lk': (HK, False),                            # chute fraco -> chute forte
    'clk': (HK, True),                            # chute baixo -> rasteira
}
CHAIN_MAX = 3
LOW_MOVES = ('sweep', 'clk', 'slide')
HABIT_DECAY = 0.9993     # hábitos "esquecem" aos poucos (meia-vida ~16 s)


class CPU:
    def __init__(self, level='NORMAL', seed=None):
        self.cfg = LEVELS[level]
        self.rng = random.Random(seed)
        self.plan = []
        self.wait = 30
        self.seen = []         # memória do oponente (atraso de reação)
        self.fatalAt = None
        self.lastThreat = None
        self.willBlock = False
        self.lastOut = 0
        # combo em andamento
        self.comboMove = None  # golpe que já emendou (não emenda duas vezes o mesmo)
        self.comboLen = 0
        # hábitos do oponente (contagens que decaem com o tempo)
        self.habit = {'jump': 0.0, 'proj': 0.0, 'block': 0.0, 'rush': 0.0, 'low': 0.0}
        self.lastSeenState = None

    def _tap(self, mask, hold=2, after=4):
        return [mask] * hold + [0] * after

    def _out(self, mask):
        self.lastOut = mask
        return mask

    # ------------------------------------------------------------ percepção
    def _perceive(self, match, me, opp):
        # o que a CPU "viu" há `react` ticks
        self.seen.append(dict(state=opp.state, move=opp.move, y=opp.y, vy=opp.vy, x=opp.x,
                              t=opp.t, hitDone=opp.hitDone, ai=opp.ai, proj=opp.projectile is not None,
                              approaching=(opp.x - me.x) * opp.facing < 0 and opp.state == 'walk'
                              and opp.animName == 'walk'))
        if len(self.seen) > self.cfg['react']:
            self.seen.pop(0)
        o = self.seen[0]
        # hábitos: conta quando o oponente (visto) entra em cada situação
        for k in self.habit:
            self.habit[k] *= HABIT_DECAY
        if o['state'] != self.lastSeenState:
            st = o['state']
            if st == 'prejump':
                self.habit['jump'] += 1
            elif st == 'special':
                self.habit['proj'] += 1
            elif st in ('block', 'cblock') and me.state == 'attack':
                self.habit['block'] += 1
            elif st == 'attack' and o['move'] in LOW_MOVES:
                self.habit['low'] += 1
            elif st == 'attack' and abs(o['x'] - me.x) < 120:
                self.habit['rush'] += 1
            self.lastSeenState = st
        if o['approaching'] and abs(o['x'] - me.x) < 200:
            self.habit['rush'] += 0.005
        return o

    def _likes(self, habit):
        """Quão marcante é um hábito do oponente (0..1), já pesado pelo nível."""
        total = sum(self.habit.values()) + 1.0
        return self.cfg['adapt'] * min(1.0, 2.0 * self.habit[habit] / total)

    # ------------------------------------------------------------ combo
    def _combo(self, me, opp):
        """Emenda o próximo golpe se o atual acertou (hit-confirm)."""
        if me.state != 'attack' or me.move is None or not me.hitDone:
            return None
        mv = MOVES.get(me.move)
        if mv is None or mv.get('air') or me.ai <= mv['active'][1]:
            return None
        if self.comboMove == (me.move, me.t) or self.comboLen >= CHAIN_MAX:
            return 0
        rng = self.rng
        self.comboMove = (me.move, me.t)
        blocked = opp.state == 'blockstun'
        if blocked:
            # defendido em pé: a mistura é o golpe baixo; agachado: para
            if opp.blockState == 'block' and rng.random() < self.cfg['combo'] * 0.6:
                self.comboLen += 1
                return DOWN | HK
            return 0
        if opp.state not in ('hitstun', 'fall') or rng.random() > self.cfg['combo']:
            return 0
        nxt = CHAIN.get(me.move)
        if nxt is None:
            return 0
        if me.move in ('lp', 'clp') and self.comboLen >= 1:   # 2 socos fracos e fecha com o forte
            nxt = (HP, me.move == 'clp')
        self.comboLen += 1
        bit, down = nxt
        return bit | (DOWN if down else 0)

    # ------------------------------------------------------------ cérebro
    def think(self, match, me):
        opp = match.other(me)
        fwd = RIGHT if me.facing > 0 else LEFT
        back = LEFT if me.facing > 0 else RIGHT
        dist = abs(opp.x - me.x)
        cfg = self.cfg
        rng = self.rng
        o = self._perceive(match, me, opp)
        oState, oMove, oY = o['state'], o['move'], o['y']

        if match.phase == 'finish':
            self.plan = []
            if me is match.winner:
                if self.fatalAt is None:
                    self.fatalAt = match.pt + rng.randint(40, 100)
                if match.pt >= self.fatalAt and match.loser.state == 'dizzy':
                    return self._out(FATAL if match.tick % 4 < 2 else 0)
            return self._out(0)
        if match.phase != 'fight':
            self.plan = []
            return self._out(0)

        # 1) combo em andamento: emenda (ou espera o golpe terminar)
        if me.state != 'attack':
            self.comboLen = 0
        c = self._combo(me, opp)
        if c is not None:
            self.plan = []
            # botão novo só conta na borda: solta se o anterior ainda estava apertado
            if c and self.lastOut & c & (LP | HP | LK | HK):
                return self._out(0)
            if c:
                self.plan = [c, c & DOWN]     # segura 2 ticks (mantém o baixo)
            return self._out(c)
        # depois do uppercut que levantou o oponente: projétil nele no ar (HARD)
        if (me.state in NEUTRAL and opp.state == 'fall' and opp.vy > 0 and me.projectile is None
                and 120 < dist < 330 and rng.random() < cfg['combo'] * 0.08):
            self.plan = self._tap(SPECIAL, 2, 20)
            return self._out(self.plan.pop(0))

        # 2) perigo: golpe vindo ou projétil chegando -> defende (ou rebate)
        threat = None
        if oState in ('attack', 'slide', 'dash') and dist < 170:
            threat = 'low' if oMove in LOW_MOVES else 'high'
        for p in match.projectiles:
            if p.owner is opp and not p.retract and (p.headX() - me.x) * p.facing < 0 and abs(p.headX() - me.x) < 230:
                threat = 'proj'
        # sorteia UMA vez por ameaça se vai reagir (não a cada tick)
        if threat and not self.lastThreat:
            self.willBlock = rng.random() < cfg['block']
        self.lastThreat = threat
        if threat and me.state in NEUTRAL + ('blockstun',):
            if self.plan and self.plan[0] & BLOCK:
                return self._out(self.plan.pop(0))
            if self.willBlock:
                self.willBlock = False
                if threat == 'proj' and dist > 200:
                    r = rng.random()
                    if me.projectile is None and r < 0.4 * cfg['punish'] + 0.1:
                        # projétil contra projétil: os dois se anulam
                        self.plan = self._tap(SPECIAL, 2, 20)
                        return self._out(self.plan.pop(0))
                    if r < 0.55:   # pula por cima e chuta
                        self.plan = [UP | fwd] * 3 + [0] * 10 + [LK] * 2 + [0] * 20
                        return self._out(self.plan.pop(0))
                low = threat == 'low' or (threat == 'high' and self._likes('low') > 0.5 and rng.random() < 0.3)
                self.plan = [BLOCK | (DOWN if low else 0)] * rng.randint(14, 24)
                return self._out(self.plan.pop(0))

        if self.plan:
            return self._out(self.plan.pop(0))
        if me.state not in NEUTRAL:
            return self._out(0)

        # 3) oportunidades (não esperam o "pensar")
        plan = self._opportunity(me, opp, o, dist, fwd, back)
        if plan:
            self.plan = plan
            return self._out(self.plan.pop(0))

        if self.wait > 0:
            self.wait -= 1
            # enquanto "pensa", anda um pouco (para longe se o oponente pula muito)
            if dist > 200 and rng.random() < 0.5:
                return self._out(fwd)
            return self._out(0)
        self.wait = rng.randint(*cfg['idle'])

        # 4) escolha pela distância, pesada pelos hábitos do oponente
        self.plan = self._neutral(me, opp, dist, fwd, back)
        return self._out(self.plan.pop(0) if self.plan else 0)

    # ------------------------------------------------------------ oportunidades
    def _opportunity(self, me, opp, o, dist, fwd, back):
        cfg = self.cfg
        rng = self.rng
        oState = o['state']
        # anti-aéreo: oponente caindo de um pulo perto de mim -> uppercut
        if o['y'] > 20 and o['vy'] < 2 and dist < 140 and oState in ('jump', 'attack'):
            if rng.random() < cfg['anti']:
                return [DOWN] * 2 + [DOWN | HP] * 2 + [DOWN] * 8
            if rng.random() < cfg['block']:
                return [BLOCK] * 16
        # oponente indefeso: chega perto e bate (combo de verdade)
        if oState in ('dizzy', 'stunned', 'frozen', 'pulled'):
            plan = [fwd] * int((dist - 80) / 3.4) if dist > 100 else []
            if rng.random() < 0.5:
                return plan + [DOWN] * 2 + [DOWN | HP] * 2 + [DOWN] * 6
            return plan + self._tap(LP, 2, 3) + self._tap(LP, 2, 3) + self._tap(HP, 2, 14)
        if rng.random() > cfg['punish']:
            return None
        # golpe que errou (ou foi defendido) e o oponente ainda está se recuperando
        if oState == 'attack' and o['move'] in MOVES and not o['hitDone'] and not MOVES[o['move']].get('air'):
            if o['ai'] > MOVES[o['move']]['active'][1] and dist < 115:
                return [DOWN] * 2 + [DOWN | HP] * 2 + [DOWN] * 8 if rng.random() < 0.6 else \
                    [DOWN] * 2 + [DOWN | HK] * 2 + [DOWN] * 14
        # projétil jogado de longe: o oponente está parado lançando -> avança nele
        if oState == 'special' and dist > 170:
            kind = me.char.special2
            if kind in DASH_KINDS or kind == 'teleport':
                return [back | SPECIAL] * 2 + [0] * 24
            if dist < 330:
                return [UP | fwd] * 3 + [fwd] * 12 + [HK] * 2 + [0] * 20
        # aterrissou de um pulo perto: pune antes que ele se mexa
        if oState == 'land' and dist < 110:
            return self._tap(LP, 2, 3) + self._tap(LP, 2, 3) + self._tap(HP, 2, 12)
        return None

    # ------------------------------------------------------------ neutro
    def _neutral(self, me, opp, dist, fwd, back):
        cfg = self.cfg
        rng = self.rng
        canSpecial = me.projectile is None
        jumper = self._likes('jump')
        blocker = self._likes('block')
        zoner = self._likes('proj')
        rusher = self._likes('rush')
        r = rng.random()
        if dist > 260:
            # contra quem pula muito, o projétil vira isca: espera ele aterrissar
            pSpecial = cfg['special'] * 2 * (1 - 0.6 * jumper)
            if canSpecial and r < pSpecial:
                return self._tap(SPECIAL, 2, 30)
            if zoner > 0.4 and r < pSpecial + 0.25:   # quem só joga projétil: entra pulando
                return [UP | fwd] * 3 + [fwd] * 14 + [HK] * 2 + [0] * 20
            if r < 0.75:
                return [fwd] * rng.randint(15, 40)
            return [UP | fwd] * 3 + [fwd] * 14 + [HK] * 2 + [0] * 20
        if dist > 120:
            if canSpecial and r < cfg['special'] * (1 + blocker):
                if rng.random() < 0.5:   # especial 2 (slide, teleporte, voadora, fan lift...)
                    return [back | SPECIAL] * 2 + [0] * 26
                return self._tap(SPECIAL, 2, 30)
            if jumper > 0.4 and r < 0.5:   # quem pula muito: espera na meia distância
                return [0] * rng.randint(10, 20)
            if r < 0.65:
                return [fwd] * rng.randint(8, 22)
            if r < 0.85 and jumper < 0.6:
                return [UP | fwd] * 3 + [fwd] * 12 + [LK] * 2 + [0] * 22
            return [back] * rng.randint(8, 16)
        # perto: contra quem defende muito, ataca baixo; contra quem ataca muito, defende e pune
        if rusher > 0.4 and rng.random() < 0.35 * rusher:
            return [BLOCK] * rng.randint(12, 20)
        lowBias = 0.35 * blocker
        choice = rng.random()
        if choice < lowBias:
            return [DOWN] * 2 + [DOWN | LK] * 2 + [DOWN] * 10 if rng.random() < 0.5 else \
                [DOWN] * 2 + [DOWN | HK] * 2 + [DOWN] * 20
        choice = rng.random()
        if choice < 0.24:
            return self._tap(LP, 2, 20)      # o combo emenda sozinho se acertar
        if choice < 0.38:
            return self._tap(HK, 2, 22)
        if choice < 0.52:
            return self._tap(LK, 2, 18)
        if choice < 0.62:
            return [DOWN] * 2 + [DOWN | HK] * 2 + [DOWN] * 20
        if choice < 0.72:
            return [DOWN] * 2 + [DOWN | LK] * 2 + [DOWN] * 10
        if choice < 0.80:
            return [DOWN] * 2 + [DOWN | HP] * 2 + [DOWN] * 16
        if choice < 0.88:
            return self._tap(HP, 2, 18)
        if choice < 0.94:
            return [BLOCK] * rng.randint(10, 20)
        return [back] * rng.randint(10, 24)
