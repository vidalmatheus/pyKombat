import pygame

pygame.init()

modeWidth = 800
modeHeight = 600
gameDisplay = pygame.display.set_mode((modeWidth,modeHeight))
pygame.display.set_caption("First Game")
bg = pygame.image.load('Bckgrnd0.png')
walkChar = [pygame.image.load('w1.png'),pygame.image.load('w2.png'),pygame.image.load('w3.png'),pygame.image.load('w4.png'),pygame.image.load('w5.png'),pygame.image.load('w6.png'),pygame.image.load('w7.png'),pygame.image.load('w8.png'),pygame.image.load('w9.png')]
standChar = [pygame.image.load('stand1.png'),pygame.image.load('stand2.png'),pygame.image.load('stand3.png'),pygame.image.load('stand4.png'),pygame.image.load('stand5.png'),pygame.image.load('stand6.png'),pygame.image.load('stand7.png')]
x=200
y=200
width = 80
height = 200
vel = 7
isJump = False
jumpCount = 10
run = True

walkCount = 0
waiting = 0

left = False
right = False
stand = 0

clock = pygame.time.Clock()

def FaseDaPartida(screen):
    screen = pygame.transform.scale(screen,(800,600))
    gameDisplay.blit(screen,(0,0))
    pygame.display.update()

def redrawGameWindow(sizeVetor,isJumping):
    global walkCount
    global waiting
    pygame.time.delay(10)
    #stringChar = str(comando+'Char')
    FaseDaPartida(bg)
    if not (isJumping):
        if left :
            gameDisplay.blit(walkChar[walkCount%sizeVetor],(x,y))
            walkCount+= 1
        elif right:
            gameDisplay.blit(walkChar[walkCount%sizeVetor],(x,y))
            walkCount+= 1
        else: 
            gameDisplay.blit(standChar[walkCount%sizeVetor],(x,y))
            waiting += 1
            if waiting>40:
                walkCount+= 1
                waiting = 0

    else: gameDisplay.blit(standChar[0],(x,y))
    pygame.display.update()



while run:
    #pygame.time.delay(100)
    clock.tick(30)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT] and x>vel:
        x-= vel
        left = True
        right = False
        comando = walkChar
    elif keys[pygame.K_RIGHT] and x<modeWidth-width-vel:
        x+= vel
        right = True
        left = False
        comando = walkChar
    else:
        right = False
        left = False
        walkCount = 0
        comando = standChar
    if not(isJump):
        #if keys[pygame.K_UP] and y>vel:
         #   y-= vel
        #if keys[pygame.K_DOWN] and y<modeHeight-height-vel:
         #   y+= vel
        #if keys[pygame.K_SPACE]:
        if keys[pygame.K_UP]:
            isJump = True
    else:
        comando = standChar
        if jumpCount >= -10:
            neg = 1
            if jumpCount < 0 :
                neg = -1
            y-= (jumpCount **2)*0.5*neg
            jumpCount -=1    
        else:
            isJump = False
            jumpCount = 10

    redrawGameWindow(len(comando),isJump)



pygame.quit()