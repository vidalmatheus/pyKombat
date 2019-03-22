import pygame
import os
from pygame.locals import *
import config
import engine
import menu

class GameRectangle:
    def __init__(self, width, height, position =engine.Vector2(0,0)):
            # Falta verificar
        self.width = width
        self.height = height
        self.area = self.width * self.height
    
    def value(self):
        return (self.width,self.height)
    
    def getCenter(self):
        return self.position + (self.width//2, self.height//2)


class SpriteSheetLoader:
    def __init__(self,file,sprite_width,sprite_height):
        self.sheet = pygame.image.load(os.path.join(file))
        self.sprite_width = sprite_width
        self.sprite_height = sprite_height
        #self.sprite_list=self.makeSpritelist()

class RectangleSheetLoader:
    def __init__(self,file,sprite_width,sprite_height):
        self.sprite_width = sprite_width
        self.sprite_height = sprite_height
        self.rectangle_list = []