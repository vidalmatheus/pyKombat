# Menus: máquina de estados assíncrona (cada tela cede o controle com
# asyncio.sleep — exigência do navegador/pygbag) que devolve o PRÓXIMO estado.
#   title -> mode -> select -> stage -> fight -> select ...
#   mode -> host/join -> netselect -> (host escolhe cenário) -> fight -> netselect ...
import asyncio
import math
import random
import time
import pygame
import ai
import assets
import characters
import fight
import fighter
import inputs
import net
import prefs
import ui
from inputs import Player, KEYMAP_P1, KEYMAP_P2

MENU_DT = 1 / 60   # menus a 60 quadros/s (seletores deslizam sem engasgar)
ROSTER = characters.ROSTER
COLS = 6   # duas linhas de lutadores


class MenuFacade:
    def __init__(self, screen='title'):
        self.screen = screen

    async def run(self, game):
        hub = inputs.Hub()
        level = prefs.get('cpuLevel', 'NORMAL')   # última dificuldade escolhida
        if level not in ai.LEVEL_NAMES:
            level = 'NORMAL'
        ctx = {'mode': 'cpu', 'cpuLevel': level, 'chars': [0, 1], 'stage': 9, 'net': None,
               'autoJoin': net.roomFromUrl()}
        state = self.screen
        if ctx['autoJoin']:
            state = 'join'
        while state is not None:
            print('menu:', state)
            if state == 'title':
                state = await TitleMenu(game, hub, ctx).run()
            elif state == 'mode':
                state = await ModeMenu(game, hub, ctx).run()
            elif state == 'controls':  # aberto pela tela inicial (OPTIONS)
                state = await ControlsScreen(game, hub).run(back='title')
            elif state == 'modecontrols':  # aberto pelo menu de modos
                state = await ControlsScreen(game, hub).run(back='mode')
            elif state == 'select':
                state = await CharacterSelect(game, hub, ctx).run()
            elif state == 'stage':
                state = await StageSelect(game, hub, ctx).run()
            elif state == 'fight':
                state = await runFight(game, hub, ctx)
            elif state == 'host':
                state = await HostScreen(game, hub, ctx).run()
            elif state == 'join':
                state = await JoinScreen(game, hub, ctx).run()
            elif state == 'netselect':
                state = await CharacterSelect(game, hub, ctx).run()
            elif state == 'netstage':
                state = await NetStage(game, hub, ctx).run()
            else:
                state = 'title'


def localPlayers(hub, ctx):
    if ctx['mode'] == 'versus':
        return [Player(hub, [KEYMAP_P1], [0]), Player(hub, [KEYMAP_P2], [1])]
    anyone = Player(hub, [KEYMAP_P1, KEYMAP_P2], [0, 1, 2, 3])
    if ctx['mode'] == 'guest':
        return [None, anyone]
    return [anyone, None]


async def runFight(game, hub, ctx):
    setup = {'mode': ctx['mode'], 'chars': list(ctx['chars']), 'stage': ctx['stage'],
             'seed': ctx.get('seed'), 'cpuLevel': ctx['cpuLevel'], 'net': ctx['net'],
             'players': localPlayers(hub, ctx)}
    r = await fight.Fight(game, hub, setup).run()
    if r is None:
        return None
    if ctx['mode'] in ('host', 'guest'):
        if r == 'done':
            return 'netselect'
        closeNet(ctx)
        return 'mode'
    return 'select' if r == 'done' else 'mode'


def closeNet(ctx):
    if ctx.get('net') is not None:
        try:
            ctx['net'].send({'t': 'bye'})
        except Exception:
            pass
        ctx['net'].close()
        ctx['net'] = None


def background(surf, stage=9, alpha=170):
    surf.blit(assets.image('res/Background/Scenario%d.png' % stage, alpha=False), (0, 0))
    ui.dim(surf, alpha)


def logo(surf, y=18, width=520):
    img = assets.image('res/Background/PyKombatLogo.png')
    h = int(img.get_height() * width / img.get_width())
    surf.blit(assets.scaledImage('res/Background/PyKombatLogo.png', (width, h)), (400 - width // 2, y))


class Screen:
    def __init__(self, game, hub, ctx=None):
        self.game = game
        self.surf = game.getDisplay()
        self.hub = hub
        self.ctx = ctx

    async def frame(self):
        pygame.display.flip()
        # dorme só o que falta para o próximo quadro (o desenho já gastou parte dele)
        now = time.perf_counter()
        last = getattr(self, '_lastFrame', now - MENU_DT)
        await asyncio.sleep(max(0.0, MENU_DT - (now - last)))
        self._lastFrame = time.perf_counter()


class TitleMenu(Screen):
    async def run(self):
        sel = self.ctx.pop('titleSel', 0)
        while True:
            self.hub.poll()
            if self.hub.quit:
                return None
            for group, action in self.hub.menu:
                if action in ('up', 'down'):
                    sel = 1 - sel
                    assets.playSound('selection')
                elif action in ('ok', 'start'):
                    assets.playSound('start' if sel == 0 else 'options')
                    self.ctx['titleSel'] = sel  # ao voltar, mantém START/OPTIONS marcado
                    return 'mode' if sel == 0 else 'controls'
            img = 'res/Background/MainMenu01.png' if sel == 0 else 'res/Background/MainMenu02.png'
            self.surf.blit(assets.image(img, alpha=False), (0, 0))
            await self.frame()


class ModeMenu(Screen):
    ITEMS = ['1 PLAYER VS CPU', '2 PLAYERS', 'ONLINE: CREATE ROOM', 'ONLINE: JOIN ROOM', 'CONTROLS']

    async def run(self):
        ctx = self.ctx
        sel = ctx.pop('modeSel', None)
        if sel is None:
            sel = {'cpu': 0, 'versus': 1, 'host': 2, 'guest': 3}.get(ctx['mode'], 0)
        level = ai.LEVEL_NAMES.index(ctx['cpuLevel'])
        while True:
            self.hub.poll()
            if self.hub.quit:
                return None
            for group, action in self.hub.menu:
                if action in ('up', 'down'):
                    sel = (sel + (1 if action == 'down' else -1)) % len(self.ITEMS)
                    assets.playSound('selection')
                elif action in ('left', 'right') and sel == 0:
                    level = (level + (1 if action == 'right' else -1)) % 3
                    ctx['cpuLevel'] = ai.LEVEL_NAMES[level]
                    prefs.put('cpuLevel', ctx['cpuLevel'])
                    assets.playSound('selection')
                elif action == 'back':
                    assets.playSound('back')
                    return 'title'
                elif action in ('ok', 'start'):
                    assets.playSound('start')
                    if sel == 0:
                        ctx['mode'] = 'cpu'
                        return 'select'
                    if sel == 1:
                        ctx['mode'] = 'versus'
                        return 'select'
                    if sel == 2:
                        return 'host'
                    if sel == 3:
                        return 'join'
                    ctx['modeSel'] = sel  # volta para este menu com CONTROLS marcado
                    return 'modecontrols'
            s = self.surf
            background(s, 9, 150)
            logo(s)
            for i, label in enumerate(self.ITEMS):
                if i == 0:
                    label = '1 PLAYER VS CPU   < %s >' % ctx['cpuLevel']
                ui.text(s, label, 30, (400, 150 + i * 52), ui.RED if i == sel else ui.WHITE)
            pads = [p.name for p in self.hub.pads]
            hint = 'GAMEPADS: ' + (', '.join(pads)[:70] if pads else 'NONE (PAIR ONE VIA BLUETOOTH AND PRESS A BUTTON)')
            ui.text(s, hint.upper(), 13, (400, 438), ui.GRAY)
            ui.backHint(s, 'ARROWS / D-PAD: MOVE   ENTER / CROSS: SELECT   ESC / CIRCLE: BACK')
            await self.frame()


class ControlsScreen(Screen):
    ROWS = [
        ('', 'PLAYER 1', 'PLAYER 2', 'GAMEPAD'),
        ('MOVE', 'W A S D', 'ARROWS', 'D-PAD / STICK'),
        ('LOW PUNCH', 'J', 'NUM1 / ;', 'SQUARE / X'),
        ('HIGH PUNCH', 'N', 'NUM4 / .', 'TRIANGLE / Y'),
        ('LOW KICK', 'K', "NUM2 / '", 'CROSS / A'),
        ('HIGH KICK', 'M', 'NUM5 / /', 'CIRCLE / B'),
        ('BLOCK', 'U', 'NUM0 / O', 'R1 R2 / RB RT'),
        ('SPECIAL', 'L', 'NUM3 / ,', 'L1 / LB'),
        ('FATALITY', 'F', 'NUM6 / P', 'L2 / LT'),
        ('PAUSE', 'ESC', 'ESC', 'OPTIONS / START'),
    ]

    async def run(self, back='title'):
        while True:
            self.hub.poll()
            if self.hub.quit:
                return None
            for group, action in self.hub.menu:
                if action in ('back', 'ok', 'start'):
                    assets.playSound('back')
                    return back
            s = self.surf
            background(s, 3, 185)
            ui.text(s, 'CONTROLS', 40, (400, 14), (255, 200, 60), outline=True)
            for r, row in enumerate(self.ROWS):
                y = 70 + r * 30
                for c, cell in enumerate(row):
                    x = (110, 300, 480, 660)[c]
                    color = (255, 200, 60) if r == 0 or c == 0 else ui.WHITE
                    ui.text(s, cell, 17, (x, y), color)
            y = 380
            for line in ('SPECIAL 1: DOWN, FORWARD + LOW PUNCH  -  SPECIAL 2: DOWN, BACK + LOW KICK',
                         'SPECIAL 3: BACK, FORWARD + HIGH PUNCH  -  SPECIAL 4: FORWARD, BACK + HIGH KICK',
                         '(OR SPECIAL BUTTON ALONE / WITH BACK / DOWN / FORWARD)',
                         'UPPERCUT: DOWN + HIGH PUNCH    SWEEP: DOWN + HIGH KICK',
                         'FINISH HIM: PRESS FATALITY  (OR DOWN, FORWARD + HIGH PUNCH)'):
                ui.text(s, line, 14, (400, y), (220, 220, 220))
                y += 21
            ui.backHint(s)
            await self.frame()


class CharacterSelect(Screen):
    """Seleção de lutadores (local, contra CPU e online)."""

    async def run(self):
        ctx = self.ctx
        mode = ctx['mode']
        online = mode in ('host', 'guest')
        me = 1 if mode == 'guest' else 0
        cursor = list(ctx['chars'])
        ready = [False, False]
        n = len(ROSTER)
        self.selPos = [None, None]   # posição animada dos seletores (deslizam suave)
        t0 = time.perf_counter()
        link = ctx.get('net')
        lastSent = None
        while True:
            self.hub.poll()
            if self.hub.quit:
                closeNet(ctx)
                return None
            tick = int((time.perf_counter() - t0) * 60)
            for group, action in self.hub.menu:
                # quem controla qual cursor
                if mode == 'versus':
                    who = 0 if group in ('kb1', 'pad0') else 1 if group in ('kb2', 'pad1') else None
                    if who is None and action == 'back':
                        who = 0 if not ready[1] else 1
                elif mode == 'cpu':
                    who = 1 if ready[0] else 0   # depois do seu lutador, você escolhe o da CPU
                else:
                    who = me
                if who is None:
                    continue
                if action == 'back':
                    if ready[who]:
                        ready[who] = False
                        assets.playSound('back')
                        continue
                    if mode == 'cpu' and who == 1:  # volta a escolher o próprio lutador
                        ready[0] = False
                        assets.playSound('back')
                        continue
                    assets.playSound('back')
                    if online:
                        closeNet(ctx)
                    return 'mode'
                if ready[who]:
                    continue
                c = cursor[who]
                if action == 'left':
                    c = c - 1 if c % COLS else c + COLS - 1
                elif action == 'right':
                    c = c + 1 if c % COLS != COLS - 1 else c - COLS + 1
                elif action in ('up', 'down'):
                    c = (c + COLS) % n
                elif action in ('ok', 'start'):
                    ready[who] = True
                    assets.playSound(characters.ROSTER[cursor[who]].nameSound)   # locutor diz o nome
                    if mode == 'cpu' and who == 0 and cursor[1] == cursor[0]:
                        cursor[1] = (cursor[0] + 1) % n   # sugere outro lutador p/ a CPU
                if c != cursor[who]:
                    cursor[who] = c
                    assets.playSound('selection')

            # R: lutador aleatório para o seletor ativo (o seu ou o da CPU)
            if pygame.K_r in self.hub.keys and not online:
                who = (1 if ready[0] else 0) if mode == 'cpu' else 0
                if not ready[who]:
                    cursor[who] = random.choice([i for i in range(n) if i != cursor[who]])
                    assets.playSound('selection')

            if online:
                link.poll()
                if link.state in ('closed', 'error'):
                    closeNet(ctx)
                    await message(self, 'CONNECTION LOST')
                    return 'mode'
                state = (cursor[me], ready[me])
                if state != lastSent or tick % 30 == 0:
                    link.send({'t': 'sel', 'c': cursor[me], 'r': ready[me]})
                    lastSent = state
                for msg in link.recv():
                    if msg.get('t') == 'sel':
                        cursor[1 - me] = int(msg['c']) % n
                        if msg['r'] and not ready[1 - me]:
                            assets.playSound(characters.ROSTER[cursor[1 - me]].nameSound)
                        ready[1 - me] = bool(msg['r'])
                    elif msg.get('t') == 'bye':
                        closeNet(ctx)
                        await message(self, 'OPPONENT LEFT')
                        return 'mode'
                    elif msg.get('t') == 'start' and mode == 'guest':
                        applyStart(ctx, msg)
                        return 'fight'

            self.draw(cursor, ready, tick, mode, me)
            await self.frame()
            if ready[0] and ready[1]:
                ctx['chars'] = list(cursor)
                await asyncio.sleep(0.5)
                if mode == 'guest':
                    return 'netstage'
                return 'netstage' if mode == 'host' else 'stage'

    def draw(self, cursor, ready, tick, mode, me):
        s = self.surf
        background(s, 6, 190)
        pickingCpu = mode == 'cpu' and ready[0] and not ready[1]
        ui.text(s, 'CHOOSE YOUR OPPONENT' if pickingCpu else 'CHOOSE YOUR FIGHTER', 34, (400, 12),
                (255, 200, 60), outline=True)
        size = 88
        gap = 8
        x0 = 400 - (COLS * size + (COLS - 1) * gap) // 2
        y0 = 62
        for i, c in enumerate(ROSTER):
            x = x0 + (i % COLS) * (size + gap)
            y = y0 + (i // COLS) * (size + gap)
            pygame.draw.rect(s, (30, 10, 10), (x - 2, y - 2, size + 4, size + 4))
            s.blit(assets.portrait(c, size=(size, size)), (x, y))
        # seletores: deslizam até o lutador escolhido e "respiram" devagar (sem piscar).
        # A suavização usa o tempo real, então o movimento é igual a 30 ou 60 quadros/s.
        now = time.perf_counter()
        dt = min(0.1, now - getattr(self, '_easeT', now))
        self._easeT = now
        ease = 1 - math.exp(-dt * 14)
        for p, base in ((0, (220, 40, 40)), (1, (60, 120, 255))):
            if mode == 'cpu' and p == 1 and not ready[0]:
                continue  # o da CPU só aparece depois que você escolhe o seu
            tx = x0 + (cursor[p] % COLS) * (size + gap)
            ty = y0 + (cursor[p] // COLS) * (size + gap)
            pos = self.selPos[p]
            if pos is None:
                pos = [float(tx), float(ty)]
            pos[0] += (tx - pos[0]) * ease
            pos[1] += (ty - pos[1]) * ease
            self.selPos[p] = pos
            if ready[p]:
                col = tuple(min(255, v + 60) for v in base)
            else:
                k = 0.5 + 0.5 * math.sin(tick * 0.08)
                col = tuple(int(v + (255 - v) * 0.35 * k) for v in base)
            off = 0 if p == 0 else 4
            rect = pygame.Rect(int(pos[0]) - 3 + off, int(pos[1]) - 3 + off, size + 6 - 2 * off, size + 6 - 2 * off)
            pygame.draw.rect(s, col, rect, 3)
        labels = {'cpu': ('1P', 'CPU'), 'versus': ('1P', '2P'), 'host': ('YOU', 'FRIEND'),
                  'guest': ('FRIEND', 'YOU')}[mode]
        for p in range(2):
            if mode == 'cpu' and p == 1 and not ready[0]:
                ui.text(s, labels[1], 18, (695, 268), (90, 140, 255), outline=True)
                ui.text(s, '?', 60, (695, 330), (90, 140, 255), outline=True)
                continue  # o lutador da CPU só aparece quando for escolhê-lo
            c = ROSTER[cursor[p]]
            alt = p == 1 and cursor[0] == cursor[1]
            facing = 1 if p == 0 else -1
            if ready[p]:
                sh = assets.sheet(c, 'win', alt)
                img = sh.frame(min(sh.n - 1, (tick // 8) % 40), facing)
                ax = sh.anchor(facing)
            else:
                sh = assets.sheet(c, 'dance', alt)
                seq = fighter.anim(c.base, 'idle')['seq']
                img = sh.frame(seq[(tick // 6) % len(seq)], facing)
                ax = sh.anchor(facing)
            cx = 105 if p == 0 else 695
            s.blit(img, (cx - ax, 470 - sh.gh))
            col = (230, 60, 60) if p == 0 else (90, 140, 255)
            ui.text(s, labels[p], 18, (cx, 268), col, outline=True)
            ui.text(s, c.name, 24, (cx, 290), c.color, outline=True)
            if ready[p]:
                ui.text(s, 'READY', 18, (cx, 318), (255, 255, 255), outline=True)
        # info do lutador sob o cursor ativo (do jogador local / da CPU sendo escolhida)
        c = ROSTER[cursor[me if mode in ('host', 'guest') else (1 if pickingCpu else 0)]]
        ui.panel(s, pygame.Rect(232, 262, 336, 150), 150)
        ui.text(s, c.name, 24, (400, 270), c.color)
        moves = [(c.specialName, 'D,F + LP'), (c.special2Name, 'D,B + LK')] + \
            [(n, k) for (_, n), k in zip(c.extra, ('B,F + HP', 'F,B + HK'))]
        for i, (name, keys) in enumerate(moves):   # especiais e o comando de cada um
            ui.text(s, '%s  %s' % (name, keys), 13, (400, 300 + i * 19), ui.WHITE if i < 2 else (255, 220, 140))
        ui.text(s, 'FATALITY: ' + c.fatalityName, 14, (400, 386), (255, 120, 120))
        if mode == 'versus':
            ui.text(s, 'P1: WASD + J      P2: ARROWS + ENTER', 13, (400, 425), ui.GRAY)
        elif mode == 'cpu':
            ui.text(s, 'PICK THE CPU FIGHTER  -  R: RANDOM' if pickingCpu else 'R: RANDOM', 13,
                    (400, 425), ui.GRAY)
        ui.backHint(s)


class StageSelect(Screen):
    # grade 3x3 de cenários: {1..8, 9=aleatório} (arte original)
    moveMap = {
        1: {"down": 4, "right": 2}, 2: {"down": 5, "right": 3, "left": 1}, 3: {"down": 6, "left": 2},
        4: {"down": 7, "right": 5, "up": 1}, 5: {"down": 8, "right": 6, "left": 4, "up": 2},
        6: {"down": 9, "left": 5, "up": 3}, 7: {"right": 8, "up": 4}, 8: {"right": 9, "left": 7, "up": 5},
        9: {"left": 8, "up": 6},
    }

    async def run(self, online=False):
        ctx = self.ctx
        stage = 9
        while True:
            self.hub.poll()
            if self.hub.quit:
                return None
            for group, action in self.hub.menu:
                if action in ('ok', 'start'):
                    assets.playSound('start')   # o "Fight!" é falado na abertura do round
                    ctx['stage'] = stage if stage != 9 else random.randint(1, 8)
                    ctx['seed'] = random.randrange(1 << 30)
                    return 'fight'
                if action == 'back':
                    assets.playSound('back')
                    return 'select'
                if action in self.moveMap[stage]:
                    stage = self.moveMap[stage][action]
                    assets.playSound('selection')
            if online:
                link = ctx['net']
                link.poll()
                for msg in link.recv():
                    if msg.get('t') == 'bye':
                        return 'lost'
                if link.state in ('closed', 'error'):
                    return 'lost'
            self.surf.blit(assets.image('res/Background/ChoosingScenario/ChooseScenario0%d.png' % stage,
                                        alpha=False), (0, 0))
            ui.backHint(self.surf)
            await self.frame()


class NetStage(Screen):
    """Online: o host escolhe o cenário; o convidado espera."""

    async def run(self):
        ctx = self.ctx
        link = ctx['net']
        if ctx['mode'] == 'host':
            r = await StageSelect(self.game, self.hub, ctx).run(online=True)
            if r == 'fight':
                link.send({'t': 'start', 'chars': ctx['chars'], 'stage': ctx['stage'], 'seed': ctx['seed']})
                return 'fight'
            if r == 'select':
                link.send({'t': 'sel', 'c': ctx['chars'][0], 'r': False})
                return 'netselect'
            closeNet(ctx)
            if r == 'lost':
                await message(self, 'CONNECTION LOST')
                return 'mode'
            return r
        while True:
            self.hub.poll()
            if self.hub.quit:
                closeNet(ctx)
                return None
            for group, action in self.hub.menu:
                if action == 'back':
                    closeNet(ctx)
                    return 'mode'
            link.poll()
            for msg in link.recv():
                t = msg.get('t')
                if t == 'start':
                    applyStart(ctx, msg)
                    return 'fight'
                if t == 'sel' and not msg.get('r'):
                    return 'netselect'
                if t == 'bye':
                    closeNet(ctx)
                    await message(self, 'OPPONENT LEFT')
                    return 'mode'
            if link.state in ('closed', 'error'):
                closeNet(ctx)
                await message(self, 'CONNECTION LOST')
                return 'mode'
            background(self.surf, 4, 180)
            ui.text(self.surf, 'YOUR FRIEND IS CHOOSING THE ARENA...', 24, (400, 220))
            await self.frame()


def applyStart(ctx, msg):
    ctx['chars'] = [int(c) for c in msg['chars']]
    ctx['stage'] = int(msg['stage'])
    ctx['seed'] = int(msg['seed'])


async def message(screen, text, seconds=2.0):
    end = time.perf_counter() + seconds
    while time.perf_counter() < end:
        screen.hub.poll()
        screen.surf.fill((0, 0, 0))
        ui.text(screen.surf, text, 34, (400, 220), ui.RED)
        pygame.display.flip()
        await asyncio.sleep(MENU_DT)


class HostScreen(Screen):
    async def run(self):
        ctx = self.ctx
        closeNet(ctx)
        link = net.transport()
        ctx['net'] = link
        ctx['mode'] = 'host'
        code = net.newCode()
        link.host(code)
        copied = 0
        while True:
            self.hub.poll()
            if self.hub.quit:
                closeNet(ctx)
                return None
            for group, action in self.hub.menu:
                if action == 'back':
                    assets.playSound('back')
                    closeNet(ctx)
                    ctx['mode'] = 'cpu'
                    return 'mode'
            for ch in self.hub.text:
                if ch.lower() == 'c' and link.copy(link.shareUrl() or link.code):
                    copied = 60
            link.poll()
            if link.state == 'open':
                for msg in link.recv():
                    pass
                link.send({'t': 'hello', 'v': 1})
                assets.playSound('start')
                return 'netselect'
            s = self.surf
            background(s, 7, 180)
            ui.text(s, 'ONLINE ROOM', 40, (400, 40), (255, 200, 60), outline=True)
            if link.state == 'error':
                ui.text(s, 'COULD NOT CREATE THE ROOM', 24, (400, 170), ui.RED)
                ui.text(s, link.error.upper()[:60], 14, (400, 210), ui.GRAY)
            else:
                ui.text(s, 'SHARE THIS CODE WITH YOUR FRIEND', 20, (400, 120))
                ui.text(s, link.code or '...', 64, (400, 160), (255, 255, 255), outline=True)
                url = link.shareUrl()
                if url:
                    ui.text(s, 'OR SEND THE LINK:', 16, (400, 260), ui.GRAY)
                    pygame.font.init()
                    img = pygame.font.SysFont(None, 22).render(url, True, (200, 220, 255))
                    s.blit(img, (400 - img.get_width() // 2, 285))
                    ui.text(s, 'PRESS C TO COPY THE LINK' if not copied else 'LINK COPIED!', 16, (400, 315),
                            (255, 200, 60) if copied else ui.GRAY)
                dots = '.' * (1 + int(time.perf_counter() * 2) % 3)
                status = 'WAITING FOR YOUR FRIEND' + dots if link.state == 'waiting' else 'CREATING ROOM' + dots
                ui.text(s, status, 22, (400, 370))
            copied = max(0, copied - 1)
            ui.backHint(s, 'ESC: CANCEL')
            await self.frame()


class JoinScreen(Screen):
    async def run(self):
        ctx = self.ctx
        closeNet(ctx)
        code = ctx.pop('autoJoin', '') or ''
        ctx['autoJoin'] = ''
        link = None
        connecting = bool(code)
        if connecting:
            link = self._connect(code)
        while True:
            self.hub.poll()
            if self.hub.quit:
                closeNet(ctx)
                return None
            for ch in self.hub.text:
                if ch == '\b':
                    if connecting:
                        closeNet(ctx)
                        connecting = False
                    elif code:
                        code = code[:-1]
                    else:
                        assets.playSound('back')
                        ctx['mode'] = 'cpu'
                        return 'mode'
                elif ch == '\n':
                    if code and not connecting:
                        link = self._connect(code)
                        connecting = True
                elif not connecting and len(code) < 21 and (ch.isalnum() or ch in '.:'):
                    code += ch.upper() if net.WEB else ch
            cancel = pygame.K_ESCAPE in self.hub.keys or any(
                action == 'back' and group != 'kb' for group, action in self.hub.menu)
            if cancel:
                assets.playSound('back')
                closeNet(ctx)
                ctx['mode'] = 'cpu'
                return 'mode'
            if connecting:
                link.poll()
                if link.state == 'open':
                    ctx['mode'] = 'guest'
                    assets.playSound('start')
                    return 'netselect'
            s = self.surf
            background(s, 2, 180)
            ui.text(s, 'JOIN A ROOM', 40, (400, 40), (255, 200, 60), outline=True)
            ui.text(s, 'TYPE THE ROOM CODE' if net.WEB else 'TYPE THE HOST ADDRESS (IP:PORT)', 20, (400, 130))
            box = pygame.Rect(200, 170, 400, 80)
            ui.panel(s, box, 200, ui.RED if not connecting else (255, 200, 60))
            caret = '_' if not connecting and int(time.perf_counter() * 2) % 2 else ''
            if net.WEB:
                ui.text(s, code + caret, 52, (400, 180))
            else:
                img = pygame.font.SysFont(None, 52).render(code + caret, True, (255, 255, 255))
                s.blit(img, (400 - img.get_width() // 2, 192))
            if connecting:
                if link.state == 'error':
                    msg = 'ROOM NOT FOUND' if 'unavailable' in link.error else 'CONNECTION ERROR'
                    ui.text(s, msg, 24, (400, 290), ui.RED)
                    ui.text(s, 'BACKSPACE: EDIT CODE', 16, (400, 330), ui.GRAY)
                else:
                    dots = '.' * (1 + int(time.perf_counter() * 2) % 3)
                    ui.text(s, 'CONNECTING' + dots, 24, (400, 290))
            else:
                ui.text(s, 'ENTER: CONNECT', 18, (400, 290), ui.GRAY)
            ui.backHint(s, 'ESC: CANCEL')
            await self.frame()

    def _connect(self, code):
        link = net.transport()
        self.ctx['net'] = link
        link.join(code)
        return link
