import pygame
from pygame.locals import *
from game import SpriteSheetLoader
import engine

class  Screen(object):
    instance = None       # Atribuição estática de classe para não precisar de inicializar toda hora
    def __new__(cls): 
        "Construtor em Python"
        if cls.instance is None:
            cls.instance = object.__new__(cls)
            opt_config = OptionConfig()
            cls.init(cls.instance, opt_config.video)
        return cls.instance
    
    def init(self, video):
        print("Inicializando tela...")
        self.video = video
        if self.video == 0:
            self.screen = pygame.display.set_mode(engine.setDisplaySize(320, 240), 0, 32)
        elif 1 <= self.video <= 2:
            self.screen = pygame.display.set_mode(engine.setDisplaySize(640, 480), 0, 32)
        elif self.video == 3:
            self.screen = pygame.display.set_mode(engine.setDisplaySize(800, 600), 0, 32)
        elif 4 <= self.video <= 5:
            self.screen = pygame.display.set_mode(engine.setDisplaySize(960, 720), 0, 32)
        elif 6 <= self.video <= 7:
            self.screen = pygame.display.set_mode(engine.setDisplaySize(1280, 960), 0, 32)
        elif self.video == 8:
            self.screen = pygame.display.set_mode(engine.setDisplaySize(320, 240), pygame.FULLSCREEN, 32)
        pygame.display.set_caption("pyKombat")
        
    def display_update(self, screen):
        
        if self.video == 1:
            screen = pygame.transform.scale(screen, (640, 480))
        elif self.video == 2:
            screen = pygame.transform.scale2x(screen)
        elif self.video == 3:
            screen = pygame.transform.scale(screen, (800, 600))
        elif self.video == 4:
            screen = pygame.transform.scale(screen, (960, 720))
        elif self.video == 5:
            screen = pygame.transform.scale2x(screen)
            screen = pygame.transform.scale(screen, (960, 720))
        elif self.video == 6:
            screen = pygame.transform.scale(screen, (1280, 960))
        elif self.video == 7:
            screen = pygame.transform.scale2x(screen)
            screen = pygame.transform.scale(screen, (1280, 960))
        
        self.screen.blit(screen, (0,0))
        pygame.display.update()

class  Alphabet(object):
    instance = None       # Attribut statique de classe
    def __new__(cls): 
        "méthode de construction standard en Python"
        if cls.instance is None:
            cls.instance = object.__new__(cls)
            cls.sprites = SpriteSheetLoader('../res/Ascii.png', 16, 16, True).getSpriteList()
        return cls.instance

class SoundPlayer:
    instance = None       # Attribut statique de classe
    def __new__(cls): 
        "méthode de construction standard en Python"
        if cls.instance is None:
            print('creating SoundPlayer')
            cls.instance = object.__new__(cls)
            vol_config = OptionConfig()
            cls.music_vol = vol_config.music*0.1
            cls.sound_vol = vol_config.sound*0.1
        return cls.instance
    
    def reinit(self, music, sound):
        self.music_vol = music*0.1
        self.sound_vol = sound*0.1
        pygame.mixer.music.set_volume(self.music_vol)
    
    def play_music(self, file):
        if file.find('../res/sound/music/') < 0:
            file = '../res/sound/music/'+file
        try:
            pygame.mixer.music.stop()
            while pygame.mixer.music.get_busy():
                print('wait...', end='')
            pygame.mixer.music.load(file)
            pygame.mixer.music.set_volume(self.music_vol)
            pygame.mixer.music.play(-1)
        except:
            print('failed to load', file)
            return
    
    def play_sound(self, file):
        if file.find('../res/sound/') < 0:
            file = '../res/sound/'+file
        sound = pygame.mixer.Sound(file)
        sound.set_volume(self.sound_vol)
        sound.play()

class OptionConfig:
    def __init__(self, file = '../res/config.txt'):
        self.time = 3
        self.rounds = 1
        self.video = 0
        self.sound = 3
        self.music = 3
        self.keysP1 = [32]*7
        self.keysP2 = [32]*7
        try:
            self.loadconfig(file)
        except:
            print('Error: unable to load config !!')
    
    def loadconfig(self, file):
        with open(file, encoding='utf-8') as txtfile:
            for line in txtfile:
                line.lower()
                if line.find('time=') != -1:
                    self.time = int(line.strip('time='))
                if line.find('rounds=') != -1:
                    self.rounds = int(line.strip('rounds='))
                if line.find('video=') != -1:
                    self.video = int(int(line.strip('video=')))
                if line.find('sound=') != -1:
                    self.sound = int(line.strip('sound='))
                if line.find('music=') != -1:
                    self.music = int(line.strip('music='))
                if line.find('keysP1=') != -1:
                    keys = line.strip('keysP1=').split('/')
                    keys.remove('\n')
                    for i in range(len(keys)):
                        keys[i]=int(keys[i])
                    self.keysP1 = keys
                if line.find('keysP2=') != -1:
                    keys = line.strip('keysP2=').split('/')
                    keys.remove('\n')
                    for i in range(len(keys)):
                        keys[i]=int(keys[i])
                    self.keysP2 = keys
    
    def saveconfig(self, file):
        with open(file, mode='w', encoding='utf-8') as txtfile:
            txtfile.write('time='+str(self.time)+'\n')
            txtfile.write('rounds='+str(self.rounds)+'\n')
            txtfile.write('video='+str(self.video)+'\n')
            txtfile.write('sound='+str(self.sound)+'\n')
            txtfile.write('music='+str(self.music)+'\n')
            txtfile.write('keysP1=')
            for i in self.keysP1:
                txtfile.write(str(i)+'/')
            txtfile.write('\nkeysP2=')
            for i in self.keysP2:
                txtfile.write(str(i)+'/')
            txtfile.write('\n')
            
            Screen().init(self.video)
            SoundPlayer().reinit(self.music, self.sound)
            print("music:", self.music, "sound:", self.sound)
            
if __name__ == "__main__":
    c = OptionConfig('../res/config.txt')
    print('done')