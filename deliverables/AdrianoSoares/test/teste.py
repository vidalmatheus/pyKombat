import pygame,os
from pygame.locals import *
import spritesheetloader


pygame.init()

display_width = 800
display_height = 600

gameDisplay = pygame.display.set_mode((display_width,display_height)) #Tamanho da tela
pygame.display.set_caption('Py-Kombat') 

clock = pygame.time.Clock() #Vai ser importante para marcar a quantidade de variação de frames por segundo

crashed = False

Black = (0,0,0)
White = (255,255,255) #Sistema RGB de coloração 3 bytes para as cores
backgroundImage = pygame.image.load('Bckgrnd0.png')
subZeroFrame = 0 

def FaseDaPartida(screen):
    screen = pygame.transform.scale(screen,(800,600))
    gameDisplay.blit(screen,(0,0))
    pygame.display.update()
    

x = display_width*0.45
y = display_height*0.8
x_change = 0
Xposition = 0
Yposition = 450
position = (Xposition,Yposition)

def SubZeroPosition(screen,position):
    gameDisplay.blit(screen,position) #Posição de inicio, legal saber            


while not crashed:
    for event in pygame.event.get(): #Para cada evento realizado
        if event.type == pygame.QUIT: #Se for para parar
            crashed = True
        keys = pygame.key.get_pressed()
        if event.type == pygame.KEYDOWN:
            if keys[pygame.K_LEFT]:  
              x_change = -5
                
              if subZeroFrame == 0:
                 subZeroFrame = 8
              
              else: subZeroFrame -= 1
                  
                  
            

            if  keys[pygame.K_RIGHT]:
                x_change = 5
                subZeroFrame = (subZeroFrame+1)%9
            
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                x_change = 0
        
    
        print(event)
        print(keys[pygame.K_LEFT])
        subZero = pygame.image.load('w'+str(subZeroFrame + 1)+'.png')
        pygame.display.update()
    
    Xposition += x_change

    position = (Xposition,Yposition)

    FaseDaPartida(backgroundImage)
    SubZeroPosition(subZero,position)

        
    pygame.display.update()
        
    clock.tick(50) #60 frames por segundo

pygame.quit()





"""import pygame, sys
from pygame.locals import *

pygame.init()

DISPLAYSURF=pygame.display.set_mode((400,300))
pygame.display.set_caption("Hello World!")
while True: #principal loop
    for event in pygame.event.get():
        if event.type==QUIT:
            pygame.quit()
            sys.exit()
        pygame.display.update()
"""
