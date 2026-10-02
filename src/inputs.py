# Entrada unificada: teclado (2 layouts), controles (Bluetooth/USB: DualSense,
# DualShock, Xbox... via SDL GameController no desktop e Gamepad API no
# navegador), CPU e jogador remoto produzem o MESMO formato: um bitmask de
# botões segurados. O lutador não sabe de onde vem o comando.
import sys
import pygame

UP, DOWN, LEFT, RIGHT = 1, 2, 4, 8
LP, HP, LK, HK = 16, 32, 64, 128
BLOCK, SPECIAL, FATAL, START = 256, 512, 1024, 2048
BACK = 4096
ATTACKS = LP | HP | LK | HK
DIRS = UP | DOWN | LEFT | RIGHT

WEB = sys.platform == 'emscripten'

# --- teclado --------------------------------------------------------------
# P1: WASD + J N K M L U F (layout original)
# P2: setas + numpad 1 4 2 5 3 0 6, com aliases de notebook ; . ' / , o p
KEYMAP_P1 = {
    UP: [pygame.K_w], DOWN: [pygame.K_s], LEFT: [pygame.K_a], RIGHT: [pygame.K_d],
    LP: [pygame.K_j], HP: [pygame.K_n], LK: [pygame.K_k], HK: [pygame.K_m],
    SPECIAL: [pygame.K_l], BLOCK: [pygame.K_u], FATAL: [pygame.K_f],
}
KEYMAP_P2 = {
    UP: [pygame.K_UP], DOWN: [pygame.K_DOWN], LEFT: [pygame.K_LEFT], RIGHT: [pygame.K_RIGHT],
    LP: [pygame.K_KP1, pygame.K_SEMICOLON], HP: [pygame.K_KP4, pygame.K_PERIOD],
    LK: [pygame.K_KP2, pygame.K_QUOTE], HK: [pygame.K_KP5, pygame.K_SLASH],
    SPECIAL: [pygame.K_KP3, pygame.K_COMMA], BLOCK: [pygame.K_KP0, pygame.K_o],
    FATAL: [pygame.K_KP6, pygame.K_p],
}

# teclas de navegação dos menus -> (grupo, ação)
MENU_KEYS = {
    pygame.K_w: ('kb1', 'up'), pygame.K_s: ('kb1', 'down'),
    pygame.K_a: ('kb1', 'left'), pygame.K_d: ('kb1', 'right'),
    pygame.K_j: ('kb1', 'ok'), pygame.K_SPACE: ('kb1', 'ok'), pygame.K_f: ('kb1', 'ok'),
    pygame.K_UP: ('kb2', 'up'), pygame.K_DOWN: ('kb2', 'down'),
    pygame.K_LEFT: ('kb2', 'left'), pygame.K_RIGHT: ('kb2', 'right'),
    pygame.K_RETURN: ('kb2', 'ok'), pygame.K_KP_ENTER: ('kb2', 'ok'),
    pygame.K_KP1: ('kb2', 'ok'), pygame.K_SEMICOLON: ('kb2', 'ok'),
    pygame.K_ESCAPE: ('kb', 'back'), pygame.K_BACKSPACE: ('kb', 'back'),
}

# --- controle (layout "standard" da Gamepad API do navegador) ------------
# 0 Cruz/A  1 Bola/B  2 Quadrado/X  3 Triângulo/Y  4 L1/LB  5 R1/RB
# 6 L2/LT   7 R2/RT   8 Share/Back  9 Options/Start  12-15 direcional
STD_BUTTONS = {
    2: LP, 3: HP, 0: LK, 1: HK, 5: BLOCK, 7: BLOCK, 4: SPECIAL, 6: FATAL,
    9: START, 8: BACK, 12: UP, 13: DOWN, 14: LEFT, 15: RIGHT,
}
STICK_DEADZONE = 0.5


class PadState:
    def __init__(self, ident, name):
        self.ident = ident
        self.name = name
        self.held = 0


class Hub:
    """Lê teclado e controles uma vez por frame e distribui para os jogadores."""

    def __init__(self):
        self.pads = []          # PadState, na ordem em que foram conectados
        self._keys = None
        self._sdlCtl = None     # módulo pygame._sdl2.controller (desktop)
        self._desktopPads = {}  # instance id -> objeto controller/joystick
        self._prevPad = {}
        self.menu = []          # eventos de menu deste frame: (grupo, ação)
        self.text = []          # caracteres digitados (código de sala)
        self.keys = []          # teclas apertadas neste frame
        self.taps = []          # toques/cliques na tela neste frame: (x, y) em coords do jogo
        self.muteRect = None    # botão de som (menus): toque nele liga/desliga e não vira toque de menu
        self.quit = False
        self._scanTimer = 0
        if not WEB:
            self._initDesktopPads()

    # ---------------- desktop: SDL GameController/Joystick ----------------
    def _initDesktopPads(self):
        try:
            from pygame._sdl2 import controller
            controller.init()
            self._sdlCtl = controller
        except Exception:
            self._sdlCtl = None
        try:
            pygame.joystick.init()
        except Exception:
            pass
        self._scanDesktop()

    def _scanDesktop(self):
        try:
            count = pygame.joystick.get_count()
        except Exception:
            return
        seen = set()
        for i in range(count):
            try:
                if self._sdlCtl is not None and self._sdlCtl.is_controller(i):
                    dev = self._sdlCtl.Controller(i)
                    key = ('c', dev.as_joystick().get_instance_id())
                    name = dev.name
                else:
                    dev = pygame.joystick.Joystick(i)
                    dev.init()
                    key = ('j', dev.get_instance_id())
                    name = dev.get_name()
            except Exception:
                continue
            seen.add(key)
            if key not in self._desktopPads:
                self._desktopPads[key] = dev
                self.pads.append(PadState(key, name))
                print('gamepad connected:', name)
        for key in list(self._desktopPads):
            if key not in seen:
                del self._desktopPads[key]
                self.pads = [p for p in self.pads if p.ident != key]

    def _readDesktopPad(self, key, dev):
        held = 0
        if key[0] == 'c':
            btn = dev.get_button
            mapping = {
                pygame.CONTROLLER_BUTTON_X: LP, pygame.CONTROLLER_BUTTON_Y: HP,
                pygame.CONTROLLER_BUTTON_A: LK, pygame.CONTROLLER_BUTTON_B: HK,
                pygame.CONTROLLER_BUTTON_RIGHTSHOULDER: BLOCK,
                pygame.CONTROLLER_BUTTON_LEFTSHOULDER: SPECIAL,
                pygame.CONTROLLER_BUTTON_START: START, pygame.CONTROLLER_BUTTON_BACK: BACK,
                pygame.CONTROLLER_BUTTON_DPAD_UP: UP, pygame.CONTROLLER_BUTTON_DPAD_DOWN: DOWN,
                pygame.CONTROLLER_BUTTON_DPAD_LEFT: LEFT, pygame.CONTROLLER_BUTTON_DPAD_RIGHT: RIGHT,
            }
            for b, bit in mapping.items():
                if btn(b):
                    held |= bit
            ax = dev.get_axis(pygame.CONTROLLER_AXIS_LEFTX) / 32767
            ay = dev.get_axis(pygame.CONTROLLER_AXIS_LEFTY) / 32767
            if dev.get_axis(pygame.CONTROLLER_AXIS_TRIGGERRIGHT) > 16000:
                held |= BLOCK
            if dev.get_axis(pygame.CONTROLLER_AXIS_TRIGGERLEFT) > 16000:
                held |= FATAL
        else:  # joystick genérico: assume layout tipo Xbox do SDL
            raw = {0: LK, 1: HK, 2: LP, 3: HP, 4: SPECIAL, 5: BLOCK, 6: BACK, 7: START}
            for b, bit in raw.items():
                if b < dev.get_numbuttons() and dev.get_button(b):
                    held |= bit
            if dev.get_numhats() > 0:
                hx, hy = dev.get_hat(0)
                held |= (LEFT if hx < 0 else RIGHT if hx > 0 else 0)
                held |= (UP if hy > 0 else DOWN if hy < 0 else 0)
            ax = dev.get_axis(0) if dev.get_numaxes() > 0 else 0
            ay = dev.get_axis(1) if dev.get_numaxes() > 1 else 0
        held |= _stick(ax, ay)
        return held

    # ---------------- navegador: Gamepad API via JS (web.tmpl) -----------
    def _readWebPads(self):
        try:
            import platform
            raw = str(platform.window.pkPads())
        except Exception:
            return
        present = []
        for entry in raw.split('|'):
            if not entry:
                continue
            parts = entry.split(':', 4)
            if len(parts) < 4:
                continue
            ident = ('w', parts[0])
            present.append(ident)
            buttons = int(parts[1] or 0)
            axes = [float(a) for a in parts[2].split(',') if a]
            held = 0
            for b, bit in STD_BUTTONS.items():
                if buttons & (1 << b):
                    held |= bit
            if len(axes) >= 2:
                held |= _stick(axes[0], axes[1])
            pad = next((p for p in self.pads if p.ident == ident), None)
            if pad is None:
                pad = PadState(ident, parts[4] if len(parts) > 4 else 'gamepad')
                self.pads.append(pad)
                print('gamepad connected:', pad.name)
            pad.held = held
        self.pads = [p for p in self.pads if p.ident in present]

    # ---------------- frame ----------------
    def poll(self):
        """Processa a fila de eventos do pygame. Chamar 1x por frame."""
        self.menu = []
        self.text = []
        self.keys = []
        self.taps = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit = True
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.muteRect is not None and self.muteRect.collidepoint(event.pos):
                    import assets
                    assets.setMuted(not assets.muted)
                    continue
                self.taps.append(event.pos)   # toque no celular chega como clique
            elif event.type == pygame.KEYDOWN:
                self.keys.append(event.key)
                if event.key in MENU_KEYS:
                    self.menu.append(MENU_KEYS[event.key])
                if event.unicode and event.unicode.isprintable():
                    self.text.append(event.unicode)
                if event.key == pygame.K_BACKSPACE:
                    self.text.append('\b')
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.text.append('\n')
                if event.key == pygame.K_v and (event.mod & pygame.KMOD_CTRL or event.mod & pygame.KMOD_META):
                    self.text.append('\x16')  # colar
            elif event.type in (getattr(pygame, 'CONTROLLERDEVICEADDED', -1),
                                getattr(pygame, 'CONTROLLERDEVICEREMOVED', -1),
                                pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
                self._scanTimer = 0
        self._keys = pygame.key.get_pressed()

        if WEB:
            self._readWebPads()
        else:
            self._scanTimer -= 1
            if self._scanTimer <= 0:
                self._scanTimer = 90
                self._scanDesktop()
            for pad in self.pads:
                dev = self._desktopPads.get(pad.ident)
                if dev is not None:
                    try:
                        pad.held = self._readDesktopPad(pad.ident, dev)
                    except Exception:
                        pad.held = 0

        # eventos de menu dos controles (borda de subida, com auto-repetição)
        for i, pad in enumerate(self.pads):
            prev, timer = self._prevPad.get(pad.ident, (0, 0))
            group = 'pad%d' % i
            edges = pad.held & ~prev
            if pad.held & DIRS and pad.held & DIRS == prev & DIRS:
                timer += 1
                if timer > 18 and timer % 6 == 0:
                    edges |= pad.held & DIRS
            else:
                timer = 0
            for bit, action in ((UP, 'up'), (DOWN, 'down'), (LEFT, 'left'), (RIGHT, 'right'),
                                (LK, 'ok'), (LP, 'ok'), (START, 'start'), (HK, 'back'), (BACK, 'back')):
                if edges & bit:
                    self.menu.append((group, action))
            self._prevPad[pad.ident] = (pad.held, timer)

    def keyboard(self, keymap):
        if self._keys is None:
            return 0
        held = 0
        for bit, keys in keymap.items():
            for k in keys:
                if self._keys[k]:
                    held |= bit
                    break
        return held

    def padHeld(self, index):
        if 0 <= index < len(self.pads):
            return self.pads[index].held
        return 0

    def keyHeld(self, key):
        return bool(self._keys and self._keys[key])


def _stick(ax, ay):
    held = 0
    if ax < -STICK_DEADZONE:
        held |= LEFT
    elif ax > STICK_DEADZONE:
        held |= RIGHT
    if ay < -STICK_DEADZONE:
        held |= UP
    elif ay > STICK_DEADZONE:
        held |= DOWN
    return held


class Player:
    """Fonte de comandos de um lutador: junta teclado(s) e controle(s)."""

    def __init__(self, hub, keymaps=(), pads=()):
        self.hub = hub
        self.keymaps = list(keymaps)
        self.pads = list(pads)
        self.held = 0

    def read(self):
        held = 0
        for km in self.keymaps:
            held |= self.hub.keyboard(km)
        for p in self.pads:
            held |= self.hub.padHeld(p)
        # esquerda+direita/cima+baixo ao mesmo tempo se anulam
        if held & LEFT and held & RIGHT:
            held &= ~(LEFT | RIGHT)
        if held & UP and held & DOWN:
            held &= ~UP
        self.held = held
        return held


def menuGroupsFor(player, mode):
    """Grupos de eventos de menu que controlam o jogador `player` (0/1)."""
    if mode != 'versus':
        return None  # qualquer fonte
    return ('kb1', 'pad0') if player == 0 else ('kb2', 'pad1')
