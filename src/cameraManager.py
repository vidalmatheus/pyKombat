import gameObject,gameState
from transform import  *
class Camera(gameObject.GameObject):
    def __init__(self,name = "camera",vec = vector2(0.0,0.0),game = gameState.gameStateManager()):
        super().__init__(name ,vec )
        self.gameState = game

    def getPositionInDisplay(self,obj = gameObject.GameObject()):
        """retorna a posição do objeto no display,retorna '(float,float)' para por no drawImage"""
        pos = obj.positionToWorld()
        camPos = self.positionToWorld()
        rel = pos - camPos
        scal = self.gameState.getPpm()*self.gameState.getScale()
        print(rel)
        print(scal*rel.x())
        return (self.gameState.getWidth()/2 + scal*rel.x(), self.gameState.getHeight()/2 - scal*rel.y())

"""
camera = Camera()
a = gameObject.GameObject("pai", vector2(1.5,111))
b = gameObject.GameObject("filho", vector2(0.7,35))
a =a + b
cameraTransform = camera.getTransform()
cameraTransform.position = cameraTransform.position

print(camera.getPositionInDisplay(b))
"""
