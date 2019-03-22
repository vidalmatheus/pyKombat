import pygame
import os
from pygame.locals import *
import config
import game
import engine
import menu

class Scenario:
    def __init__(self, game, scenario):
        self.game = game
        self.scenario = scenario
        pygame.mixer.music.stop()
        music = engine.Music("mkt")
        music.play()

    def setScenario(self, scenario):
        self.scene = pygame.image.load('../res/Background/Scenario'+str(scenario)+'.png')
        self.game.getDisplay().blit(self.scene, (0, 0))
        pygame.display.update()
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == K_ESCAPE:
                        # colocar áudio "out"
                        sound = engine.Sound("back")
                        sound.play()     
                        #scene = self.scene.ScenarioMenu()
