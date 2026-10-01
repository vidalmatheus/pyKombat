#!/bin/bash
# Gera a versão web (pygbag/WebAssembly) em web/, publicada no GitHub Pages
# pelo workflow .github/workflows/pages.yml (e nas prévias de PR por
# .github/workflows/pr-preview.yml).
# Monta uma pasta temporária só com o necessário (código + assets usados),
# para o pacote não inflar com PDFs, PSDs, sheets originais, mp3 duplicados etc.
set -euo pipefail
cd "$(dirname "$0")"

STAGE=$(mktemp -d)/pyKombat
mkdir -p "$STAGE/src" "$STAGE/res/Background/ChoosingScenario" "$STAGE/res/Sound" "$STAGE/res/Music"

cp main.py "$STAGE/"
cp src/menu.py src/engine.py src/fight.py src/fighter.py src/match.py src/render.py \
   src/fatalfx.py src/assets.py src/characters.py src/inputs.py src/ai.py src/net.py \
   src/ui.py "$STAGE/src/"

# sprites paletizados (gerados por tools/build_sprites.py a partir de res/Char)
cp -r res/sprites "$STAGE/res/"
cp res/mk2.ttf res/icon.png res/finishhim.png res/fatality.png "$STAGE/res/"
cp res/Background/Scenario?.png res/Background/MainMenu0?.png res/Background/PyKombatLogo.png \
   "$STAGE/res/Background/"
cp res/Background/ChoosingScenario/ChooseScenario0?.png "$STAGE/res/Background/ChoosingScenario/"
cp res/Music/intro.ogg res/Music/mkt.ogg "$STAGE/res/Music/"
for s in selection back start options Fight block IceSound IceSound2 ComeHere GetOverHere \
         FinishHim ScorpionWins SubZeroWins Fatality HitFatality Excellent FlawlessVictory \
         Toasty HitLongo BeforeFinish Hit0 Hit1 Hit2 Hit3 Hit4 Hit5 Hit6 Hit7 Hit8 Hit9 Hit10 Hit11 Hit12; do
    cp "res/Sound/$s.ogg" "$STAGE/res/Sound/"
done

# --ume_block 0: começa o jogo direto, sem esperar clique/toque na página
# --no_opt: não passar os PNGs pelo pngquant (re-quantizar a paleta quebraria
#           a troca de cores dos lutadores; os assets já são pequenos)
python3 -m pygbag --template "$PWD/web.tmpl" --ume_block 0 --no_opt --build "$STAGE"

mkdir -p web
cp "$STAGE/build/web/index.html" "$STAGE/build/web/pykombat.tar.gz" web/
# carimbo do build nas URLs (pacote e net.js): depois de um deploy novo o
# navegador baixa a versão nova sem precisar limpar o cache
BUILD=$(git rev-parse --short HEAD 2>/dev/null || echo dev)-$(date +%s)
sed -i "s/__BUILD__/$BUILD/g" web/index.html
cp webjs/net.js webjs/peerjs.min.js web/   # salas online + controles (ver web.tmpl)
cp res/icon.png web/favicon.png # favicon = logo do jogo (não o padrão do pygbag)
cp res/Background/MainMenu01.png web/splash.png # arte da tela de carregamento (ver web.tmpl)
echo "OK: web/ atualizado ($(du -sh web | cut -f1))"
