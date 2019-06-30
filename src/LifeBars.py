import pygame
import pygame_functions



class LifeBar:
    def __init__(self,fighterName):
        self.hp = 100
        self.damage = 0
        self.lifeBarImg = pygame.image.load('../res/' + fighterName + 'lifebar.png')
        self.damageFull = pygame.image.load('../res/DamageFull.png')
        self.shown = self.damage/100.0
        self.damageImage = pygame.transform.scale(self.damageFull,(0,self.damageFull.get_height()))
        self.pos = [0.0, 0.0]
        """Posição da barra de hp relativa(cheia)"""
        self.RelativePos = [[338,0],[8,0]]
        self.initialPos = []
        self.dmgPos = self.RelativePos[0]
    
    def getLifeImage(self):
        return self.lifeBarImg
    
    def addDamage(self,dmg):
        """Adciona dano ao hp do personagem,se quizer curar basta um numero inteiro negativo"""
        if self.hp<=0:
            self.hp = 0
            return
        self.hp = self.hp - dmg
        self.damage = self.damage + dmg
        
        if self.damage > 100:
            self.damage = 100
            self.hp = 0
        
        self.shown = self.damage/100.0
        
        self.damageImage = self.damageImage = pygame.transform.scale(self.damageFull,(
            int(self.shown*self.damageFull.get_width()),self.damageFull.get_height()))
        
        self.damagePosition()
    
    def isDead(self):
        """Verifica se HP é menor ou igual a zero"""
        if self.hp <=0 :
            return True
        return False

    def setLifePosition(self,pos = [0.0,0.0]):
        self.pos = pos

    def render(self):
        pygame_functions.screen.blit(self.lifeBarImg,[self.pos[0],self.pos[1]])
        pygame_functions.screen.blit(self.damageImage, [self.pos[0] + self.dmgPos[0], self.pos[1]+self.dmgPos[1]])


class ProxyPlayerLifeBar(LifeBar):
    
    def __init__(self,fighterId):
        self.nameFighter = ["SubZero","Scorpion"]
        self.id = fighterId
        LifeBar.__init__(self,self.nameFighter[self.id])
        self.initialPos = self.RelativePos[self.id]
        self.dmgPos = self.initialPos
    
    def damagePosition(self):
        """abstract"""
        if self.id == 0: 
            self.dmgPos = [self.initialPos[0] - self.damageImage.get_width(),self.initialPos[1]]
    


