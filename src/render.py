# Desenho da luta a partir do snapshot (local, contra CPU ou online).
import math
import random
import pygame
import assets
import characters
import fatalfx
import ui

W, H = 800, 500
ICE_LAUNCH_TICKS = 3   # ticks por frame da rajada saindo da mão (frames 0-4)
ICE_BURST = 7          # primeiro frame do estilhaço (7-11)
ICE_BURST_TICKS = 4
ATTACK_SHEETS = {'Apunch', 'Bpunch', 'Cpunch', 'Dpunch', 'Akick', 'Bkick', 'Ckick', 'Dkick',
                 'Ekick', 'Epunch', 'Special', 'Special2', 'Fkick', 'fatality'}
# projéteis do MK2 desenhados com os sprites do jogo (tools/mk2_sprites.py):
# kind -> (sheet de efeito, nº de frames, frames saindo, frames voando, frames do impacto)
FX = {
    'fireball': ('fireball', 8, (0, 1), (2, 3), (4, 5, 6, 7)),
    'fan': ('fan', 10, (), tuple(range(10)), ()),
    'fanlift': ('fanwind', 8, (0, 1, 2), (3, 4, 5, 6, 7), ()),
    'lightning': ('lightning', 10, (0, 1, 2), (3, 4, 5, 6), (7, 8, 9)),
}
FX_TICKS = 4         # ticks por frame dos efeitos acima


class Particle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'life', 'max', 'size', 'color', 'kind', 'rest')

    def __init__(self, x, y, vx, vy, life, size, color, kind):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.life = self.max = life
        self.size, self.color, self.kind = size, color, kind
        self.rest = False


class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.world = pygame.Surface((W, H))
        self.particles = []
        self.stage = None
        self.bg = None
        self.shownLife = [100.0, 100.0]
        self.toasty = 0
        self.rng = random.Random(1)
        self._glows = {}
        self.label = None  # texto extra no HUD (ex.: "ONLINE")
        self.steps = 1
        self.bursts = []   # estilhaços da rajada de gelo: [x, y, facing, t]
        self.impacts = []  # explosões dos projéteis do MK2: [kind, x, y, facing, t]
        self.heads = []    # cabeça voando (fatality da Kitana): [surf, x, y, vx, vy, t]

    # ------------------------------------------------------------ eventos
    def handleEvents(self, events, ground):
        for ev in events:
            kind = ev[0]
            if kind == 'snd':
                assets.playSound(ev[1], ev[2] if len(ev) > 2 else 1.0)
            elif kind == 'music':
                if ev[1] == 'stop':
                    pygame.mixer.music.stop()
            elif kind == 'blood':
                _, x, y, d, n, seed = ev
                rng = random.Random(seed)
                for _ in range(min(n, 60)):
                    self.particles.append(Particle(
                        x, y, d * rng.uniform(0.5, 5.5) + rng.uniform(-1.5, 1.5), -rng.uniform(1.5, 7.5),
                        rng.randint(40, 80), rng.randint(2, 4),
                        rng.choice(((170, 0, 0), (210, 20, 20), (120, 0, 0))), 'blood'))
            elif kind == 'spark':
                _, x, y, t = ev
                col = (255, 240, 150) if t != 2 else (200, 240, 255)
                for i in range(10):
                    a = i / 10 * 6.283
                    self.particles.append(Particle(x, y, math.cos(a) * 4, math.sin(a) * 4, 10, 2, col, 'spark'))
            elif kind in ('tele', 'land'):
                _, x, y, idx = ev
                for i in range(8 if kind == 'tele' else 5):
                    a = i / 8 * 6.283
                    self.particles.append(Particle(
                        x + math.cos(a) * 10, ground - y - (60 if kind == 'tele' else 4),
                        math.cos(a) * 1.6, math.sin(a) * (1.2 if kind == 'tele' else 0.4) - 0.3,
                        26, 14 if kind == 'tele' else 10, (150, 150, 160) if kind == 'tele' else (150, 120, 90), 'puff'))
            elif kind == 'toasty':
                self.toasty = 70
            elif kind == 'head':  # recorta a cabeça do frame da vítima e a joga para longe do golpe
                _, ci, alt, sheetName, frame, x, facing, dirX, seed = ev
                sh = assets.sheet(characters.ROSTER[ci], sheetName, bool(alt))
                img = sh.frame(frame, facing)
                body = img.get_bounding_rect()
                cut = pygame.Rect(body.x, body.y, body.w, min(body.h, 30))
                left = x - sh.anchor(facing)
                self.heads.append([img.subsurface(cut).copy(), left + cut.x, ground - sh.h + cut.y,
                                   dirX * 3.2, -8.5, 0])
            elif kind == 'pfx':  # projétil explodiu (acertou, foi defendido ou trombou)
                _, pk, x, y, facing = ev
                if pk == 'ice':
                    self.bursts.append([x, y, facing, 0])
                elif pk in FX and FX[pk][4]:
                    self.impacts.append([pk, x, y, facing, 0])
                else:
                    import match as M
                    col = M.PROJ.get(pk, {}).get('color', (255, 240, 150))
                    for i in range(14):
                        a = i / 14 * 6.283
                        self.particles.append(Particle(x, y, math.cos(a) * 3.5, math.sin(a) * 3.5,
                                                       14, 2, col, 'spark'))
        if len(self.particles) > 500:
            self.particles = self.particles[-500:]

    def _updateParticles(self, ground):
        alive = []
        for p in self.particles:
            p.life -= 1
            if p.life <= 0:
                continue
            if p.kind == 'blood':
                if not p.rest:
                    p.x += p.vx
                    p.y += p.vy
                    p.vy += 0.42
                    if p.y >= ground:
                        p.y = ground - 1
                        p.rest = True
                        p.life = 160
            elif p.kind == 'spark':
                p.x += p.vx
                p.y += p.vy
            else:
                p.x += p.vx
                p.y += p.vy
                p.size += 0.5
            alive.append(p)
        self.particles = alive

    def _drawParticles(self, surf):
        for p in self.particles:
            if p.kind == 'blood':
                if p.rest:
                    pygame.draw.ellipse(surf, p.color, (int(p.x) - p.size, int(p.y) - 1, p.size * 3, 3))
                else:
                    pygame.draw.rect(surf, p.color, (int(p.x), int(p.y), p.size, p.size))
            elif p.kind == 'spark':
                pygame.draw.line(surf, p.color, (int(p.x), int(p.y)), (int(p.x - p.vx * 2), int(p.y - p.vy * 2)), 2)
            else:
                self._glow(surf, p.x, p.y, int(p.size), p.color, int(160 * p.life / p.max))

    def _glow(self, surf, x, y, r, color, alpha):
        r = max(1, int(r))
        key = (r, color)
        s = self._glows.get(key)
        if s is None:
            s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, color + (255,), (r, r), r)
            self._glows[key] = s
            if len(self._glows) > 300:
                self._glows.clear()
        s.set_alpha(max(0, min(255, alpha)))
        surf.blit(s, (int(x - r), int(y - r)))

    # ------------------------------------------------------------ desenho
    def setStage(self, stage):
        if stage != self.stage:
            self.stage = stage
            self.bg = assets.image('res/Background/Scenario%d.png' % stage, alpha=False)
            self.particles = []

    def draw(self, snap, steps=1):
        """Desenha o snapshot; `steps` = ticks de simulação desde o último desenho
        (partículas e animações do HUD andam no ritmo da luta, não do monitor)."""
        self.setStage(snap['st'])
        ground = snap['g']
        self.ground = ground
        if snap['ph'] == 'intro' and snap['pt'] <= 2:
            self.heads = []
        self.handleEvents(snap.get('ev', ()), ground)
        self.steps = steps
        for _ in range(steps):
            self._updateParticles(ground)
            for b in self.bursts:
                b[3] += 1
        self.bursts = [b for b in self.bursts if b[3] < ICE_BURST_TICKS * 5]
        for _ in range(steps):
            for b in self.impacts:
                b[4] += 1
            for hd in self.heads:
                hd[5] += 1
                if hd[2] < ground - hd[0].get_height():
                    hd[1] += hd[3]
                    hd[2] = min(ground - hd[0].get_height(), hd[2] + hd[4])
                    hd[4] += 0.45
        self.impacts = [b for b in self.impacts if b[4] < FX_TICKS * len(FX[b[0]][4])]
        world = self.world
        world.blit(self.bg, (0, 0))

        fz = snap['fx']
        fighters = snap['f']
        # sombras
        for f in fighters:
            if f[7] & 2:
                continue
            sw = max(30, 80 - f[5] // 3)
            self._shadow(world, f[4], ground, sw)
        # quem está atacando é desenhado por cima
        order = sorted(range(2), key=lambda i: 1 if fighters[i][2] in ATTACK_SHEETS else 0)
        for i in order:
            self._drawFighter(world, fighters[i], ground, snap['t'])
        if fz:
            kind, t, wi, li, seed, vs, vf, vfacing, vx = fz
            lf = fighters[li]
            char = characters.ROSTER[lf[0]]
            sh = assets.sheet(char, vs, bool(lf[1]))
            surf = sh.frame(vf, vfacing)
            left = vx - sh.anchor(vfacing)
            top = ground - sh.h
            fatalfx.draw(world, kind, t, surf, left, top, ground, seed, fighters[wi][4])
        for p in snap['p']:
            self._drawProjectile(world, p, fighters, ground, snap['t'])
        for x, y, facing, t in self.bursts:
            self._drawIce(world, ICE_BURST + min(4, t // ICE_BURST_TICKS), x, y, facing)
        for kind, x, y, facing, t in self.impacts:
            frames = FX[kind][4]
            self._drawFx(world, kind, frames[min(len(frames) - 1, t // FX_TICKS)], x, y, facing, center=True)
        for img, x, y, vx, vy, t in self.heads:
            rot = img if y >= self.ground - img.get_height() else pygame.transform.rotate(img, -t * 14 * (1 if vx > 0 else -1))
            world.blit(rot, (int(x), int(y)))
        self._drawParticles(world)

        shake = snap.get('sh', 0)
        ox = oy = 0
        if shake:
            ox = self.rng.randint(-4, 4)
            oy = self.rng.randint(-3, 3)
        self.screen.fill((0, 0, 0))
        self.screen.blit(world, (ox, oy))
        self._hud(snap)

    def _shadow(self, surf, x, ground, w):
        key = ('shadow', w)
        s = self._glows.get(key)
        if s is None:
            s = pygame.Surface((w, 12), pygame.SRCALPHA)
            pygame.draw.ellipse(s, (0, 0, 0, 90), (0, 0, w, 12))
            self._glows[key] = s
        surf.blit(s, (x - w // 2, ground - 7))

    def _drawFighter(self, surf, f, ground, tick):
        ci, alt, sheetName, frame, x, y, facing, flags, ax, life = f
        if flags & 2:
            return
        char = characters.ROSTER[ci]
        sh = assets.sheet(char, sheetName, bool(alt))
        if sh is None:
            return
        img = sh.frame(frame, facing)
        if ax:
            anchor = ax if facing > 0 else sh.w - ax
        else:
            anchor = sh.anchor(facing)
        if flags & 1:  # congelado
            img = assets.tinted(img, 'frozen', (110, 170, 230), pygame.BLEND_RGB_MULT)
            img = assets.tinted(img, 'frozen2', (70, 110, 140), pygame.BLEND_RGB_ADD)
        elif flags & 4:  # piscada branca do impacto
            img = assets.tinted(img, 'flash', (110, 110, 110), pygame.BLEND_RGB_ADD)
        alpha = None
        if char.ghost:
            alpha = 120 + int(60 * math.sin(tick * 0.15))
        if flags & 8:
            alpha = 90 if tick % 4 < 2 else 200
        if alpha is not None:
            img = assets.tinted(img, 'ghost', (0, 0, 0, 0), pygame.BLEND_RGBA_ADD)
            img.set_alpha(alpha)
        surf.blit(img, (x - anchor, ground - y - sh.h))

    def _drawProjectile(self, surf, p, fighters, ground, tick):
        kind, x, y, facing, age, owner, length = p
        sy = ground - y
        if kind == 'spear':
            o = fighters[owner]
            hx0 = o[4] + facing * 40
            pts = []
            n = 24
            for i in range(n + 1):
                fx = hx0 + (x - hx0) * i / n
                amp = 6 * math.sin(i / n * math.pi) * (1 if length < 300 else 0.4)
                pts.append((fx, sy + math.sin(i * 1.3 + age * 0.9) * amp))
            if len(pts) > 1:
                pygame.draw.lines(surf, (150, 110, 80), False, pts, 2)
            head = assets.image('res/sprites/spearhead.png')
            if facing < 0:
                head = pygame.transform.flip(head, True, False)
            surf.blit(head, (x - (head.get_width() if facing > 0 else 0), sy - head.get_height() // 2))
            return
        if kind in FX:
            _, n, launch, fly, _ = FX[kind]
            k = age // FX_TICKS
            frame = launch[k] if k < len(launch) else fly[(k - len(launch)) % len(fly)]
            self._drawFx(surf, kind, frame, x, sy, facing)
            return
        if kind == 'ice':
            if age < ICE_LAUNCH_TICKS * 5:   # saindo da mão
                frame = age // ICE_LAUNCH_TICKS
            else:                            # voando (alterna os dois rastros)
                frame = 5 + (age // 5) % 2
            self._drawIce(surf, frame, x, sy, facing)
            return
        import match as M
        cfg = M.PROJ[kind]
        r = cfg['r']
        col, core = cfg['color'], cfg['core']
        for k in range(1, 5):  # rastro
            self._glow(surf, x - facing * k * 9, sy, r - k * 2, col, 110 - k * 22)
        if kind == 'rock':
            ang = age * 0.3
            pts = [(x + math.cos(ang + a) * r * (0.8 + 0.2 * ((a * 7) % 1)), sy + math.sin(ang + a) * r)
                   for a in (0, 1.1, 2.0, 3.0, 4.1, 5.2)]
            pygame.draw.polygon(surf, col, pts)
            pygame.draw.polygon(surf, core, pts, 2)
            return
        if kind == 'shard':
            pts = [(x + facing * r * 2, sy), (x, sy - r * 0.6), (x - facing * r * 1.2, sy), (x, sy + r * 0.6)]
            self._glow(surf, x, sy, r + 6, col, 90)
            pygame.draw.polygon(surf, core, pts)
            pygame.draw.polygon(surf, col, pts, 2)
            return
        pulse = 2 * math.sin(age * 0.5)
        self._glow(surf, x, sy, r + 7 + pulse, col, 90)
        self._glow(surf, x, sy, r, col, 230)
        self._glow(surf, x, sy, max(3, r // 2), core, 255)
        if kind == 'bolt':
            rng = random.Random(age)
            for _ in range(3):
                a = rng.uniform(0, 6.28)
                pygame.draw.line(surf, (240, 230, 255), (x, sy), (x + math.cos(a) * (r + 10), sy + math.sin(a) * (r + 10)), 2)
        elif kind == 'shadow':
            a = age * 0.6
            pygame.draw.arc(surf, (190, 150, 255), (x - r - 3, sy - r - 3, 2 * r + 6, 2 * r + 6), a, a + 2.5, 3)
        elif kind == 'ice':
            rng = random.Random(age // 2)
            for _ in range(4):
                pygame.draw.rect(surf, (255, 255, 255), (x + rng.randint(-r, r), sy + rng.randint(-r, r), 2, 2))

    def _drawFx(self, surf, kind, frame, x, y, facing, center=False):
        # frames alinhados pela frente (borda direita) e centrados na vertical
        sh = assets.fxSheet(FX[kind][0], FX[kind][1])
        img = sh.frame(frame, facing)
        ax = sh.w // 2 if center else sh.anchor(facing)
        surf.blit(img, (x - ax, y - sh.h // 2))

    def _drawIce(self, surf, frame, x, y, facing):
        # icefx: frames 240x100 com o ponto de referência em (200, 50)
        sh = assets.fxSheet('icefx', 12, 200)
        surf.blit(sh.frame(frame, facing), (x - sh.anchor(facing), y - sh.h // 2))

    # ------------------------------------------------------------ HUD
    def _hud(self, snap):
        s = self.screen
        fs = snap['f']
        for i in range(2):
            life = fs[i][9]
            for _ in range(self.steps):
                if self.shownLife[i] > life:
                    self.shownLife[i] += (life - self.shownLife[i]) * 0.08
                else:
                    self.shownLife[i] = life
            char = characters.ROSTER[fs[i][0]]
            x0 = 30 if i == 0 else 450
            bar = pygame.Rect(x0, 18, 320, 20)
            pygame.draw.rect(s, (0, 0, 0), bar.inflate(6, 6))
            pygame.draw.rect(s, (150, 0, 0), bar)
            def fill(v, color):
                w = int(320 * max(0.0, v) / 100)
                r = pygame.Rect(x0 + (0 if i == 0 else 320 - w), 18, w, 20)
                pygame.draw.rect(s, color, r)
            fill(self.shownLife[i], (240, 200, 40))
            fill(life, (30, 170, 40))
            pygame.draw.rect(s, (230, 230, 230), bar, 2)
            name = char.name
            ui.text(s, name, 18, (x0 + 4 if i == 0 else x0 + 316 - ui.textWidth(name, 18), 44),
                    (255, 255, 255), center=False, outline=True)
            for k in range(snap['w'][i]):  # medalhas de round
                cx = x0 + 300 - k * 22 if i == 0 else x0 + 20 + k * 22
                pygame.draw.circle(s, (0, 0, 0), (cx, 54), 9)
                pygame.draw.circle(s, (230, 180, 30), (cx, 54), 7)
                pygame.draw.circle(s, (160, 20, 20), (cx, 54), 3)
        ui.text(s, '%d' % snap['tm'], 34, (400, 10), (255, 255, 255), outline=True)
        if self.label:
            ui.text(s, self.label, 14, (400, 52), (200, 200, 200), outline=True)
        self._banners(snap)
        if self.toasty > 0:
            self.toasty = max(0, self.toasty - self.steps)
            k = min(1.0, (70 - self.toasty) / 8, self.toasty / 8)
            x = int(800 - 150 * k)
            pygame.draw.rect(s, (0, 0, 0), (x, 400, 150, 70))
            ui.text(s, 'TOASTY!', 26, (x + 75, 420), (255, 120, 20), outline=True)

    def _banners(self, snap):
        s = self.screen
        ph, pt = snap['ph'], snap['pt']
        fs = snap['f']
        def name(i):
            return characters.ROSTER[fs[i][0]].name
        if ph == 'intro':
            if pt < 70:
                ui.text(s, 'ROUND %d' % snap['r'], 54, (400, 170), (255, 200, 60), outline=True)
            else:
                k = min(1.0, (pt - 70) / 8)
                ui.text(s, 'FIGHT!', int(40 + 40 * k), (400, 200 - int(20 * k)), (230, 30, 30), outline=True)
        elif ph == 'finish':
            if (pt // 18) % 4 != 3:
                img = assets.image('res/finishhim.png')
                img = pygame.transform.scale(img, (img.get_width() * 3 // 2, img.get_height() * 3 // 2))
                s.blit(img, (400 - img.get_width() // 2, 140))
            if pt < 200:
                ui.text(s, 'FATALITY: F / NUMPAD 6 / L2  (or  DOWN, FWD + HP)', 14, (400, 205), (220, 220, 220), outline=True)
        elif ph == 'ko':
            if snap['rw'] < 0:
                if pt > 10:
                    ui.text(s, 'DRAW', 50, (400, 160), (255, 255, 255), outline=True)
            elif pt >= 80:
                ui.text(s, '%s WINS' % name(snap['rw']), 44, (400, 150), (255, 255, 255), outline=True)
                if snap['fl'] and pt >= 150:
                    ui.text(s, 'FLAWLESS VICTORY', 30, (400, 205), (255, 200, 60), outline=True)
        elif ph == 'over':
            w = snap['mw']
            if snap['fd']:
                ui.text(s, '%s WINS' % name(w), 44, (400, 130), (255, 255, 255), outline=True)
                img = assets.image('res/fatality.png')
                img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
                s.blit(img, (400 - img.get_width() // 2, 190))
                fn = snap.get('fn', '')
                title = characters.FATALITY_TITLES.get(fn) or characters.ROSTER[fs[w][0]].fatalityName
                ui.text(s, title, 20, (400, 245), (255, 200, 60), outline=True)
            elif pt >= 60:
                ui.text(s, '%s WINS' % name(w), 44, (400, 150), (255, 255, 255), outline=True)
                if snap['fl'] and pt >= 140:
                    ui.text(s, 'FLAWLESS VICTORY', 30, (400, 205), (255, 200, 60), outline=True)
            if pt > 200 and (pt // 25) % 2 == 0:
                ui.text(s, 'PRESS ANY ATTACK BUTTON', 18, (400, 440), (230, 230, 230), outline=True)
