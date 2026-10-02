# Loop da luta: passo fixo de 60 Hz, desenho a cada frame.
# Modos: 'versus' (2 jogadores locais), 'cpu', 'host' e 'guest' (online).
import asyncio
import time
import pygame
import ai
import assets
import characters
import ui
from match import Match
from render import Renderer

STEP = 1.0 / 60
MAX_STEPS = 5


def music(name, volume):
    try:
        pygame.mixer.music.load('res/Music/%s.ogg' % name)
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(volume)
    except Exception as e:
        print('music error', e)


class Fight:
    def __init__(self, game, hub, setup):
        """setup: mode, chars (índices), stage, seed, cpuLevel, net, players."""
        self.screen = game.getDisplay()
        self.hub = hub
        self.setup = setup
        self.mode = setup['mode']
        self.net = setup.get('net')
        c1, c2 = (characters.ROSTER[i] for i in setup['chars'])
        self.renderer = Renderer(self.screen)
        if self.mode == 'host':
            self.renderer.label = 'ONLINE - HOST'
        elif self.mode == 'guest':
            self.renderer.label = 'ONLINE - GUEST'
        elif self.mode == 'cpu':
            self.renderer.label = 'VS CPU - %s' % setup.get('cpuLevel', 'NORMAL')
        self.match = None
        if self.mode != 'guest':
            self.match = Match(c1, c2, setup['stage'], seed=setup.get('seed'))
        else:  # convidado só desenha; pré-carrega os sprites para não engasgar
            for c, alt in ((c1, False), (c2, c1 is c2)):
                assets.preload(c, alt)
        self.players = setup['players']   # inputs.Player por lado (None = CPU/remoto)
        self.cpu = None
        if self.mode == 'cpu':
            self.cpu = ai.CPU(setup.get('cpuLevel', 'NORMAL'), seed=setup.get('seed'))
        self.remoteHeld = 0
        self.remotePressed = 0
        self.lastSent = -1
        self.sendTimer = 0
        self.lastSnap = None

    async def run(self):
        """Devolve 'done' (fim da luta), 'menu' (saiu) ou None (fechou o jogo)."""
        music('mkt', 0.25)
        acc = 0.0
        last = time.perf_counter()
        while True:
            now = time.perf_counter()
            acc += now - last
            last = now
            if acc > STEP * MAX_STEPS:
                acc = STEP * MAX_STEPS
            self.hub.poll()
            if self.hub.quit:
                self._bye()
                return None
            # pausa (só fora do online)
            for group, action in self.hub.menu:
                if action in ('back', 'start') and group in ('kb',) or action == 'start':
                    if self.mode in ('host', 'guest'):
                        choice = await self.leaveMenu()
                    else:
                        choice = await self.pauseMenu()
                    last = time.perf_counter()
                    acc = 0.0
                    if choice is None:
                        return None
                    if choice == 'quit':
                        self._bye()
                        music('intro', 0.5)
                        return 'menu'
                    break

            if self.mode == 'guest':
                r = self._guestFrame()
            else:
                r = None
                steps = 0
                while acc >= STEP:
                    acc -= STEP
                    steps += 1
                    r = self._tick()
                    if r:
                        break
                if self.lastSnap is not None:
                    self.renderer.draw(self.lastSnap, steps)
                    self.lastSnap['ev'] = []
            if r:
                if r == 'lost':
                    await self.message('CONNECTION LOST')
                    music('intro', 0.5)
                    return 'menu'
                music('intro', 0.5)
                return 'done'
            pygame.display.flip()
            await asyncio.sleep(0)

    # ------------------------------------------------------------ local/host
    def _tick(self):
        m = self.match
        helds = []
        for i in range(2):
            p = self.players[i]
            if p is not None:
                helds.append(p.read())
            elif self.cpu is not None:
                helds.append(self.cpu.think(m, m.fighters[i]))
            else:
                helds.append(self.remoteHeld)
        if self.mode == 'host':
            for msg in self.net.recv():
                if msg.get('t') == 'in':
                    h = int(msg.get('h', 0))
                    self.remotePressed |= int(msg.get('p', 0)) | (h & ~self.remoteHeld)
                    self.remoteHeld = h
                elif msg.get('t') == 'bye':
                    return 'lost'
            helds[1] = self.remoteHeld
            m.fighters[1].pending |= self.remotePressed
            self.remotePressed = 0
            self.net.poll()
            if self.net.state in ('closed', 'error'):
                return 'lost'
        m.step(helds)
        snap = m.snapshot()
        if self.lastSnap is not None and self.lastSnap.get('ev'):
            snap['ev'] = self.lastSnap['ev'] + snap['ev']  # eventos de ticks sem desenho
        self.lastSnap = snap
        if self.mode == 'host':
            self.net.send({'t': 's', 's': snap})
        if m.finished:
            if self.mode == 'host':
                self.net.send({'t': 'end'})
            return 'done'
        return None

    # ------------------------------------------------------------ convidado
    def _guestFrame(self):
        net = self.net
        net.poll()
        held = self.players[1].read()
        self.sendTimer -= 1
        if held != self.lastSent or self.sendTimer <= 0:
            pressed = held & ~(self.lastSent if self.lastSent >= 0 else 0)
            net.send({'t': 'in', 'h': held, 'p': pressed})
            self.lastSent = held
            self.sendTimer = 10
        snaps = []
        for msg in net.recv():
            t = msg.get('t')
            if t == 's':
                snaps.append(msg['s'])
            elif t == 'end':
                return 'done'
            elif t == 'bye':
                return 'lost'
        if net.state in ('closed', 'error'):
            return 'lost'
        if snaps:
            for s in snaps[:-1]:
                self.renderer.handleEvents(s.get('ev', ()), s['g'])
            self.lastSnap = snaps[-1]
        if self.lastSnap is not None:
            self.renderer.draw(self.lastSnap, len(snaps))
            self.lastSnap['ev'] = []
        else:
            self.screen.fill((0, 0, 0))
            ui.text(self.screen, 'WAITING FOR HOST...', 28, (400, 230))
        return None

    def _bye(self):
        if self.net is not None:
            try:
                self.net.send({'t': 'bye'})
            except Exception:
                pass

    # ------------------------------------------------------------ menus
    async def pauseMenu(self):
        pygame.mixer.music.pause()
        frozen = self.screen.copy()
        options = ['RESUME', 'MOVE LIST', 'QUIT TO MENU']
        sel = 0
        showMoves = False
        while True:
            self.hub.poll()
            if self.hub.quit:
                return None
            for group, action in self.hub.menu:
                if showMoves:
                    if action in ('back', 'ok', 'start'):
                        showMoves = False
                        assets.playSound('back')
                    continue
                if action in ('up', 'down'):
                    sel = (sel + (1 if action == 'down' else -1)) % len(options)
                    assets.playSound('selection')
                elif action == 'start' or (action == 'back'):
                    pygame.mixer.music.unpause()
                    self._waitRelease()
                    return 'resume'
                elif action == 'ok':
                    if sel == 0:
                        pygame.mixer.music.unpause()
                        self._waitRelease()
                        return 'resume'
                    if sel == 1:
                        showMoves = True
                        assets.playSound('selection')
                    if sel == 2:
                        assets.playSound('back')
                        pygame.mixer.music.stop()
                        return 'quit'
            self.screen.blit(frozen, (0, 0))
            ui.dim(self.screen, 225 if showMoves else 160)
            if showMoves:
                drawMoveList(self.screen, [characters.ROSTER[i] for i in self.setup['chars']])
            else:
                ui.text(self.screen, 'PAUSED', 40, (400, 120), (255, 200, 60), outline=True)
                for i, label in enumerate(options):
                    ui.text(self.screen, label, 34, (400, 200 + i * 60), ui.RED if i == sel else ui.WHITE)
            pygame.display.flip()
            await asyncio.sleep(1 / 30)

    async def leaveMenu(self):
        # online não pausa: só pergunta se quer sair (a luta continua)
        options = ['KEEP FIGHTING', 'LEAVE MATCH']
        sel = 0
        while True:
            self.hub.poll()
            if self.hub.quit:
                return None
            for group, action in self.hub.menu:
                if action in ('up', 'down'):
                    sel = 1 - sel
                elif action in ('back', 'start'):
                    return 'resume'
                elif action == 'ok':
                    return 'resume' if sel == 0 else 'quit'
            # a simulação/recepção segue rodando por baixo
            if self.mode == 'guest':
                if self._guestFrame():
                    return 'quit'
            else:
                r = self._tick()
                if self.lastSnap is not None:
                    self.renderer.draw(self.lastSnap)
                    self.lastSnap['ev'] = []
                if r:
                    return 'quit'
            ui.dim(self.screen, 140)
            for i, label in enumerate(options):
                ui.text(self.screen, label, 32, (400, 200 + i * 60), ui.RED if i == sel else ui.WHITE)
            pygame.display.flip()
            await asyncio.sleep(1 / 60)

    def _waitRelease(self):
        for p in self.players:
            if p is not None:
                p.read()

    async def message(self, msg, seconds=2.0):
        end = time.perf_counter() + seconds
        while time.perf_counter() < end:
            self.hub.poll()
            self.screen.fill((0, 0, 0))
            ui.text(self.screen, msg, 36, (400, 220), ui.RED)
            pygame.display.flip()
            await asyncio.sleep(1 / 30)


MOVE_HELP = [
    ('JAB / HIGH PUNCH', 'LP / HP'),
    ('LOW / HIGH KICK', 'LK / HK'),
    ('UPPERCUT', 'DOWN + HP'),
    ('SWEEP', 'DOWN + HK'),
    ('JUMP KICK / PUNCH', 'IN THE AIR: LK/HK  LP/HP'),
    ('BLOCK (LOW)', 'BLOCK  (DOWN + BLOCK)'),
    ('COMBO', 'HIT, THEN ATTACK AGAIN'),
]


def drawMoveList(screen, chars):
    ui.text(screen, 'MOVE LIST', 34, (400, 30), (255, 200, 60), outline=True)
    y = 80
    for name, keys in MOVE_HELP:
        ui.text(screen, name, 16, (230, y), ui.WHITE)
        ui.text(screen, keys, 16, (570, y), ui.GRAY)
        y += 20
    y += 8
    seen = []
    for c in chars:
        if c in seen:
            continue
        seen.append(c)
        ui.text(screen, c.name, 22, (400, y), c.color, outline=True)
        y += 26
        ui.text(screen, '%s: DOWN, FWD + LP  (OR SPECIAL)' % c.specialName, 15, (400, y))
        y += 19
        ui.text(screen, '%s: DOWN, BACK + LK  (OR BACK + SPECIAL)' % c.special2Name, 15, (400, y))
        y += 19
        for (_, name), keys in zip(c.extra, ('BACK, FWD + HP  (OR DOWN + SPECIAL)',
                                             'FWD, BACK + HK  (OR FWD + SPECIAL)')):
            ui.text(screen, '%s: %s' % (name, keys), 15, (400, y))
            y += 19
        ui.text(screen, 'FATALITY - %s: FATALITY BUTTON (FINISH HIM)' % c.fatalityName, 15, (400, y), (255, 120, 120))
        y += 24
    ui.text(screen, 'ESC: BACK', 14, (400, 470), ui.GRAY)
