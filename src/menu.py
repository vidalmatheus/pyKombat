import pygame
import os
from pygame.locals import *
import config
import game
import engine


class Menu:
    pass
        
    
class MainMenu(Menu):
    def __init__(self, game = engine.Game()):
        clock = pygame.time.Clock()
        while True:
            clock.tick(15)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
            mainmenu = pygame.image.load('../res/Background/MainMenu01.png')
            game.getDisplay().blit(mainmenu, (0,0))
            pygame.display.update()

class OptionMenu(Menu):
    pass

class CharMenu(Menu):
    pass

class ScenarioMenu(Menu):
    pass