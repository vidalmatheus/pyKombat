# pyKombat

![alt text](https://github.com/vidalmatheus/pyKombat/blob/master/res/Background/MainMenu01.png)

![alt text](https://github.com/vidalmatheus/pyKombat/blob/master/res/Screenshot.png)


## Play in the browser 🎮

https://vidalmatheus.github.io/pyKombat/

(no install needed — powered by [pygbag](https://github.com/pygame-web/pygbag)/WebAssembly)

Every pull request also gets its own playable preview at
`https://vidalmatheus.github.io/pyKombat/pr-preview/pr-<number>/` (the link is posted on the PR).


## Game modes

* **1 player vs CPU** — three difficulty levels (EASY / NORMAL / HARD, pick with ← → on the menu).
* **2 players** on the same machine (keyboard and/or two gamepads).
* **Online** — *Create room* shows a 5-letter code and a link; your friend opens the link (or picks
  *Join room* and types the code) and you fight peer-to-peer (WebRTC). On the desktop version the
  "code" is the host's `IP:7777` (LAN or a forwarded port).

Fights are best of 3 rounds with a 99 s timer. Win the deciding round and you get **FINISH HIM** —
press the fatality button (or ↓ → + HP) for your fighter's fatality.


## Fighters

| Fighter | Special 1 (↓ → + LP) | Special 2 (↓ ← + LK) | Fatality |
|---|---|---|---|
| Sub-Zero | Ice blast (freezes) | Slide | Deep freeze |
| Scorpion | Spear ("Get over here!") | Teleport punch | Toasty (fire breath) |
| Liu Kang | Fireball | Flying kick | Dragon bite |
| Kitana | Fan throw | Fan lift | Fan decapitation |
| Raiden | Lightning | Torpedo | Electrocution |
| Kung Lao | Hat throw | Teleport | Hat slice |
| Johnny Cage | Green bolt | Shadow kick | Uppercut decapitation |
| Baraka | Blade spark | Blade fury | Blade decapitation |
| Mileena | Sai throw | Roll | Sai frenzy |
| Jax | Energy wave | Ground smash | Arm rip |
| Shang Tsung | Flaming skull | Ground fire | Soul steal |
| Reptile | Acid spit | Force ball | Tongue lash |

Every fighter uses the Mortal Kombat II (SNES) sprites, specials and fatalities — all 12 playable
MK2 fighters. Specials 3 and 4 (↓ / → + Special, or ← → + HP / → ← + HK) add more MK2 moves, e.g.
Reptile's slide and invisibility. Freezing an
already frozen opponent backfires, just like in MK.


## Controls

| | Player 1 | Player 2 | Gamepad (PS / Xbox) |
|---|---|---|---|
| Move / jump / crouch | W A S D | arrows | D-pad / left stick |
| Low punch | J | Num1 or `;` | □ / X |
| High punch | N | Num4 or `.` | △ / Y |
| Low kick | K | Num2 or `'` | ✕ / A |
| High kick | M | Num5 or `/` | ○ / B |
| Block | U | Num0 or `O` | R1 R2 / RB RT |
| Special | L (hold back for special 2) | Num3 or `,` | L1 / LB |
| Fatality | F | Num6 or `P` | L2 / LT |
| Pause | Esc | Esc | Options / Start |

Moves: ↓ + HP uppercut, ↓ + HK sweep, attack in the air for jump kicks/punches, ↓ + Block blocks
low attacks (sweeps and low kicks go under a standing block). A hit that lands can be chained into
another attack.

**Bluetooth controllers** (DualSense/PS5, DualShock 4, Xbox, ...): pair the controller with your
computer/phone, open the game and press any button — it shows up in the main menu. In 2-player mode
the first gamepad is P1 and the second is P2; in the other modes any gamepad controls you.

**Phone / tablet**: open the game link and turn the phone sideways (it asks you to). The first touch
goes fullscreen in landscape where the browser allows it. On-screen controls: stick on the left,
LP / HP / LK / HK / BLOCK / SPECIAL / FATAL on the right, BACK and PAUSE at the top corners. In
the menus you can also just tap: tap a fighter or arena to highlight it, tap it again to pick it.
`?touch=1` in the URL shows the touch controls on a PC too (`?touch=0` hides them).

Specials cost charges: each fighter has 3 (the bars under the name), refilled over time and when
you get hit — heavier hits refill more.


## Run the game locally:

```
pip install pygame
python main.py
```

## Rebuild the web version:

```
pip install pygbag
./build_web.sh
```

This writes the browser build to `web/` (not committed). GitHub Actions builds and deploys it on
every push to `master` (`.github/workflows/pages.yml`) and builds a separate preview for each pull
request (`.github/workflows/pr-preview.yml`).

GitHub Pages must be set to **Settings → Pages → Source: Deploy from a branch → `gh-pages` /
(root)** so that the main site and the PR previews (in `gh-pages/pr-preview/`) live side by side.

## Run the web version locally:

```
cd web
python3 -m http.server 8000
```

Then open http://localhost:8000 — the same static files served by GitHub Pages.
After a rebuild, just hard-refresh the browser (the game bundle is cached aggressively).

## Sprites

`res/Char/<name>/sheet.png` are the Mortal Kombat II (SNES) sprite sheets from
spriters-resource.com. `tools/build_sprites.py` (standard library only) runs
`tools/mk2_sprites.py`, which maps each animation to sprite indices of the sheet and writes the
palettized, right-facing strips in `res/sprites/` that the game loads. The SNES sprites are
scaled with Scale2x and the console's 8:7 pixel aspect. Fighters are defined in
`src/characters.py`.

`tools/headless_test.py` plays CPU vs CPU fights with every fighter on both sides of the screen
until the fatality (no window, `SDL_VIDEODRIVER=dummy`) and saves screenshots; the PR preview
workflow runs it and publishes the screenshots under `pr-preview/pr-<N>/shots/`.

## Code map

| File | What |
|---|---|
| `src/fighter.py` | fighter state machine, moves, animations (fixed 60 Hz step) |
| `src/match.py` | rounds, hit/hurt boxes (pixel masks), projectiles, FINISH HIM, fatalities, snapshots |
| `src/render.py`, `src/fatalfx.py` | drawing (fighters, HUD, blood) and the drawn fatalities (electrocution, hat slice, soul steal) |
| `src/ai.py` | CPU opponent |
| `src/inputs.py` | keyboard + gamepads (SDL GameController on desktop, Gamepad API in the browser) |
| `src/net.py`, `webjs/net.js` | online rooms (TCP on desktop, WebRTC/PeerJS in the browser) |
| `webjs/touch.js` | on-screen touch controls for phones (exposed to Python as one more gamepad) |
| `src/menu.py`, `src/fight.py` | menus and the fight loop |

Enjoy! :)


OBS.: sprites from https://www.spriters-resource.com/snes/mortalkombat2/ — PeerJS (MIT) is
vendored in `webjs/`.
