# pyKombat — ponto de entrada
# Roda no desktop (python main.py) e no navegador via pygbag/WebAssembly,
# por isso o loop principal é assíncrono (asyncio.run + await nos loops).
import asyncio
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)  # caminhos de assets ('res/...') são relativos à raiz
sys.path.insert(0, os.path.join(ROOT, 'src'))

import pygame
import engine
import menu


async def main():
    print('loading...')

    pygame.init()
    pygame.mixer.init()   # som

    game = engine.Game()
    music = engine.Music()
    music.play()
    music.volume(0.5)
    # Design Pattern Facade (ou Interface): máquina de estados dos menus/luta
    await menu.MenuFacade().run(game)
    pygame.quit()


asyncio.run(main())
