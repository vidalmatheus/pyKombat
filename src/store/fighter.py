import engine

"""Usa a classe GameObject como superClasse e veja as classes Animation,AnimationManager e Transform"""
"""criado um condigo pra facilitar os testes renderizados,então pra testar vai ter que criar vc mesmo,
susar a classe Game e Camera pode ajudar"""

class State:
    def __init__(self):
        self.animationIndex = 0
        self.animation = None
        self.waitTime = 0.0

class StateController():
    def __init__(self):
        self.animatorController = engine.AnimatorController()
        self.stateList = []
        self.state = None
        self.stateVariable = 0
        self.dictVar = {"faceRight":1,"right":2,"left":4,"up":8
                        ,"down":16, "strongPunch":32, "punch":64, "strongKick":128, "kick":258,
                        "defence":516,"specialMove":1032,"down":2064,"onTheAir":4128,"dizzy":8256,"frozen":16512,
                        "ended":33024,"hit":66048,"endedState":132096

        }

    def update(self,game = None):
        if self.animation.hasEnded():
            self.waitTime -= game.getDeltaTime()



class Fighter(engine.GameObject):
    def __init__(self, name="fighter", vec=Vector2(0.0, 0.0)):
        super().__init__(name,vec)
        self.fighterName = name
        self.stateController = StateController()
        self.enemy = None
        self.control = None#recebe a variavel controle


        #self.loadImages = #Tem que upar as imagens do Scorpion
         
    def setEnemy(self,enemyFighter = Fighter()):
        self.enemy = enemyFighter
    """def initializeScorpion(self,position,game):
        engine.ImageManager.drawImage(image, self.position, game)"""




