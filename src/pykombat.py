import pygame
import os
from pygame.locals import *
import config           # importa config.py
import menu             # importa menu.py
import engine           # importa engine.py
# from game import Point  # importa apenas a classe Point de game.py

if __name__ == "__main__":
    print('loading...')

    pygame.init()
    pygame.mixer.init()   # som
    
    game = engine.Game()
    music = engine.Music()
    music.play()
    music.volume(0.5)
    menu = menu.MainMenu(game)

