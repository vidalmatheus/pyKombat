# pyKombat
[CES-22]_[COMP21]_Game developed in python with pygame. 

Group: Adriano Soares/ Matheus Vidal/ Pedro Alves

Sprites: https://www.spriters-resource.com/snes/mortalkombat2/

![alt text](https://github.com/vidalmatheus/pyKombat/blob/master/res/Background/MainMenu01.png)

![alt text](https://github.com/vidalmatheus/pyKombat/blob/master/res/Screenshot.png)

## Play in the browser 🎮

https://vidalmatheus.github.io/pyKombat/

(no install needed — powered by [pygbag](https://github.com/pygame-web/pygbag)/WebAssembly)

## Run the game locally:

```
python main.py
```

## Rebuild the web version:

```
pip install pygbag
./build_web.sh
```

This refreshes `web/`, which is deployed to GitHub Pages automatically on push.

## Run the web version locally:

```
cd web
python3 -m http.server 8000
```

Then open http://localhost:8000 — the same static files served by GitHub Pages.
After a rebuild, just hard-refresh the browser (the game bundle is cached aggressively).

Enjoy! :)
