import asyncio
import pygame
from pygame.locals import *
import engine
import fightScene

MENU_FPS = 1/30  # pausa entre iterações dos menus (era clock.tick(10) bloqueante)


#---------------- Design Pattern Facade for Menus ---------------
# O Facade virou uma máquina de estados assíncrona: cada tela roda seu
# próprio loop (cedendo o controle com asyncio.sleep, exigência do
# navegador/pygbag) e devolve o PRÓXIMO estado em vez de construir a
# próxima tela — isso elimina a recursão menu -> luta -> menu.
#   Estados: "start" | "options" | "scenario" | ("fight", n) | None (sair)
class MenuFacade:
    def __init__(self, screen="start"):
        self.screen = screen

    async def run(self, game):
        state = self.screen
        while state is not None:
            print('Summoning menu:', state)
            if state == "start":
                state = await MainMenu(game).run()
            elif state == "options":
                state = await OptionMenu(game).run()
            elif state == "scenario":
                state = await ScenarioMenu(game).run()
            else:  # ("fight", scenario)
                fight = fightScene.Scenario(game, state[1])
                state = await fight.run()


class MainMenu:
    def __init__(self, game):
        self.game = game

    async def run(self):
        game = self.game
        screen = "start"
        mainmenu = pygame.image.load('res/Background/MainMenu01.png')
        game.getDisplay().blit(mainmenu, (0, 0))
        pygame.display.update()
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    # carregar áudio
                    sound = engine.Sound()
                    if event.key == pygame.K_ESCAPE:
                        return None
                    if event.key == 13:  # 13 == ENTER
                        # coloca áudio "in"
                        sound.setSound(screen)
                        sound.play()
                        return "scenario" if screen == "start" else "options"
                    elif screen == "start":
                        if event.key == pygame.K_DOWN or event.key == pygame.K_UP:
                            sound.play()
                            screen = "options"
                            mainmenu = pygame.image.load(
                                'res/Background/MainMenu02.png')
                            game.getDisplay().blit(mainmenu, (0, 0))
                            pygame.display.update()

                    elif screen == "options":
                        if event.key == pygame.K_DOWN or event.key == pygame.K_UP:
                            sound.play()
                            screen = "start"
                            mainmenu = pygame.image.load(
                                'res/Background/MainMenu01.png')
                            game.getDisplay().blit(mainmenu, (0, 0))
                            pygame.display.update()
            await asyncio.sleep(MENU_FPS)


class OptionMenu:
    def __init__(self, game):
        self.game = game

    async def run(self):
        mainmenu = pygame.image.load('res/Background/Instrucoes.png')
        self.game.getDisplay().blit(mainmenu, (0, 0))
        pygame.display.update()
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
                    if event.key == K_BACKSPACE:
                        # colocar áudio "out"
                        sound = engine.Sound("back")
                        sound.play()
                        return "start"
            await asyncio.sleep(MENU_FPS)


class ScenarioMenu:
    # navegação da grade 3x3 de cenários: {1..8, 9=random}
    moveMap = {
        1: {"down": 4, "right": 2},
        2: {"down": 5, "right": 3, "left": 1},
        3: {"down": 6, "left": 2},
        4: {"down": 7, "right": 5, "up": 1},
        5: {"down": 8, "right": 6, "left": 4, "up": 2},
        6: {"down": 9, "left": 5, "up": 3},
        7: {"right": 8, "up": 4},
        8: {"right": 9, "left": 7, "up": 5},
        9: {"left": 8, "up": 6},
    }
    keyNames = {pygame.K_DOWN: "down", pygame.K_UP: "up",
                pygame.K_LEFT: "left", pygame.K_RIGHT: "right"}

    def __init__(self, game):
        self.game = game

    async def run(self):
        scenario = 9  # começa no aleatório {1..8, 9=random}
        self.setScenario(scenario)
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    # carregar áudio
                    sound = engine.Sound()
                    if event.key == pygame.K_ESCAPE:
                        return None
                    if event.key == 13:  # 13 == ENTER
                        # Entra no cenário escolhido
                        sound.setSound("Fight")
                        sound.play()
                        return ("fight", scenario)
                    if event.key == pygame.K_BACKSPACE:
                        # colocar áudio "out"
                        sound = engine.Sound("back")
                        sound.play()
                        return "start"
                    if event.key in self.keyNames:
                        move = self.keyNames[event.key]
                        if move in self.moveMap[scenario]:
                            sound.play()
                            scenario = self.moveMap[scenario][move]
                            self.setScenario(scenario)
            await asyncio.sleep(MENU_FPS)

    def setScenario(self, scenario):
        self.mainmenu = pygame.image.load('res/Background/ChoosingScenario/ChooseScenario0'+str(scenario)+'.png')
        self.game.getDisplay().blit(self.mainmenu, (0, 0))
        pygame.display.update()
