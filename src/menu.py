import pygame, os
from pygame.locals import *
import config
import Round
import game

class MainMenu(self):
    clock = pygame.time.Clock()
    while True:
        clock.tick(15)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()

    pygame.display.update()


    menu = menu.MainMenu()

