# Desenho da luta a partir do snapshot (local, contra CPU ou online).
import math
import random
import pygame
import assets
import characters
import fatalfx
import ui

W, H = 800, 500
ATTACK_SHEETS = {'Apunch', 'Bpunch', 'Cpunch', 'Dpunch', 'Akick', 'Bkick', 'Ckick', 'Dkick',
                 'Ekick', 'Epunch', 'Special', 'Special2', 'Fkick', 'fatality'}
# projéteis do MK2 desenhados com os sprites do jogo (tools/mk2_sprites.py):
# kind -> (sheet de efeito, nº de frames, frames saindo, frames voando, frames do impacto)
FX = {
    'ice': ('ice', 9, (0, 1, 2), (3, 4), (5, 6, 7, 8)),
    'fireball': ('fireball', 8, (0, 1), (2, 3), (4, 5, 6, 7)),
    'fan': ('fan', 10, (), tuple(range(10)), ()),
    'fanlift': ('fanwind', 8, (0, 1, 2), (3, 4, 5, 6, 7), ()),
    'lightning': ('lightning', 10, (0, 1, 2), (3, 4, 5, 6), (7, 8, 9)),
    'hat': ('hat', 3, (), (0, 1, 2), ()),
    'greenball': ('greenball', 9, (0, 1, 2), (3, 4, 5, 6), (7, 8)),
    'spark': ('spark', 11, (0, 1, 2, 3), (4, 5), (6, 7, 8, 9, 10)),
    'sai': ('sai', 9, (0, 1), (2, 3), (4, 5, 6, 7, 8)),
    'skull': ('skull', 11, (0, 1, 2, 3), (4, 5, 6), (7, 8, 9, 10)),
    'wave': ('wave', 5, (0, 1), (2,), (3, 4)),
    'lowfireball': ('fireball', 8, (0, 1), (2, 3), (4, 5, 6, 7)),
    'groundice': ('icepuddle', 9, (0, 1), (2,), (3, 4, 5, 6, 7, 8)),   # poça de gelo deslizando no chão
}
GROUND_FX = {'firerise': ('firerise', 6, 7)}   # efeitos que saem do chão: (sheet, frames, ticks/frame)
SHADOW_KICK = (90, 230, 60)   # rastro verde da shadow kick do Johnny Cage
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
        self.noMeter = [0, 0]   # pisca as cargas de quem tentou especial sem carga
        self.rng = random.Random(1)
        self._glows = {}
        self.label = None  # texto extra no HUD (ex.: "ONLINE")
        self.steps = 1
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
            elif kind == 'nometer':
                self.noMeter[ev[1]] = 24
            elif kind == 'head':  # recorta a cabeça do frame da vítima e a joga para longe do golpe
                _, ci, alt, sheetName, frame, x, facing, dirX, seed = ev
                sh = assets.sheet(characters.ROSTER[ci], sheetName, bool(alt))
                img = sh.frame(frame, facing)
                body = img.get_bounding_rect()
                cut = pygame.Rect(body.x, body.y, body.w, min(body.h, 30))
                left = x - sh.anchor(facing)
                self.heads.append([img.subsurface(cut).copy(), left + cut.x, ground - sh.gh + cut.y,
                                   dirX * 3.2, -8.5, 0])
            elif kind == 'pfx':  # projétil explodiu (acertou, foi defendido ou trombou)
                _, pk, x, y, facing = ev
                if pk in FX and FX[pk][4]:
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
            top = ground - sh.gh
            fatalfx.draw(world, kind, t, surf, left, top, ground, seed, fighters[wi][4])
        for p in snap['p']:
            self._drawProjectile(world, p, fighters, ground, snap['t'])
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
        ci, alt, sheetName, frame, x, y, facing, flags, ax, life = f[:10]
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
        if sheetName == 'Fkick' and char.special2 == 'shadowkick':  # sombras verdes atrás do chute
            ghost = assets.tinted(img, 'shadowkick', SHADOW_KICK, pygame.BLEND_RGB_MULT)
            for k, a in ((3, 70), (2, 110), (1, 150)):
                g = assets.tinted(ghost, ('sk', k), (0, 0, 0, 0), pygame.BLEND_RGBA_ADD)
                g.set_alpha(a)
                surf.blit(g, (x - anchor - facing * 26 * k, ground - y - sh.gh))
        alpha = None
        if flags & 8:
            alpha = 90 if tick % 4 < 2 else 200
        if alpha is not None:
            img = assets.tinted(img, 'ghost', (0, 0, 0, 0), pygame.BLEND_RGBA_ADD)
            img.set_alpha(alpha)
        surf.blit(img, (x - anchor, ground - y - sh.gh))

    def _drawProjectile(self, surf, p, fighters, ground, tick):
        kind, x, y, facing, age, owner, length, x0 = p
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
            sh = assets.fxSheet('spearhead', 1)   # kunai da ponta (MK2), a frente é a referência
            surf.blit(sh.frame(0, facing), (x - sh.anchor(facing), sy - sh.h // 2))
            return
        if kind in GROUND_FX:
            name, n, step = GROUND_FX[kind]
            self._drawGroundFx(surf, name, n, min(n - 1, age // step), x, ground, facing)
            return
        if kind == 'quake':  # onda roxa correndo rente ao chão
            for k in range(5):
                self._glow(surf, x - facing * k * 12, ground - 6 - (k % 2) * 4, 12 - k * 2, (190, 90, 255), 180 - k * 30)
            return
        if kind in FX:
            _, n, launch, fly, _ = FX[kind]
            k = age // FX_TICKS
            frame = launch[k] if k < len(launch) else fly[(k - len(launch)) % len(fly)]
            # o rastro não passa para trás da mão de quem jogou (sai "de dentro" da mão)
            clip = surf.get_clip()
            if facing > 0:
                surf.set_clip(pygame.Rect(x0, 0, W - x0, H).clip(clip))
            else:
                surf.set_clip(pygame.Rect(0, 0, x0, H).clip(clip))
            self._drawFx(surf, kind, frame, x, sy, facing)
            surf.set_clip(clip)
            return
        import match as M   # projétil sem sprite: bola de luz na cor dele
        cfg = M.PROJ[kind]
        r = cfg['r']
        col, core = cfg['color'], cfg['core']
        for k in range(1, 5):  # rastro
            self._glow(surf, x - facing * k * 9, sy, r - k * 2, col, 110 - k * 22)
        pulse = 2 * math.sin(age * 0.5)
        self._glow(surf, x, sy, r + 7 + pulse, col, 90)
        self._glow(surf, x, sy, r, col, 230)
        self._glow(surf, x, sy, max(3, r // 2), core, 255)

    def _drawGroundFx(self, surf, name, n, frame, cx, ground, facing):
        # pelo contorno do desenho: centrado em x, com a base no chão
        sh = assets.fxSheet(name, n)
        img = sh.frame(frame, facing)
        br = img.get_bounding_rect()
        surf.blit(img, (int(cx - br.centerx), int(ground - br.bottom)))

    def _drawFx(self, surf, kind, frame, x, y, facing, center=False):
        # frames alinhados pela frente (borda direita) e centrados na vertical
        sh = assets.fxSheet(FX[kind][0], FX[kind][1])
        img = sh.frame(frame, facing)
        ax = sh.w // 2 if center else sh.anchor(facing)
        surf.blit(img, (x - ax, y - sh.h // 2))

    def _meter(self, s, x0, i, meter):
        """Cargas de especial: 3 barrinhas sob o nome; a que está recarregando enche aos poucos."""
        flash = self.noMeter[i] > 0 and (self.noMeter[i] // 4) % 2 == 0
        for k in range(3):
            x = x0 + 4 + k * 34 if i == 0 else x0 + 316 - 30 - k * 34
            r = pygame.Rect(x, 66, 30, 8)
            pygame.draw.rect(s, (0, 0, 0), r.inflate(4, 4))
            pygame.draw.rect(s, (200, 30, 30) if flash else (30, 30, 60), r)
            v = max(0.0, min(1.0, meter - k))
            if v > 0:
                w = int(30 * v)
                fr = pygame.Rect(x if i == 0 else x + 30 - w, 66, w, 8)
                pygame.draw.rect(s, (80, 170, 255) if v >= 1 else (50, 90, 150), fr)
        self.noMeter[i] = max(0, self.noMeter[i] - self.steps)

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
            self._meter(s, x0, i, fs[i][10] if len(fs[i]) > 10 else 3)
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
            # rosto do Dan Forden (sprite do MK2, sem fundo) entra pelo canto inferior direito
            img = assets.image('res/sprites/toasty.png')
            k = min(1.0, (70 - self.toasty) / 8, self.toasty / 8)
            x = int(800 - (img.get_width() + 12) * k)
            s.blit(img, (x, 500 - 8 - img.get_height()))

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
            loser = 1 - snap['mw'] if snap['mw'] >= 0 else 0
            if (pt // 18) % 4 != 3 and characters.ROSTER[fs[loser][0]].female:
                ui.text(s, 'FINISH HER!', 50, (400, 158), (230, 30, 30), outline=True)
            elif (pt // 18) % 4 != 3:
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
                if snap['fl'] and pt >= 200:
                    ui.text(s, 'FLAWLESS VICTORY', 30, (400, 205), (255, 200, 60), outline=True)
        elif ph == 'over':
            w = snap['mw']
            if snap['fd']:
                ui.text(s, '%s WINS' % name(w), 44, (400, 130), (255, 255, 255), outline=True)
                img = assets.image('res/fatality.png')
                img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
                s.blit(img, (400 - img.get_width() // 2, 190))
                title = characters.ROSTER[fs[w][0]].fatalityName
                ui.text(s, title, 20, (400, 245), (255, 200, 60), outline=True)
            elif pt >= 60:
                ui.text(s, '%s WINS' % name(w), 44, (400, 150), (255, 255, 255), outline=True)
                if snap['fl'] and pt >= 185:
                    ui.text(s, 'FLAWLESS VICTORY', 30, (400, 205), (255, 200, 60), outline=True)
            if pt > 200 and (pt // 25) % 2 == 0:
                ui.text(s, 'PRESS ANY ATTACK BUTTON', 18, (400, 440), (230, 230, 230), outline=True)
