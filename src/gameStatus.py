import pygame,os
from pygame.locals import *
import delegates

"""
É a classe que será responsavel, pelas alterações que deverão ser constante pelo game,
como o tamanho da tela,funcionalidade do pygame,como inicializar o jogo,pegar o tempo entre os frames
"""
class gameStatusManager:
    def __init__(self,width = 800, height = 500,fps = 24,icon = None,gameName = "pyKombat"):
        self.width = width
        self.height = height
        self.gameExit = False
        self.frame = 0
        self.fps = fps
        self.gameName = gameName
        self.icon = icon
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.display = pygame.display.set_mode((self.width,self.height),HWSURFACE|DOUBLEBUF)
        self.clock = pygame.time.Clock()

        self.frameRect = [] #É a lista dos rects geradas no frame atual(novo Frame)
        self.lastFrameRect = []  # É a lista dos rects geradas no frame anterior(novo Frame)

        self.musicVolume = 10
        self.fxVolume = 10

        pygame.display.set_caption(self.gameName)
        self.event = self.getEvent()


    def setMusicVolume(self, value):
        """
        define o valor do volume do som,varia entre inteiro de 0-10
        """
        if value > 10:
            value = 10
        elif value < 0:
            value = 0
        self.musicVolume = value


    def setFxMusicVolume(self, value):
        """
        define o valor do volume dos efeitos sonoros,varia entre inteiro de 0-10
        """
        if value > 10:
            value = 10
        elif value < 0:
            value = 0
        self.fxVolume = value


    def getScaleTime(self):
        """
        Retorna a escala do tempo '0.0' é parado, '1.0' normal,
        essa escala pode variar livremente entre os reais positivo
        """
        return self.scaleTime


    def getMusicVolume(self):
        """
        Retorna o volume de musica '0' é mudo, '10' maximo,
        """
        return self.musicVolume


    def getFxVolume(self):
        """
        Retorna o volume dos efeitos sonoros '0' é mudo, '10' maximo,
        """
        return self.fxVolume


    def getDisplay(self):
        """
        Retorna o display do pygame,
        """
        return self.display


    def getWidth(self):
        """
        Retorna o comprimento da tela em pixels
        """
        return self.width


    def getHeight(self):
        """
        Retorna o altura da tela em pixels
        """
        return self.height


    def waitFrame(self):
        """
        espera um determinado, até o frame terminar em tempo de (1/fps) e retorna o tempo em segundos
        """
        return self.clock.tick(self.fps)/1000

    def changeFps(self,newFPS = 24):
        """
        muda o valor do fps
        """
        self.fps = newFPS


    def getEvent(self):
        """pega e retorna os eventos no pygame"""
        self.event = pygame.event.get()
        return self.event


    def getEventList(self):
        "retorna os eventos no pygame"
        return self.event


    def quit(self):
        "fecha o jogo"
        pygame.quit()


