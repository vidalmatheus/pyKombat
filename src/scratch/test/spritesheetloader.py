import pygame,os
from pygame.locals import *

class SpritesheetLoader:
    
    def __init__(self,file,sprite_width,sprite_height, fullsheet=False):
        self.sheet = pygame.image.load(os.path.join(file))
        self.sprite_width = sprite_width
        self.sprite_height = sprite_height
        self.sprite_list=self.makeSpritelist()
        if not fullsheet:
            self.removeBlanks(file)
    
    def getSpriteList(self):
        return self.sprite_list
    
    def getSpriteLines(self,*args):
        for arg in args:
            assert(isinstance(arg, int)) # Se for um indice de array
            yield self.sprite_list[arg] # Retorna a animação e pega a próxima
    
    def makeSprite(self,line=0,column=0):
        sprite = pygame.Surface((self.sprite_width, self.sprite_height)).convert_alpha()
        sprite.fill((0,0,0,0))
        sprite.blit(self.sheet, (-(column*self.sprite_width),-(line*self.sprite_height)))
        return sprite
    
    def makeSpritelist(self):
        size = self.sheet.get_size()
        sprite_list=[]
        for i in range(int(size[1]/self.sprite_height)):    
            sprite_line=[]
            for j in range(int(size[0]/self.sprite_width)):
                sprite_line.append(self.makeSprite(i,j))
            sprite_list.append(sprite_line)
        return sprite_list
    
    def testBlankSprite(self,sprite):
        for i in range(self.sprite_width):
            for j in range(self.sprite_height):
                if sprite.get_at((i,j))!=(0,0,0,0):
                    return False
        return True
    
    def removeBlanks(self, file):
        try:
            with open(file.replace('.png', '.txt'), encoding='utf-8') as txtfile:
                i=0
                for line in txtfile:
                    length = int(line)
                    while length < len(self.sprite_list[i]):
                        self.sprite_list[i].pop()
                    i+=1
        except:
            print('creating...')    
            for sprite_line in self.sprite_list:
                j=0
                while j < len(sprite_line):
                    if self.testBlankSprite(sprite_line[j]):
                        sprite_line[j] = None
                    j+=1
            self.write(file)
            
    def write(self,file):
        txtfile = open(file.replace('.psd', '.txt'), mode='w', encoding='utf-8') #Estava png
        for sprite_line in self.sprite_list:
            i=0
            for sprite in sprite_line:
                if sprite == None:
                    break
                else: i+=1
            txtfile.write(str(i))
            txtfile.write('\n')    
        