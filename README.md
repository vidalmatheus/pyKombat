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
| Sub-Zero | Ice blast (freezes) | Slide | Spine splitter |
| Scorpion | Spear ("Get over here!") | Teleport punch | Spear splitter |
| Reptile | Acid spit | Slide | Acid bath |
| Smoke | Harpoon | Teleport punch | Smoke bomb |
| Noob Saibot | Shadow disc | Shadow teleport | Shadow slice |
| Ermac | Soul ball | Teleport punch | Telekinetic slam |
| Rain | Lightning orb | Slide | Thunderstrike |
| Tremor | Rock throw | Slide | Earthquake |
| Frost | Ice shard (freezes) | Slide | Deep freeze |
| Chameleon | Mimic (random) | Teleport punch | Any of them |

The eight new ninjas are palette swaps of the Sub-Zero/Scorpion sprites — the same trick the
original Mortal Kombat used. Freezing an already frozen opponent backfires, just like in MK.


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

`res/Char/` holds the original sprite sheets. `tools/build_sprites.py` turns them into the
palettized, right-facing sheets in `res/sprites/` that the game loads (re-run it after editing
the originals; requires Pillow). New fighters are defined in `src/characters.py`.

## Code map

| File | What |
|---|---|
| `src/fighter.py` | fighter state machine, moves, animations (fixed 60 Hz step) |
| `src/match.py` | rounds, hit/hurt boxes (pixel masks), projectiles, FINISH HIM, fatalities, snapshots |
| `src/render.py`, `src/fatalfx.py` | drawing (fighters, HUD, blood) and the procedural fatalities |
| `src/ai.py` | CPU opponent |
| `src/inputs.py` | keyboard + gamepads (SDL GameController on desktop, Gamepad API in the browser) |
| `src/net.py`, `webjs/net.js` | online rooms (TCP on desktop, WebRTC/PeerJS in the browser) |
| `src/menu.py`, `src/fight.py` | menus and the fight loop |

Enjoy! :)


OBS.: sprites from https://www.spriters-resource.com/snes/mortalkombat2/ — PeerJS (MIT) is
vendored in `webjs/`.
