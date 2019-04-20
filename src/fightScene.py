import pygame
import os
from pygame.locals import *
import config
import game
import engine
import menu
from random import randint
import _fighter
from pygame_functions import *



class Scenario:
    
    def __init__(self, game, scenario):
        self.game = game
        self.scenario = scenario
        pygame.mixer.music.stop()
        #music = engine.Music("mkt")
        #music.play()

    def setScenario(self, scenario):
        if scenario == 9:
            scenario = randint(1, 8)
        #self.scene = pygame.image.load('../res/Background/Scenario'+str(scenario)+'.png')
        #self.game.getDisplay().blit(self.scene, (0, 0))
        #pygame.display.update()
        screenSize(800, 500,"pyKombat")
        setBackgroundImage('../res/Background/Scenario'+str(scenario)+'.png')
        self.judge(scenario)
    
    def judge(self,scenario):
        [player1,player2] = self.addFigther(scenario) 
        player1.act()
        player2.act()
        nextFrame1 = clock()
        nextFrame2 = clock()
        while True:
            aux1 = player1.fight(clock(),nextFrame1)
            nextFrame1 = aux1
            aux2 = player2.fight(clock(),nextFrame2)
            nextFrame2 = aux2    
            if(collide(player1,player2)):
                # caso só encostem
                x1 = player1.getX()
                x2 = player2.getX()
                if (player1.isWalking() and player2.isDancing()) or (player2.isWalking() and player1.isDancing()) or (player1.isWalking() and player2.isWalking()):
                    player1.setX(x1-12)
                    player2.setX(x2+12) 
                # caso houve soco fraco:
                if ( player1.isPunching() and (player2.isWalking() or player2.isDancing()) ) or ( player2.isPunching() and (player1.isWalking() or player1.isDancing()) ):
                    if player1.isPunching():                        
                        player2.takeHit("Apunching")
                    else: player1.takeHit("Apunching")
                    sound = engine.Sound("Hit2")  
                    sound.play()
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                if keyPressed("esc"):
                    self.goBack(player1,player2)
    
    def addFigther(self,scenario):
        player1 = _fighter.Fighter(0) # 0: subzero
        player2 = _fighter.Fighter(1) # 1: scorpion
        return player1,player2
    
    def goBack(self,player1,player2):
        player1.killPlayer()
        player2.killPlayer()
        del(player1)
        del(player2)
        sound = engine.Sound("back")  
        sound.play()
        pygame.mixer.music.stop()
        music = engine.Music("intro")
        music.play()     
        menu.ScenarioMenu()
       
                        
def collide(player1,player2):
    return pygame.sprite.collide_mask(player1.currentSprite(), player2.currentSprite())
