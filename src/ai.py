# Oponente controlado pelo computador. Gera o mesmo bitmask de botões que um
# controle — o lutador da CPU obedece exatamente às mesmas regras do jogador.
import random
from inputs import UP, DOWN, LEFT, RIGHT, LP, HP, LK, HK, BLOCK, SPECIAL, FATAL
from fighter import NEUTRAL

LEVELS = {
    #          reação, chance de defender, pausa entre ações, uso de especial
    'EASY':   dict(react=24, block=0.20, idle=(18, 45), special=0.10, anti=0.15),
    'NORMAL': dict(react=13, block=0.50, idle=(8, 26), special=0.22, anti=0.40),
    'HARD':   dict(react=6, block=0.80, idle=(2, 12), special=0.30, anti=0.75),
}
LEVEL_NAMES = ['EASY', 'NORMAL', 'HARD']


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

    def _tap(self, mask, hold=2, after=4):
        return [mask] * hold + [0] * after

    def think(self, match, me):
        opp = match.other(me)
        fwd = RIGHT if me.facing > 0 else LEFT
        back = LEFT if me.facing > 0 else RIGHT
        dist = abs(opp.x - me.x)
        cfg = self.cfg
        rng = self.rng

        # o que a CPU "viu" há `react` ticks
        self.seen.append((opp.state, opp.move, opp.y, opp.x))
        if len(self.seen) > cfg['react']:
            self.seen.pop(0)
        oState, oMove, oY, oX = self.seen[0]

        if match.phase == 'finish':
            self.plan = []
            if me is match.winner:
                if self.fatalAt is None:
                    self.fatalAt = match.pt + rng.randint(40, 100)
                if match.pt >= self.fatalAt and match.loser.state == 'dizzy':
                    return FATAL if match.tick % 4 < 2 else 0
            return 0
        if match.phase != 'fight':
            self.plan = []
            return 0

        # perigo: golpe vindo ou projétil chegando -> defende
        threat = None
        if oState in ('attack', 'slide', 'dash') and dist < 170:
            threat = 'low' if oMove in ('sweep', 'clk', 'slide') else 'high'
        for p in match.projectiles:
            if p.owner is opp and not p.retract and (p.headX() - me.x) * p.facing < 0 and abs(p.headX() - me.x) < 230:
                threat = 'proj'
        # sorteia UMA vez por ameaça se vai reagir (não a cada tick)
        if threat and not self.lastThreat:
            self.willBlock = rng.random() < cfg['block']
        self.lastThreat = threat
        if threat and me.state in NEUTRAL + ('blockstun',):
            if self.plan and self.plan[0] & BLOCK:
                return self.plan.pop(0)
            if self.willBlock:
                self.willBlock = False
                if threat == 'proj' and rng.random() < 0.35 and dist > 200:
                    self.plan = [UP | fwd] * 3 + [0] * 10 + [LK] * 2 + [0] * 20
                else:
                    mask = BLOCK | (DOWN if threat == 'low' else 0)
                    self.plan = [mask] * rng.randint(14, 24)
                return self.plan.pop(0)

        if self.plan:
            return self.plan.pop(0)
        if me.state not in NEUTRAL:
            return 0
        if self.wait > 0:
            self.wait -= 1
            # enquanto "pensa", anda um pouco
            if dist > 200 and rng.random() < 0.5:
                return fwd
            return 0
        self.wait = rng.randint(*cfg['idle'])

        # anti-aéreo
        if oY > 20 and dist < 150 and rng.random() < cfg['anti']:
            self.plan = [DOWN] * 2 + [DOWN | HP] * 2 + [DOWN] * 8
            return self.plan.pop(0)
        # oponente indefeso: pune
        if oState in ('dizzy', 'stunned', 'frozen', 'pulled'):
            if dist > 110:
                self.plan = [fwd] * int((dist - 90) / 3.4)
            self.plan += [DOWN] * 2 + [DOWN | HP] * 2 + [DOWN] * 6 if rng.random() < 0.5 else [HK] * 2 + [0] * 16
            return self.plan.pop(0)

        canSpecial = me.projectile is None
        r = rng.random()
        if dist > 260:
            if canSpecial and r < cfg['special'] * 2:
                self.plan = self._tap(SPECIAL, 2, 30)
            elif r < 0.75:
                self.plan = [fwd] * rng.randint(15, 40)
            else:
                self.plan = [UP | fwd] * 3 + [fwd] * 14 + [HK] * 2 + [0] * 20
        elif dist > 120:
            if canSpecial and r < cfg['special']:
                if rng.random() < 0.5:   # especial 2 (slide, teleporte, voadora, fan lift...)
                    self.plan = [back | SPECIAL] * 2 + [0] * 26
                else:
                    self.plan = self._tap(SPECIAL, 2, 30)
            elif r < 0.65:
                self.plan = [fwd] * rng.randint(8, 22)
            elif r < 0.85:
                self.plan = [UP | fwd] * 3 + [fwd] * 12 + [LK] * 2 + [0] * 22
            else:
                self.plan = [back] * rng.randint(8, 16)
        else:
            choice = rng.random()
            if choice < 0.22:
                self.plan = [LP] * 2 + [0] * 5 + [LP] * 2 + [0] * 5 + [HP] * 2 + [0] * 12
            elif choice < 0.38:
                self.plan = [HK] * 2 + [0] * 22
            elif choice < 0.50:
                self.plan = [LK] * 2 + [0] * 18
            elif choice < 0.62:
                self.plan = [DOWN] * 2 + [DOWN | HK] * 2 + [DOWN] * 20
            elif choice < 0.72:
                self.plan = [DOWN] * 2 + [DOWN | LK] * 2 + [DOWN] * 10
            elif choice < 0.80:
                self.plan = [DOWN] * 2 + [DOWN | HP] * 2 + [DOWN] * 16
            elif choice < 0.90:
                self.plan = [BLOCK] * rng.randint(10, 20)
            else:
                self.plan = [back] * rng.randint(10, 24)
        return self.plan.pop(0) if self.plan else 0
