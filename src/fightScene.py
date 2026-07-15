import asyncio
import pygame
import os
from pygame.locals import *
import engine
from random import randint
import _fighter
import pygame_functions # p/ globais reatribuídos (background) — o import * congela o binding
from pygame_functions import *



class Scenario:
    
    def __init__(self, game, scenario):
        self.game = game
        self.scenario = scenario
        pygame.mixer.music.stop()
        music = engine.Music("mkt")
        music.play()
        music.volume(0.2)
        # button sprite
        self.back = makeSprite('res/back.png')

    async def run(self):
        # retorna o próximo estado do MenuFacade: "scenario" (voltar) ou None (sair)
        scenario = self.scenario
        if scenario == 9:
            scenario = randint(1, 8)
        #screenSize(800, 500,"pyKombat",None,None,True) # FullScreen
        screenSize(800, 500,"pyKombat") # Minimized
        setBackgroundImage('res/Background/Scenario'+str(scenario)+'.png')
        return await self.judge(scenario)

    async def judge(self,scenario):
        [player1,player2] = self.addFigther(scenario) 
        player1.act()
        player2.act()
        nextFrame1 = clock()
        nextFrame2 = clock()
        hitCounter = 0
        dizzyCounter = 1
        specialCounter = 1
        specialLimit = 41
        setAutoUpdate(False) # evita um flip de tela por sprite; um único updateDisplay() por frame (fim do loop)
        while True:
            aux1 = player1.fight(clock(),nextFrame1) # call fight moves
            nextFrame1 = aux1
            player1.life.render() # add lifebar
            aux2 = player2.fight(clock(),nextFrame2) # call fight moves
            nextFrame2 = aux2
            player2.life.render() # add lifebar
            
            # fighter positions
            x1 = player1.getX()
            x2 = player2.getX()

            # lutadores sempre de frente um para o outro
            player1.faceOpponent(x2)
            player2.faceOpponent(x1)
            sep = 1 if x1 <= x2 else -1 # sentido p/ separar os lutadores (lados podem estar trocados)

            # caso encostem na tela
            if player1.getX() < 20:
                player1.setX(20) 

            if player2.getX() < 20:
                player2.setX(20)  
            
            if player1.getX() > (800-20):
                player1.setX(800-20) 

            if player2.getX() > (800-20):
                player2.setX(800-20)  

            if not player1.isAlive() or not player2.isAlive():
                if not player1.isAlive(): # finish player1
                    if player2.isFatality() or player1.getHitName() == "fatality":
                        pass # fatality em andamento: as animações cuidam do resto
                    elif keyPressed(player2.combat[6]) and dizzyCounter < 100: # FATALITY! (P2: numpad 6 ou P)
                        player2.startFatality()
                        player1.takeHit("fatality")
                        player1.fatalityHitStart = clock() + 1000 # golpe do scorpion demora 1s p/ atingir
                    else:
                        player1.takeHit("dizzy")
                        if (collide(player1.currentSprite(),player2.currentSprite()) or collide(player1.getProjectile().getProjectileSprite(), player2.currentSprite()) or collide(player2.getProjectile().getProjectileSprite(), player1.currentSprite())):
                            if player2.isAttacking() or collide(player2.getProjectile().getProjectileSprite(), player1.currentSprite()):
                                dizzyCounter = 100 # tempo de dizzy
                        if dizzyCounter >= 100:
                            player1.takeHit("dead") # player1 morreu
                if not player2.isAlive(): # finish player 2
                    if player1.isFatality() or player2.getHitName() == "fatality":
                        pass # fatality em andamento
                    elif keyPressed(player1.combat[6]) and dizzyCounter < 100: # FATALITY! (P1: tecla F)
                        player1.startFatality()
                        player2.takeHit("fatality")
                        player2.fatalityHitStart = clock() + 1000 # golpe do subzero demora 1s p/ atingir
                    else:
                        player2.takeHit("dizzy")
                        if (collide(player2.currentSprite(),player1.currentSprite()) or collide(player2.getProjectile().getProjectileSprite(), player1.currentSprite()) or collide(player1.getProjectile().getProjectileSprite(), player2.currentSprite())):
                            if player1.isAttacking() or collide(player1.getProjectile().getProjectileSprite(), player2.currentSprite()):
                                dizzyCounter = 100 # tempo de dizzy
                        if dizzyCounter >= 100:
                            player2.takeHit("dead") # player2 morreu
                if dizzyCounter == 150:
                    # dica "BACKSPACE: MENU" (ESC também volta)
                    moveSprite(self.back, 400, 486, True)
                    showSprite(self.back)
                dizzyCounter += 1
                
            elif (collide(player1.currentSprite(),player2.currentSprite())):
                # caso só encostem
                if ( (player1.isWalking() or player1.isJumping()) and (player2.isDancing() or player2.isCrouching() or player2.isWalking() or player2.isDizzing() or player2.ishitSpecial() ) ) or ((player2.isWalking() or player2.isJumping()) and (player1.isDancing() or player1.isCrouching() or player1.isWalking() or player1.isDizzing() or player1.ishitSpecial()) ) or (player1.isWalking() and player2.isWalking()) or (player1.isJumping() and player2.isJumping()) or (player1.isDancing() and player2.isDancing()) or (player1.isSpecialMove() and player2.ishitSpecial()):
                    player1.setX(x1-6*sep)
                    if not player2.isSpecialMove() :player2.setX(x2+6*sep)
                # caso houve soco fraco:
                if ( player1.isApunching() and (player2.isWalking() or player2.isDancing() or player2.isApunching() or player2.ishitSpecial()) ) or ( player2.isApunching() and (player1.isWalking() or player1.isDancing() or player1.isApunching()) ):
                    if player1.isApunching():                        
                        player2.takeHit("Apunching")
                        specialCounter = specialLimit
                    if player2.isApunching():    
                        player1.takeHit("Apunching")
                    engine.Sound("Hit0").play()
                    if hitCounter == 0: engine.Sound().roundHit()
                    hitCounter = (hitCounter+1) % 5 
                # caso houve soco forte:
                if ( player1.isBpunching() and (player2.isWalking() or player2.isDancing() or player2.isBpunching() or player2.ishitSpecial()) ) or ( player2.isBpunching() and (player1.isWalking() or player1.isDancing() or player1.isBpunching()) ):
                    if player1.isBpunching():                        
                        player2.takeHit("Bpunching")
                        specialCounter = specialLimit
                    if player2.isBpunching():    
                        player1.takeHit("Bpunching")
                    engine.Sound("Hit0").play()
                    if hitCounter == 0: engine.Sound().roundHit()
                    hitCounter = (hitCounter+1) % 5 
                # caso houve chute fraco:
                if ( player1.isAkicking() and (player2.isWalking() or player2.isDancing() or player2.isAkicking() or player2.isCrouching() or player2.ishitSpecial()) and not player2.isBblocking() ) or ( player2.isAkicking() and (player1.isWalking() or player1.isDancing() or player1.isAkicking() or player1.isCrouching() and not player1.isBblocking()) ):
                    if player1.isAkicking():                        
                        player2.takeHit("Akicking")
                        specialCounter = specialLimit
                    if player2.isAkicking():                        
                        player1.takeHit("Akicking")
                    engine.Sound("Hit0").play()
                    if hitCounter == 0: engine.Sound().roundHit()
                    hitCounter = (hitCounter+1) % 5 
                # caso houve chute forte:
                if ( player1.isBkicking() and (player2.isWalking() or player2.isDancing() or player2.isBkicking() or player2.ishitSpecial()) ) or ( player2.isBkicking() and (player1.isWalking() or player1.isDancing() or player1.isBkicking()) ):
                    if player1.isBkicking():                        
                        player2.takeHit("Bkicking")
                        specialCounter = specialLimit
                    if player2.isBkicking():                        
                        player1.takeHit("Bkicking")
                    engine.Sound("Hit0").play()
                    if hitCounter == 0: engine.Sound().roundHit()
                    hitCounter = (hitCounter+1) % 5 
                # caso houve bloqueio em pé:
                if ( (player1.isApunching() or player1.isBpunching() or player1.isDpunching() or player1.isAkicking() or player1.isBkicking() ) and player2.isAblocking() ) or ( (player2.isApunching() or player2.isBpunching() or player1.isDpunching() or player2.isAkicking() or player2.isBkicking() ) and player1.isAblocking() ):
                    if player1.isAblocking():                        
                        player1.takeHit("Ablocking")
                    if player2.isAblocking():                        
                        player2.takeHit("Ablocking")
                    engine.Sound("block").play()
                    player1.setX(x1-12*sep)
                    player2.setX(x2+12*sep)
                # caso houve soco ou chute agachado fraco em alguém em pé:
                if ( ((player1.isCpunching() or player1.isCkicking() ) and not player2.isCrouching() and not player2.isBblocking() ) or ((player2.isCpunching() or player2.isCkicking() ) and not player1.isCrouching() and not player1.isBblocking() ) ): # falta adicionar o Bblock
                    if player1.isCpunching() or player1.isCkicking():                        
                        player2.takeHit("Cpunching")
                        specialCounter = specialLimit
                    if player2.isCpunching() or player2.isCkicking():    
                        player1.takeHit("Cpunching")
                    engine.Sound("Hit0").play()
                    if hitCounter == 0: engine.Sound().roundHit()
                    hitCounter = (hitCounter+1) % 5
                # caso houve soco agachado forte em alguém em pé:
                if ( (player1.isDpunching() and (not player2.isAblocking() and not player2.isBblocking())  )  or player2.isDpunching() and (not player1.isAblocking() and not player1.isBblocking()) ): 
                    if player1.isDpunching():                        
                        player2.takeHit("Bkicking")
                        specialCounter = specialLimit
                    if player2.isDpunching():    
                        player1.takeHit("Bkicking")
                    engine.Sound("Hit0").play()
                    if hitCounter == 0: engine.Sound().roundHit()
                    hitCounter = (hitCounter+1) % 5 
                # caso houve chute agachado forte em alguém em pé:
                if ( player1.isDkicking()  or player2.isDkicking() ): 
                    if player1.isDkicking():                        
                        player2.takeHit("Dkicking")
                        specialCounter = specialLimit
                    if player2.isDkicking():    
                        player1.takeHit("Dkicking")
                    engine.Sound("Hit0").play()
                    if hitCounter == 0: engine.Sound().roundHit()
                    hitCounter = (hitCounter+1) % 5 
                # caso houve soco ou chute agachado fraco em alguém agachado:
                if ( ( (player1.isCpunching() or player1.isCkicking()) and player2.isCrouching() and not player2.isBblocking()  )  or ( (player2.isCpunching() or player2.isCkicking()) and player1.isCrouching() and not player1.isBblocking() ) ):
                    if player1.isCpunching() or player1.isCkicking():                        
                        player2.takeDownHit("Ehit")
                    if player2.isCpunching() or player2.isCkicking():    
                        player1.takeDownHit("Ehit")
                    engine.Sound("Hit0").play()
                    if hitCounter == 0: engine.Sound().roundHit()
                    hitCounter = (hitCounter+1) % 5
                # caso houve bloqueio agachado:
                if ( (player1.isCpunching() or player1.isDpunching() or player1.isAkicking() or player1.isCkicking() ) and player2.isBblocking() ) or ( (player2.isCpunching() or player2.isDpunching() or player2.isAkicking() or player2.isCkicking() ) and player1.isBblocking() ):
                    if player1.isBblocking():                        
                        player1.takeDownHit("Bblocking")
                    if player2.isBblocking():                        
                        player2.takeDownHit("Bblocking")
                    engine.Sound("block").play()
                    player1.setX(x1-12*sep)
                    player2.setX(x2+12*sep)

            # caso houve special
            if ( player1.isSpecialMove() and (player2.isWalking() or player2.isDancing() or player2.isAblocking() or player2.isBblocking() or player2.ishitSpecial()) ) or ( player2.isSpecialMove() and (player1.isWalking() or player1.isDancing() or player1.isAblocking() or player1.ishitSpecial()) ):
                if player1.isSpecialMove() and collide(player1.getProjectile().getProjectileSprite(), player2.currentSprite()):   # and collide(projetil,player2)
                    player1.getProjectile().endProjectile()
                    if not player2.isAblocking() and not player2.isBblocking() and not player2.ishitSpecial():   player2.takeHit("special")
                if player2.isSpecialMove() and collide(player2.getProjectile().getProjectileSprite(), player1.currentSprite()):   # and collide(projetil,player1) 
                    player2.getProjectile().endProjectile()  
                    if not player1.isAblocking() and not player1.ishitSpecial() and not collide(player1.currentSprite(),player2.currentSprite()):   player1.takeHit("special")
                
            # caso frozen
            if ( player2.ishitSpecial() and specialCounter <= specialLimit-1 ):
                player2.takeHit("special")
                player2.life.addDamage(-5)
                specialCounter+=1
                if specialCounter == specialLimit: 
                    specialCounter = 1
                    player2.stopHit()
            if specialCounter == specialLimit: 
                specialCounter = 1

            
            

            for event in pygame.event.get():
                if event.type == QUIT:
                    return None
            if keyPressed("backspace"): # voltar ao menu de cenários
                return self.goBack(player1,player2)
            if keyPressed("esc"): # pausa
                pausedAt = clock()
                choice = await self.pauseMenu()
                if choice is None:
                    return None
                if choice == "back":
                    return self.goBack(player1,player2)
                # resume: retoma a música e compensa o tempo parado (senão os
                # relógios de animação ficariam atrasados e acelerariam a luta)
                pygame.mixer.music.unpause()
                # restaura o fundo inteiro (o véu escuro cobria a tela toda)
                pygame.display.get_surface().blit(pygame_functions.background.surface, (0, 0))
                delta = clock() - pausedAt
                nextFrame1 += delta
                nextFrame2 += delta
                while pygame.key.get_pressed()[pygame.K_ESCAPE]: # espera soltar ESC p/ não repausar
                    pygame.event.pump()
                    await asyncio.sleep(0.02)

            updateDisplay() # redesenha tudo uma única vez por frame
            tick(51) # 60*0.85: desacelera os movimentos por iteração (knockback etc.) em 15%
            await asyncio.sleep(0) # cede o controle ao navegador (pygbag)
    
    async def pauseMenu(self):
        # pausa a luta: música parada, cena congelada com fade escuro e um
        # menu RESUME/OPTIONS. Retorna "resume", "back" (menu de cenários)
        # ou None (fechar o jogo).
        pygame.mixer.music.pause()
        surf = pygame.display.get_surface()
        font = pygame.font.Font('res/mk2.ttf', 48) # fonte do menu do MK2 (mesma cara do menu principal)
        backHint = pygame.image.load('res/back.png')
        instructions = pygame.transform.smoothscale(
            pygame.image.load('res/Background/Instrucoes.png'), (800, 500)) # arte maior que a janela
        overlay = pygame.Surface((800, 500))
        overlay.fill((0, 0, 0))

        def drawScene(alpha):
            # luta congelada + véu escuro
            surf.blit(pygame_functions.background.surface, (0, 0))
            pygame_functions.spriteGroup.draw(surf)
            overlay.set_alpha(alpha)
            surf.blit(overlay, (0, 0))

        def drawHint():
            surf.blit(backHint, ((800 - backHint.get_width()) // 2, 500 - backHint.get_height() - 8))

        def drawMenu(sel):
            drawScene(150)
            for i, label in enumerate(["RESUME", "OPTIONS"]):
                colour = (196, 30, 30) if i == sel else (232, 232, 232)
                text = font.render(label, True, colour)
                surf.blit(text, (400 - text.get_width() // 2, 195 + i * 70))
            drawHint()
            pygame.display.update()

        # fade progressivo
        for alpha in (40, 80, 120):
            drawScene(alpha)
            pygame.display.update()
            await asyncio.sleep(0.05)

        sel = 0
        drawMenu(sel)
        showingOptions = False
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    if showingOptions:
                        if event.key in (K_BACKSPACE, pygame.K_ESCAPE):
                            engine.Sound("back").play()
                            showingOptions = False
                            drawMenu(sel)
                        continue
                    if event.key == pygame.K_ESCAPE:
                        return "resume"
                    if event.key == K_BACKSPACE:
                        engine.Sound("back").play()
                        return "back"
                    if event.key in (pygame.K_UP, pygame.K_DOWN):
                        engine.Sound().play()
                        sel = 1 - sel
                        drawMenu(sel)
                    if event.key == 13:  # ENTER
                        if sel == 0:
                            return "resume"
                        engine.Sound().play()
                        showingOptions = True
                        surf.blit(instructions, (0, 0))
                        drawHint()
                        pygame.display.update()
            await asyncio.sleep(1/30)

    def addFigther(self,scenario):
        player1 = _fighter.Fighter(0,scenario) # 0: subzero
        player2 = _fighter.Fighter(1,scenario) # 1: scorpion
        hideSprite(player1.spriteWins)
        hideSprite(player2.spriteWins)
        return player1,player2
    
    def goBack(self,player1,player2):
        # remove os sprites SEM redesenhar a cada kill — senão cada killSprite
        # faz um flip inteiro e "buracos" claros piscam na tela (visível
        # principalmente saindo do menu de pausa, sobre a cena escurecida)
        setAutoUpdate(False)
        # kill buttons
        killSprite(self.back)
        # kill players
        killSprite(player1.getProjectile().getProjectileSprite())
        killSprite(player2.getProjectile().getProjectileSprite())
        player1.killPlayer()
        player2.killPlayer()
        del(player1)
        del(player2)
        setAutoUpdate(True) # menus dependem do refresh automático
        sound = engine.Sound("back")
        sound.play()
        pygame.mixer.music.stop()
        music = engine.Music("intro")
        music.play()
        music.volume(0.5)
        return "scenario" # devolve ao MenuFacade em vez de recursar no menu
       
                        
def collide(sprite1,sprite2):
    return pygame.sprite.collide_mask(sprite1,sprite2)
