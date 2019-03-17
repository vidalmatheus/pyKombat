from transform import *

"""classe gameObjeto sera classe pai de todas as classe de instancias"""
class GameObject:

    def __init__(self,name = "object",vec = vector2(0.0,0.0)):
        self.name = name
        self.transform = transform(vec)
        self.children = []
        self.parent = None
        self.faceRight = True

    def positionToWorld(self):
        """retorna a posição do objeto em relação ao mundo"""
        if self.parent is None:
            return self.transform.position
        else:
            return self.transform.position + self.parent.positionToWorld()
    def getTransform(self):
        return self.transform

    def isFacingRight(self):
        """retorna uma booleana,caso esteja olhando para a direita será 'True'"""
        return self.faceRight

    def changeFacingRight(self,facing=True):
        """insere 'True' para faceRight"""
        self.faceRight = facing

    def xInvertion(self):
        """inverte o 'gameObject' em 'x' e altera o faceRight"""
        self.faceRight = not self.faceRight
        if len(self.children) > 0:
            for child in self.children:
                child.getTransform().position = child.getTransform().position - \
                                                vector2(2.0*child.getTransform().position.x(), 0.0)
                child.xInvertion()

    def yInvertion(self):
        """inverte o 'gameObject' em 'y' e altera o faceRight"""
        if len(self.children)>0:
            for child in self.children:
                child.getTransform().position = child.getTransform().position - \
                                                vector2(0.0,2.0*child.getTransform().position.y())
                child.yInvertion()

    def draw(self):
        return
    def __add__(self, obj):
        """operação de adciona a lista de children"""
        obj.parent = self
        self.children.append(obj)


    def __sub__(self, obj):
        """operação de remove a lista de children"""
        self.children.remove(obj)


