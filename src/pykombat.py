import pygame
import os
from pygame.locals import *
import menu             # importa menu.py
import engine           # importa engine.py

if __name__ == "__main__":
    print('loading...')

    pygame.init()
    pygame.mixer.init()   # som
    
    game = engine.Game()
    music = engine.Music()
    music.play()
    music.volume(0.5)
    menu = menu.MainMenu(game)

