from pygame_functions import * #Necessary to manipulate Spritesheets


class ProjectileModel: #Create standards of projectile model.
 
    def __init__(self,pos= [0,0],id_fighter= 0): #Configurations of Projectile
        self.vel = 200
        self.id = id_fighter
        self.relativePos = [[150,-15],[-200,-10]] #Start Position of Characters
        self.position = pos + self.relativePos[id_fighter]
        self.projectileLimit = [12,6]
        self.name = ["Sub-Zero","Scorpion"]
        self.frame_projectile = 0
        self.projectile = makeSprite('../res/Char/'+str(self.name[self.id])+'/projectile.png', self.projectileLimit[self.id])
        self.frame_step = 60
        self.end_Projectile = True
#------------------------------------------------------------------------------------------------------------------------------
class ProjectileView: #Create standards of projectile views.

    def __init__(self,ProjectileModel):
        self.projectileModel = ProjectileModel
    
    def draw(self,time,nextFrame):
        
        if time>nextFrame:
            moveSprite(self.projectileModel.projectile, self.projectileModel.position[0], self.projectileModel.position[1], True)
            showSprite(self.projectileModel.projectile)
            changeSpriteImage(self.projectileModel.projectile, self.projectileModel.frame_projectile)
            self.projectileModel.frame_projectile = (self.projectileModel.frame_projectile+1)
            
            if(self.projectileModel.frame_projectile == self.projectileModel.projectileLimit[self.projectileModel.id]):
               self.projectileModel.frame_projectile = 0
               self.projectileModel.end_Projectile = True
               hideSprite(self.projectileModel.projectile)
        
        return nextFrame + self.projectileModel.frame_step

#---------------------------------------------------------------------------------------------------------------------------------
class Projectile: #Controller

    def __init__(self,pos,id_fighter): #Load ProjectileModel and insert the object in ProjectileView
        self.projectileModel = ProjectileModel(pos,id_fighter)
        self.projectileView = ProjectileView(self.projectileModel)


    def drawProjectile(self,time,nextFrame):
        return self.projectileView.draw(time,nextFrame)
        

    
    def setPos(self,pos = [0,0]):
        self.projectileModel.position = [pos[0] + self.projectileModel.relativePos[self.projectileModel.id][0],pos[1] 
            + self.projectileModel.relativePos[self.projectileModel.id][1]]

    def moveProjectile(self):
        if self.projectileModel.id == 0:
            self.projectileModel.position = self.projectileModel.position + self.projectileModel.vel*[1,0]
        else: self.projectileModel.position = self.projectileModel.position + self.projectileModel.vel*[-1,0]
        
    def isProjectileEnded(self):
        return self.projectileModel.end_Projectile

    def endProjectile(self):
        self.projectileModel.frame_projectile = 0
        self.projectileModel.end_Projectile = True
        hideSprite(self.projectileModel.projectile)
    
    def startProjectile(self):
        self.projectileModel.end_Projectile = False


    def getProjectileSprite(self):
        return self.projectileModel.projectile

#------------------------------------------------------------------------------------------------------------------------------
#Código antigo
#from pygame_functions import *

#class Projectile:

 #   def __init__(self,pos = [0,0],id_fighter = 0):
  #      self.vel = 200
  #      self.id = id_fighter
  #      self.relativePos = [[150,-15],[-200,-10]]
  #      self.position = pos + self.relativePos[id_fighter]
  #      self.projectileLimit = [12,6]
  #      self.name = ["Sub-Zero","Scorpion"]
  #      self.frame_projectile = 0
  #      self.projectile = makeSprite('../res/Char/'+str(self.name[self.id])+'/projectile.png', self.projectileLimit[self.id])
  #      self.frame_step = 60
  #      self.end_Projectile = True

   # def setPos(self,pos = [0,0]):
    #    self.position = [pos[0] + self.relativePos[self.id][0],pos[1] 
#            + self.relativePos[self.id][1]]

    #def moveProjectile(self):
     #   if self.id == 0:
      #      self.position = self.position + self.vel*[1,0]
       # else: self.position = self.position + self.vel*[-1,0]
        
    #def isProjectileEnded(self):
     #   return self.end_Projectile

    #def endProjectile(self):
     #   self.frame_projectile = 0
     #   self.end_Projectile = True
     #   hideSprite(self.projectile)
    
    #def startProjectile(self):
     #   self.end_Projectile = False

    #def drawProjectile(self,time,nextFrame):
        
     #   if time>nextFrame:
     #       moveSprite(self.projectile, self.position[0], self.position[1], True)
     #       showSprite(self.projectile)
     #       changeSpriteImage(self.projectile, self.frame_projectile)
     #       self.frame_projectile = (self.frame_projectile+1)
     #       #self.frame_projectile = (self.frame_projectile+1)%self.projectileLimit[self.id]
     #       if(self.frame_projectile == self.projectileLimit[self.id]):
     #          self.frame_projectile = 0
     #          self.end_Projectile = True
     #          hideSprite(self.projectile)
        
     #   return nextFrame + self.frame_step

    #def getProjectileSprite(self):
     #   return self.projectile

