import pygame
import os
from pygame.locals import *
import config
import game
import engine


class Menu:
    pass


class MainMenu(Menu):
    def __init__(self, game=engine.Game()):
        clock = pygame.time.Clock()
        screen = "start"
        mainmenu = pygame.image.load('../res/Background/MainMenu01.png')
        game.getDisplay().blit(mainmenu, (0, 0))
        pygame.display.update()
        while True:
            clock.tick(15)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    # coloca áudio
                    if event.key == 13:  # 13 == ENTER
                        # coloca áudio "in"
                        if screen == "start":
                            ScenarioMenu()
                        if screen == "options":
                            print("flag1")
                            OptionMenu()
                    elif screen == "start":
                        if event.key == pygame.K_DOWN or event.key == pygame.K_UP:
                            screen = "options"
                            mainmenu = pygame.image.load(
                                '../res/Background/MainMenu02.png')
                            game.getDisplay().blit(mainmenu, (0, 0))
                            pygame.display.update()

                    elif screen == "options":
                        if event.key == pygame.K_DOWN or event.key == pygame.K_UP:
                            screen = "start"
                            mainmenu = pygame.image.load(
                                '../res/Background/MainMenu01.png')
                            game.getDisplay().blit(mainmenu, (0, 0))
                            pygame.display.update()

class OptionMenu(Menu):
    def __init__(self):
        mainmenu = pygame.image.load('../res/Background/Instrucoes.png')
        game.getDisplay().blit(mainmenu, (0, 0))
        
        pygame.display.update()
        print("flag2")
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if pygame.key == K_ESCAPE:
                    print("ESCAPE")
                    # colocar áudio "out"
                    MainMenu()
        print("flag3")


class CharMenu(Menu):
    pass


class ScenarioMenu(Menu):
    def __init__(self, game=engine.Game()):
        scenario = 1  # {1,2,3,4,5,6,7,8,9=random}
        mainmenu = pygame.image.load('../res/Background/ChoosingScenario/ChooseScenario01.png')
        game.getDisplay().blit(mainmenu, (0, 0))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                # coloca áudio
                if event.key == 13:  # 13 == ENTER
                        # coloca áudio "in"
                        # Entra no cenário escolhido
                    game
                elif scenario == 1:
                    if event.key == pygame.K_DOWN:
                        # coloca áudio
                        scenario = 4
                    if event.key == pygame.K_RIGHT:
                        # coloca áudio
                        scenario = 2
                    self.setScenario(scenario)

                elif scenario == 2:
                    if event.key == pygame.K_DOWN:
                        # coloca áudio
                        scenario = 5
                    if event.key == pygame.K_RIGHT:
                        # coloca áudio
                        scenario = 3
                    if event.key == pygame.K_LEFT:
                        # coloca áudio
                        scenario = 1
                    self.setScenario(scenario)

                elif scenario == 3:
                    if event.key == pygame.K_DOWN:
                        # coloca áudio
                        scenario = 6
                    if event.key == pygame.K_LEFT:
                        # coloca áudio
                        scenario = 2
                    self.setScenario(scenario)

                elif scenario == 4:
                    if event.key == pygame.K_DOWN:
                        # coloca áudio
                        scenario = 7
                    if event.key == pygame.K_RIGHT:
                        # coloca áudio
                        scenario = 5
                    if event.key == pygame.K_UP:
                        # coloca áudio
                        scenario = 1
                    self.setScenario(scenario)

                elif scenario == 5:
                    if event.key == pygame.K_DOWN:
                        # coloca áudio
                        scenario = 8
                    if event.key == pygame.K_RIGHT:
                        # coloca áudio
                        scenario = 6
                    if event.key == pygame.K_LEFT:
                        # coloca áudio
                        scenario = 4
                    if event.key == pygame.K_UP:
                        # coloca áudio
                        scenario = 2
                    self.setScenario(scenario)

                elif scenario == 6:
                    if event.key == pygame.K_DOWN:
                        # coloca áudio
                        scenario = 9
                    if event.key == pygame.K_LEFT:
                        # coloca áudio
                        scenario = 5
                    if event.key == pygame.K_UP:
                        # coloca áudio
                        scenario = 3
                    self.setScenario(scenario)

                elif scenario == 7:
                    if event.key == pygame.K_RIGHT:
                        # coloca áudio
                        scenario = 8
                    if event.key == pygame.K_UP:
                        # coloca áudio
                        scenario = 4
                    self.setScenario(scenario)

                elif scenario == 8:
                    if event.key == pygame.K_RIGHT:
                        # coloca áudio
                        scenario = 9
                    if event.key == pygame.K_LEFT:
                        # coloca áudio
                        scenario = 7
                    if event.key == pygame.K_UP:
                        # coloca áudio
                        scenario = 5
                    self.setScenario(scenario)

                elif scenario == 9:
                    if event.key == pygame.K_LEFT:
                        # coloca áudio
                        scenario = 8
                    if event.key == pygame.K_UP:
                        # coloca áudio
                        scenario = 6
                    self.setScenario(scenario)

                if pygame.event.get() == pygame.K_ESCAPE:
                    # colocar áudio "out"
                    MainMenu()

    def setScenario(scenario):
        mainmenu = pygame.image.load(
            '../res/Background/ChoosingScenario/ChooseScenario0'+scenario+'.png').convert()
        game.getDisplay().blit(mainmenu, (0, 0))
        pygame.display.update()
