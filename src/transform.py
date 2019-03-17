import numpy as np

"""classe de vetor de 2 dimensões, representa o vetor do mundo do jogo,
onde soma,subtração de 'vector2' são possiveis,chama-a 'vector(float,float)'"""
class vector2:
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
        return (vector2(self.x()+vec.x(), self.y()+vec.y()))

    def __sub__(self,vec):
        """operação de subtração, retorna self - vec"""
        return (vector2(self.x()-vec.x(), self.y()-vec.y()))

    def __mul__(self, multiplicador=1.0):
        """operação de multiplicação, retorna self*multiplicação.Talvez vá ter opção com matrizes"""
        return (vector2(self.x()*multiplicador, self.y()*multiplicador))
    def __truediv__(self, divisor = 1.0):
        """operação de divisão"""
        return (vector2(self.x()/divisor, self.y()/divisor))

    def __str__(self):
        """operação que retorna string para 'print'"""
        return "(" + str(self.x())+" ," +str(self.y()) + ")"


"""classe de tramsfor ele recebe uma determinada posição no mundo do jogo,
onde soma,subtração de 'vector2' ou 'transform' são possiveis,chama-a 'transform(vector2(float,float))'"""
class transform:
    def __init__(self, position = vector2(0.0,0.0)):
        """.position será publica"""
        self.position = position

    def getPostion(self):
        """retorna 'vector2' que representa a posição do objeto no mundo do jogo"""
        return self.position
    def getX(self):
        return self.position.x()

    def getY(self):
        return self.position.y()




