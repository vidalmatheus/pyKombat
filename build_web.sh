#!/bin/bash
# Gera a versão web (pygbag/WebAssembly) em web/, publicada no GitHub Pages
# pelo workflow .github/workflows/pages.yml.
# Monta uma pasta temporária só com o necessário (código + png/ogg usados),
# para o pacote não inflar com PDFs, PSDs, mp3 duplicados etc.
set -euo pipefail
cd "$(dirname "$0")"

STAGE=$(mktemp -d)/pyKombat
mkdir -p "$STAGE/src"

cp main.py "$STAGE/"
cp src/menu.py src/engine.py src/fightScene.py src/_fighter.py \
   src/projectile.py src/LifeBars.py src/pygame_functions.py "$STAGE/src/"
rsync -a --include='*/' --include='*.png' --include='*.ogg' --include='*.ttf' --exclude='*' res/ "$STAGE/res/"

# remove sons não referenciados pelo código
python3 - "$STAGE/res/Sound" <<'EOF'
import os, sys
keep = {'selection','back','start','options','Fight','block','IceSound','ComeHere',
        'FinishHim','ScorpionWins','SubZeroWins','Fatality','HitFatality'} | {f'Hit{i}' for i in range(13)}
d = sys.argv[1]
for f in os.listdir(d):
    if f[:-4] not in keep:
        os.remove(os.path.join(d, f))
EOF

# --ume_block 0: começa o jogo direto, sem esperar clique/toque na página
python3 -m pygbag --template "$PWD/web.tmpl" --ume_block 0 --build "$STAGE"

mkdir -p web
cp "$STAGE/build/web/index.html" "$STAGE/build/web/pykombat.tar.gz" web/
cp res/icon.png web/favicon.png # favicon = logo do jogo (não o padrão do pygbag)
cp res/Background/MainMenu01.png web/splash.png # arte da tela de carregamento (ver web.tmpl)
echo "OK: web/ atualizado ($(du -sh web | cut -f1))"
