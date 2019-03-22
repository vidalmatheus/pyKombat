import pygame
import os
from pygame.locals import *
import config
import game
import engine
import menu
from random import randint

class Scenario:
    def __init__(self, game, scenario):
        self.game = game
        self.scenario = scenario
        pygame.mixer.music.stop()
        music = engine.Music("mkt")
        music.play()

    def setScenario(self, scenario):
        if scenario != 9:
            self.scene = pygame.image.load('../res/Background/Scenario'+str(scenario)+'.png')
        else: # random
            self.scene = pygame.image.load('../res/Background/Scenario'+str(randint(1, 8))+'.png')
        self.game.getDisplay().blit(self.scene, (0, 0))
        pygame.display.update()
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                # carregar áudio "out"
                sound = engine.Sound("back")  
                if event.type == pygame.KEYDOWN:  
                    if event.key == K_ESCAPE:
                        
                        sound.play()
                        pygame.mixer.music.stop()
                        music = engine.Music("intro")
                        music.play()     
                        menu.ScenarioMenu()


class Collision:
    def __init__(self, rect1, rect2):
        self.rect1 = rect1
        self.rect2 = rect2
        if rect1 == None or rect2 == None:
            self.center = None
        else:
            if self.collide():
                self.center = self.rect1.getCenter()+((self.rect2.getCenter()-self.rect1.getCenter())//2)
            else:
                self.center = None
    
    def collide(self):
        return (( self.rect1.position.x < self.rect2.position.x + self.rect2.width) \
        and (self.rect1.position.x + self.rect1.width > self.rect2.position.x)) \
        and (( self.rect1.position.y < self.rect2.position.y + self.rect2.height) \
        and (self.rect1.position.y + self.rect1.height > self.rect2.position.y))
