import pygame
from Fighter import Fighter

pygame.init()

modeWidth = 800
modeHeight = 600
gameDisplay = pygame.display.set_mode((modeWidth,modeHeight))

bg = pygame.image.load('Bckgrnd0.png')

        
        
def FaseDaPartida(screen):
    screen = pygame.transform.scale(screen,(800,600))
    gameDisplay.blit(screen,(0,0))
    pygame.display.update()


def redrawGameWindow(object):
    FaseDaPartida(bg)
    object.drawFighter(gameDisplay)
    
    pygame.display.update()

run = True
clock = pygame.time.Clock()

Scorpion = Fighter(200,450,80,200,2)

while run:

    clock.tick(30)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]: 
        Scorpion.moveLeft()

    
    elif keys[pygame.K_RIGHT] :
        Scorpion.moveRight(modeWidth)

    elif keys[pygame.K_DOWN]:
        Scorpion.moveDown() 
    
    elif keys[pygame.K_SPACE]:
        Scorpion.special()

    else: Scorpion.stand()
        
    if not Scorpion.isJump:
        
        if keys[pygame.K_UP]:
            Scorpion.isJump = True
            Scorpion.isDown = False
    else: Scorpion.jump()
    Scorpion.waitingSpecial+=1    
    redrawGameWindow(Scorpion)

pygame.quit()