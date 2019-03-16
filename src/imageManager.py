import pygame
from pygame.locals import *
import delegates


"""
imageManager é uma classe que altera outros objetos de imagem,não a si mesmo
"""
class imageManager:

    def scaleImage(image, scale = 1.0):
        "retorna uma imagem que crresponde a 'image',escalonada"
        ScaledImage = pygame.transform.smoothscale(image,(int(scale*image.get_width()),
                                                          int(scale*image.get_height())))
        return ScaledImage


    def cutImage(image,shown = ((0.0,1.0) , (0.0,1.0))):
        "retorna a imagem correspondente à 'image' cortada com o indice do shown '0' significa 'x' "
        CutImage = pygame.transform.chop(image,(shown[0][0]*image.get_width(),shown[1][0]*image.get_height(),
                                                shown[0][1]*image.get_width(),shown[1][1]*image.get_height()))
        return CutImage

    def drawImage(image, pos = (0.0,0.0), game = None):
        "prepara o desenho da imagem, e retorna o rect que determina a area que tera que ser redesenhada"
        rect = image.rect()
        return game.getDisplay().blit(image,(int(pos[0] - rect.center[0]),int(pos[1] - rect.center[1])))

"""
classe image é feito para armazenar as imagens na memoria,escalona-las,
corta-las, e retornar os blitRect para a função update do display desenha-las na região desejada
"""
class image:
    def __init__(self,local):
        self.local = local #local onde a imagem se encontra na pasta do jogo
        """retangulo que determina a regigão que o display irá redesenhar,será  
                                   usada para imagens que n são redesenhadas todos os frames"""
        self.blitRect = []
        if not local == "":
            self.Image = pygame.image.load(local).convert_alpha()
            self.Rect = self.Image.get_rect()


    def drawImage(self,pos = (0.0,0.0), game = None):
        """irá retornar o rect do desenho anterios e o novo"""
        beforeRect = self.blitRect
        self.blitRect = game.getDisplay().blit(self.Image,(int(pos[0]-self.Rect.center[0]),
                                                           int(pos[1]-self.Rect.center[1])))
        return beforeRect + self.blitRect


    def changeImage(self,image):
        """altera o a imagem principal,podera ser por ela mesma reescalonada,cortada ou invertida"""
        self.Image = image.convert_alpha()
        self.Rect = self.Image.get_rect()


    def getImage(self):
        """retorna a imagem"""
        return self.Image


    def getRect(self):
        """retorna rect"""
        return self.Rect


    def getWidth(self):
        """retorna o comprimento da imagem"""
        return self.Image.get_width()



    def getHeight(self):
        """retorna a altura da imagem"""
        return self.Image.get_height()


