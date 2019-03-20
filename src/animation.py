import imageManager
import directory

class Animation:
    def __init__(self):
        self.frameList = []
        self.waitFrame = []
        self.i = 0
        self.frame = 1
        self.ended = False
        """tem que fazer os box colliders"""
    def setWaitFrameList(self,lista = []):
        self.waitFrame = lista

    def setFrameList(self,lista = []):
        """pega a lista da animação"""
        self.frameList = lista

    def start(self):
        self.i = 0
        self.frame = self.waitFrame[self.i]

    def update(self,positionInDisplay = (0.0,0.0), game = None):
        """atualiza o frame"""
        self.frame = self.frame - 1
        if self.frame == 0 and len(self.frameList[0]) == self.i + 1:
            self.ended = True
        elif self.frame < 0:
            self.i = self.i + 1
            self.frame = self.waitFrame[self.i]

        """desenha imagem"""
        self.frameList[self.i].drawImage(positionInDisplay,game )

    def rescaleFrames(self,scale = 1.0):
        """muda o tamanho das imagens"""
        if scale == 1.0:
            return
        for img in self.frameList:
            img.reScale(scale*img.getScale())

class animatorController:






