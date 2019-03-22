import pygame
import os
from pygame.locals import *
import config           # importa config.py
import menu             # importa menu.py
import gameState        # importa gameState.py
# from game import Point  # importa apenas a classe Point de game.py

if __name__ == "__main__":
    print('loading...')

    gameState.gameStateManager()
