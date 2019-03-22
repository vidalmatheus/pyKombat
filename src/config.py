import pygame
from pygame.locals import *
from game import SpriteSheetLoader
import engine

class  Screen(object):
    instance = None       # Atribuição estática de classe para não precisar de inicializar toda hora
    def __new__(cls): 
        "Construtor em Python"
        if cls.instance is None:
            cls.instance = object.__new__(cls)
            opt_config = OptionConfig()
            cls.init(cls.instance, opt_config.video)
        return cls.instance
    
    def init(self, video):
        print("Inicializando a tela...")
        self.video = video
        if self.video == 0:
            self.screen = pygame.display.set_mode(engine.setDisplaySize(320, 240), 0, 32)
        elif 1 <= self.video <= 2:
            self.screen = pygame.display.set_mode(engine.setDisplaySize(640, 480), 0, 32)
        elif self.video == 3:
            self.screen = pygame.display.set_mode(engine.setDisplaySize(800, 600), 0, 32)
        elif 4 <= self.video <= 5:
            self.screen = pygame.display.set_mode(engine.setDisplaySize(960, 720), 0, 32)
        elif 6 <= self.video <= 7:
            self.screen = pygame.display.set_mode(engine.setDisplaySize(1280, 960), 0, 32)
        elif self.video == 8:
            self.screen = pygame.display.set_mode(engine.setDisplaySize(320, 240), pygame.FULLSCREEN, 32)
        pygame.display.set_caption("pyKombat")