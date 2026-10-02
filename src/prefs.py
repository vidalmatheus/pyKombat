# Preferências que o jogo lembra entre partidas (ex.: dificuldade da CPU).
#
# Navegador (pygbag): localStorage da página. Desktop: um JSON na pasta do
# usuário. Qualquer falha (armazenamento bloqueado, arquivo sem permissão)
# só faz o jogo voltar ao padrão — nunca derruba nada.
import json
import os
import sys

WEB = sys.platform == 'emscripten'
KEY = 'pykombat.prefs'
PATH = os.path.join(os.path.expanduser('~'), '.pykombat.json')


def _load():
    try:
        if WEB:
            import platform
            raw = platform.window.localStorage.getItem(KEY)
            return json.loads(str(raw)) if raw else {}
        with open(PATH) as fh:
            return json.load(fh)
    except Exception:
        return {}


def get(name, default=None):
    v = _load().get(name)
    return default if v is None else v


def put(name, value):
    data = _load()
    data[name] = value
    try:
        raw = json.dumps(data)
        if WEB:
            import platform
            platform.window.localStorage.setItem(KEY, raw)
        else:
            with open(PATH, 'w') as fh:
                fh.write(raw)
    except Exception:
        pass
