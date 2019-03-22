import pygame,os
from pygame.locals import *
import numpy as np
import delegates

"""
É a classe que será responsavel, pelas alterações que deverão ser constante pelo game,
como o tamanho da tela,funcionalidade do pygame,como inicializar o jogo,pegar o tempo entre os frames
"""
class Game:
    def __init__(self,width = 800, height = 500,fps = 24,icon = None,gameName = "pyKombat"):
        pygame.init()
        self.width = width
        self.height = height
        self.displayWidth = width
        self.displayHeight = height
        self.gameExit = False
        self.frame = 0
        self.fps = fps
        self.gameName = gameName
        self.icon = icon
        self.scale = 1.0
        self.ppm = 70 #pixel por metros
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.display = pygame.display.set_mode((self.width,self.height),HWSURFACE|DOUBLEBUF)
        self.clock = pygame.time.Clock()
        self.deltaTime = 0.0
        self.musicVolume = 10
        self.fxVolume = 10

        pygame.display.set_caption(self.gameName)
        self.event = self.getEvent()

    def getDisplayWidth(self):
        """Retorna o comprimento do 'display'"""
        return self.diplayWidth

    def getDisplayHeight(self):
        """Retorna a altura do 'display'"""
        return self.diplayHeight

    def setDisplaySize(self,value = (800,500)):
        """altera o tamanho do display,onde 'value =(int = 800,int=500)' """
        scale = value[0]/self.width
        if int(scale*self.displayHeight) > value[1]:
            print("não proporçã do almento do comprimento da tela não pode ser maior que da altura")
            print("logo a tela,não será alterada")
            return
        self.displayWidth = value[0]
        self.scale = value[0]/self.width
        self.displayHeight = value[1]
        self.display = pygame.display.set_mode(value,HWSURFACE|DOUBLEBUF)

    def setScale(self, value=1.0):
        """
        Põe o valor da escala, onde o '1.0' é o o tamanho original,se value menor que ou igual à'0.0'
        a scale não é alterada
        """
        if value <= 0.0:
            return
        self.scale = value

    def getScale(self):
        """Retorna o valor da escala"""
        return self.scale

    def setPpm(self,value = 1.0):
        """
        Põe o valor da ppm(pixel por metro), onde o '0.0' é o o tamanho original,se value menor que ou igual à'0.0'
        a scale não é alterada
        """
        if value <= 0.0:
            return
        self.ppm = value

    def getPpm(self):
        """Retorna o valor da ppm, o padrão é 70"""
        return self.ppm

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

    """espera um determinado tempo(1/fps), pega esse tempo e põe no deltaTime"""
    def waitFrame(self):  # espera um determinado tempo(1/fps)
        self.deltaTime = self.clock.tick(self.fps) / 1000

    """Retorna o tempo entre os frames"""
    def getDeltaTime(self):
        return self.deltaTime

    def quit(self):
        "fecha o jogo"
        pygame.quit()

"""
imageManager é uma classe que altera outros objetos de imagem,não a si mesmo
"""
class ImageManager:

    def scaleImage(image, scale = 1.0):
        "retorna uma imagem que crresponde a 'image',escalonada"
        if scale == 1.0:
            return
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
class Image:
    def __init__(self,local):
        self.local = local #local onde a imagem se encontra na pasta do jogo

        self.scale = 1.0
        self.blitRect = []
        """retangulo que determina a regigão que o display irá redesenhar,será  
                                           usada para imagens que n são redesenhadas todos os frames"""
        if not local == "":
            self.Image = pygame.image.load(local).convert_alpha()
            self.Rect = self.Image.get_rect()
    def getScale(self):
        """retorna o valor da 'scale' da imagem"""
        return self.scale
    def reScale(self,scale = 1.0):
        """ré-escala o tamanho da imagem"""
        if scale == 1.0 and self.scale == 1.0:
            return
        self.Image = ImageManager.scaleImage(self.Image, scale/self.scale)
        self.scale = scale

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

"""classe de vetor de 2 dimensões, representa o vetor do mundo do jogo,
onde soma,subtração de 'vector2' são possiveis,chama-a 'vector(float,float)'"""
class Vector2:
    def __init__(self,x = 0.0,y = 0.0):
        self.vec = np.array((x,y))#usa numpy,pois ela possue operações de arrays e matrizes mais velozes

    def x(self):
        """retorna x"""
        return self.vec[0]

    def y(self):
        """retorna y"""
        return self.vec[1]

    def __add__(self, vec):
        """operação de soma, retorna self + vec"""
        return Vector2(self.x()+vec.x(), self.y()+vec.y())

    def __sub__(self,vec):
        """operação de subtração, retorna self - vec"""
        return Vector2(self.x()-vec.x(), self.y()-vec.y())

    def __mul__(self, multiplicador=1.0):
        """operação de multiplicação, retorna self*multiplicação.Talvez vá ter opção com matrizes"""
        return Vector2(self.x()*multiplicador, self.y()*multiplicador)
    def __truediv__(self, divisor = 1.0):
        """operação de divisão"""
        return Vector2(self.x()/divisor, self.y()/divisor)

    def __str__(self):
        """operação que retorna string para 'print'"""
        return "(" + str(self.x())+" ," +str(self.y()) + ")"


"""classe de tramsfor ele recebe uma determinada posição no mundo do jogo,
onde soma,subtração de 'vector2' ou 'transform' são possiveis,chama-a 'transform(vector2(float,float))'"""
class Transform:
    def __init__(self, position = Vector2(0.0,0.0)):
        """.position será publica"""
        self.position = position

    def getPostion(self):
        """retorna 'vector2' que representa a posição do objeto no mundo do jogo"""
        return self.position

    def getX(self):
        return self.position.x()

    def getY(self):
        return self.position.y()


"""classe gameObjeto sera classe super de todas as classe de instancias"""

class GameObject:

    def __init__(self, name="object", vec=Vector2(0.0, 0.0)):
        self.name = name
        self.transform = Transform(vec)
        self.children = []
        self.parent = None
        # self.faceRight = True

    def positionToWorld(self):
        """retorna a posição do objeto em relação ao mundo"""
        if self.parent is None:
            return self.transform.position
        else:
            return self.transform.position + self.parent.positionToWorld()

    def getTransform(self):
        return self.transform

    '''
    def isFacingRight(self):
        """retorna uma booleana,caso esteja olhando para a direita será 'True'"""
        return self.faceRight

    def changeFacingRight(self,facing=True):
        """insere 'True' para faceRight"""
        self.faceRight = facing
    '''

    def xInvertion(self):
        """inverte o 'gameObject' em 'x' e altera o faceRight"""
        # self.faceRight = not self.faceRight
        if len(self.children) > 0:
            for child in self.children:
                child.getTransform().position = child.getTransform().position - \
                                                Vector2(2.0 * child.getTransform().position.x(), 0.0)
                child.xInvertion()

    def yInvertion(self):
        """inverte o 'gameObject' em 'y' e altera o faceRight"""
        if len(self.children) > 0:
            for child in self.children:
                child.getTransform().position = child.getTransform().position - \
                                                Vector2(0.0, 2.0 * child.getTransform().position.y())
                child.yInvertion()

    def Update(self, game=None):
        """
        Update é um metodo abstrata,que o objeto chama todo frame, em que ele essta ativo
        ela vai ser responsavel de atualizar o objeto durante a gameScene.
        """
        return

    def render(self, positionInDisplay=(0.0, 0.0), game=None):
        """
        render é um metodo abstrata,que o objeto chama todo frame, em que ele essta ativo.
        ela vai ser responsavel de desenhar o objeto na camera na camera.
        """
        return

    def __add__(self, obj):
        """operação de adciona a lista de children"""
        obj.parent = self
        self.children.append(obj)

    def __sub__(self, obj):
        """operação de remove a lista de children"""
        self.children.remove(obj)

"""
classe responsavel pela animação,não é responsavel pela alocação das imagens
"""
class Animation:
    def __init__(self):
        self.frameList = []
        self.waitFrame = []
        self.i = 0
        self.frame = 1
        self.ended = False
        """tem que fazer os box colliders"""
    def setWaitFrameList(self,lista = []):
        """
        recebe a lista de wait frames, ela diz quantos frames do jogo tem que se passar,
        para passar a proxima imagem
        """
        self.waitFrame = lista

    def setFrameList(self,lista = []):
        """pega a lista da animação"""
        self.frameList = lista

    def start(self):
        self.i = 0
        self.frame = self.waitFrame[self.i]

    def update(self):
        """atualiza o frame"""
        self.frame = self.frame - 1
        if self.frame == 0 and len(self.frameList[0]) == self.i + 1:
            self.ended = True
        elif self.frame < 0:
            self.i = self.i + 1
            self.frame = self.waitFrame[self.i]


    def render(self,positionInDisplay = (0.0,0.0), game = None):
        """desenha imagem"""
        return self.frameList[self.i].drawImage(positionInDisplay, game)
    def rescaleFrames(self,scale = 1.0):
        """muda o tamanho das imagens"""
        if scale == 1.0:
            return
        for img in self.frameList:
            img.reScale(scale*img.getScale())

#class animatorController:
"""classe GameObject,que será responsavel pela camera do jogo"""
class Camera(GameObject):
    def __init__(self,name = "camera",vec = Vector2(0.0,0.0),game = Game()):
        super().__init__(name ,vec )
        self.gameState = game
        self.sceneGameObjectsScene = []
        self.Ui = []

    def getRenderList(self):
        """
        retorna o 'delegate' das renders, para que a camera possa desenhar a imagem
        """
        return self.sceneGameObjectsScene

    def getPositionInDisplay(self,obj = GameObject()):
        """retorna a posição do objeto no display,retorna '(float,float)' para por no drawImage"""
        pos = obj.positionToWorld()
        camPos = self.positionToWorld()
        rel = pos - camPos
        scal = self.gameState.getPpm()*self.gameState.getScale()
        print(rel)
        print(scal*rel.x())
        return self.gameState.getWidth()/2 + scal*rel.x(), self.gameState.getHeight()/2 - scal*rel.y()

