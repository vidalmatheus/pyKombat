from pygame_functions import *

class Projectile:

    def __init__(self,pos = [0,0],id_fighter = 0):
        self.vel = 200
        self.id = id_fighter
        self.relativePos = [[150,0],[-200,-10]]
        self.position = pos + self.relativePos[id_fighter]
        self.projectileLimit = [12,6]
        self.name = ["Sub-Zero","Scorpion"]
        self.frame_projectile = 0
        self.projectile = makeSprite('../res/Char/'+str(self.name[self.id])+'/projectile.png', self.projectileLimit[self.id])
        self.frame_step = 60
        self.end_Projectile = True
    def setPos(self,pos = [0,0]):
        self.position = [pos[0] + self.relativePos[self.id][0],pos[1] 
            + self.relativePos[self.id][1]]
        print(self.position)
    def moveProjectile(self):
        if self.id == 0:
            self.position = self.position + self.vel*[1,0]
        else: self.position = self.position + self.vel*[-1,0]
        
    def isProjectileEnded(self):
        return self.end_Projectile

    def endProjectile(self):
        self.frame_projectile = 0
        self.end_Projectile = True
        hideSprite(self.projectile)
    
    def startProjectile(self):
        self.end_Projectile = False

    def drawProjectile(self,time,nextFrame):
        
        if time>nextFrame:
            moveSprite(self.projectile, self.position[0], self.position[1], True)
            showSprite(self.projectile)
            changeSpriteImage(self.projectile, self.frame_projectile)
            self.frame_projectile = (self.frame_projectile+1)
            #self.frame_projectile = (self.frame_projectile+1)%self.projectileLimit[self.id]
            if(self.frame_projectile == self.projectileLimit[self.id]):
               self.frame_projectile = 0
               self.end_Projectile = True
               hideSprite(self.projectile)
               print("Projetil ended")  
        
        return nextFrame + self.frame_step

    def getProjectileSprite(self):
        return self.projectile

