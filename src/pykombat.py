# Entrada legada: o jogo agora vive em main.py na raiz do projeto
# (estrutura exigida pelo pygbag para rodar no navegador).
# Este wrapper mantém `python pykombat.py` funcionando a partir de src/.
import os
import runpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    runpy.run_path(os.path.join(ROOT, 'main.py'), run_name='__main__')
