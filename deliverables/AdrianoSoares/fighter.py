import pygame

class Fighter(object):
    
    def __init__(self,x,y,width,height,OneOrTwo):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vel = 7
        self.isJump = False
        self.isDown = False
        self.isSpecial = True
        self.jumpCounter = 10
        self.abaixado = y+height/3
        self.emPe = y
        self.walkCount = 0
        self.standCount = 0
        self.jumpCount = 0
        self.downCount = 0
        self.waiting = 0
        self.waitingSpecial = 0
        self.number = OneOrTwo
        self.walkChar = [pygame.image.load(str(OneOrTwo)+'/walk/w1.png'),pygame.image.load(str(OneOrTwo)+'/walk/w2.png'),pygame.image.load(str(OneOrTwo)+'/walk/w3.png'),pygame.image.load(str(OneOrTwo)+'/walk/w4.png'),pygame.image.load(str(OneOrTwo)+'/walk/w5.png'),pygame.image.load(str(OneOrTwo)+'/walk/w6.png'),pygame.image.load(str(OneOrTwo)+'/walk/w7.png'),pygame.image.load(str(OneOrTwo)+'/walk/w8.png'),pygame.image.load(str(OneOrTwo)+'/walk/w9.png')]
        self.standChar = [pygame.image.load(str(OneOrTwo)+'/stand/stand1.png'),pygame.image.load(str(OneOrTwo)+'/stand/stand2.png'),pygame.image.load(str(OneOrTwo)+'/stand/stand3.png'),pygame.image.load(str(OneOrTwo)+'/stand/stand4.png'),pygame.image.load(str(OneOrTwo)+'/stand/stand5.png'),pygame.image.load(str(OneOrTwo)+'/stand/stand6.png'),pygame.image.load(str(OneOrTwo)+'/stand/stand7.png')]
        self.jumpChar = [pygame.image.load(str(OneOrTwo)+'/jump/j1.png'),pygame.image.load(str(OneOrTwo)+'/jump/j2.png'),pygame.image.load(str(OneOrTwo)+'/jump/j3.png')]
        self.downChar = [pygame.image.load(str(OneOrTwo)+'/down/d1.png'),pygame.image.load(str(OneOrTwo)+'/down/d2.png'),pygame.image.load(str(OneOrTwo)+'/down/d3.png')]
        self.specialChar = [pygame.image.load(str(OneOrTwo)+'/special/s1.png'),pygame.image.load(str(OneOrTwo)+'/special/s2.png'),pygame.image.load(str(OneOrTwo)+'/special/s3.png'),pygame.image.load(str(OneOrTwo)+'/special/s4.png')]

    def moveLeft(self):
        
        if(self.x> self.vel): 
            self.x-= self.vel
            if not self.isJump:
                self.y = self.emPe
            self.left = True
            self.ultimate = False
            self.right = False
            self.isDown = False
        

    def moveRight(self,modeWidth):
        
        if(self.x<modeWidth-self.width-self.vel):
            self.x+= self.vel
            if not self.isJump:
                self.y = self.emPe
            self.right = True
            self.left = False
            self.ultimate = False
            self.isDown = False

    def moveDown(self):
        
        if(not self.isJump):
            self.right = False
            self.left = False
            self.ultimate = False
            self.isDown = True
            self.y = self.abaixado
    
    def stand(self):
        
        if not(self.isJump) and not(self.isDown):
            self.y = self.emPe
        self.right = False
        self.left = False
        self.ultimate = False
        self.isDown = False
        self.walkCount = 0
    

    def jump(self):
        
        if self.jumpCounter >= -10:
            neg = 1
            if self.jumpCounter < 0 :
                neg = -1
            self.y-= (self.jumpCounter **2)*0.5*neg
            self.jumpCounter -=1    
        else:
            self.isJump = False
            self.jumpCounter = 10

    
    def special(self):
        if(self.isSpecial):
            self.isSpecial = False
            self.ultimate = True
        elif(self.waitingSpecial > 30):
            self.isSpecial = True
            self.waitingSpecial = 0
            self.ultimate = True
        else:
            self.ultimate = False 
    

    
    
    def drawFighter(self,gameDisplay):
        
        if not (self.isJump):
        
            if not (self.isDown):
                if self.left :
                    gameDisplay.blit(self.walkChar[self.walkCount%len(self.walkChar)],(self.x,self.y))
                    self.waiting +=1
                    self.standCount = 0
                    self.jumpCount = 0
                    if self.walkCount<0:
                        self.walkCount = len(self.walkChar) - 1

                    if self.waiting>1:
                        self.walkCount-= 1
                        self.waiting = 0

                elif self.right:
                    gameDisplay.blit(self.walkChar[self.walkCount%len(self.walkChar)],(self.x,self.y))
                    self.waiting +=1
                    self.walkCount+= 1
                    self.standCount = 0
                    self.jumpCount = 0
                    if self.waiting>1:
                        self.walkCount-= 1
                        self.waiting = 0
                
                elif (self.ultimate):
                    contador = 0
                    self.waiting = 0
                    gameDisplay.blit(self.specialChar[contador],(self.x,self.y))
                    while(self.waiting<100000):
                        self.waiting += 1
                        self.walkCount = 0
                        self.jumpCount = 0
                    
                        if self.waiting == 20000 and contador<len(self.specialChar)-1:
                            contador +=1
                            gameDisplay.blit(self.specialChar[contador],(self.x,self.y))
                            self.waiting = 0 
                        if contador == len(self.specialChar):
                            contador = len(self.specialChar)-1
                            self.waiting = 20001
                            
                    


                else:
                    
                    gameDisplay.blit(self.standChar[self.standCount%len(self.standChar)],(self.x,self.y))
                    self.waiting += 1
                    self.walkCount = 0
                    self.jumpCount = 0
                    
                    if self.waiting>1:
                        self.standCount +=1
                        self.waiting = 0
                
            else:gameDisplay.blit(self.downChar[2],(self.x,self.y))
                
            
        else: 
            if self.jumpCount >= 0 and self.jumpCount < 5 :
                gameDisplay.blit(self.jumpChar[0],(self.x,self.y))
            elif self.jumpCount >= 5 and self.jumpCount <= 13:
                gameDisplay.blit(self.jumpChar[1],(self.x,self.y))
            elif self.jumpCount > 13 and self.jumpCount <= 20:
                gameDisplay.blit(self.jumpChar[0],(self.x,self.y))
            else : gameDisplay.blit(self.jumpChar[2],(self.x,self.y))
            
            self.jumpCount+=1