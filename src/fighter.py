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
    def __init__(self, name="fighter", vec=engine.Vector2(0.0, 0.0)):
        super().__init__(name,vec)
        self.fighterName = name
        self.stateController = StateController()
        self.enemy = None
        self.control = None#recebe a variavel controle


        #self.loadImages = #Tem que upar as imagens do Scorpion
         
    def setEnemy(self,enemyFighter = None):
        self.enemy = enemyFighter
    """def initializeScorpion(self,position,game):
        engine.ImageManager.drawImage(image, self.position, game)"""


class Scorpion(Fighter):
    def __init__(self, name="Scorpion", vec=engine.Vector2(0.0, 0.0)):
        super().__init__(name,vec)
        self.anim = []
        self.i = 0
        self.anim.append(engine.Animation())
        self.anim.append(engine.Animation())
        self.ended = False
        '../res/Background/MainMenu01.png'
        v = []
        i = 1
        while i < 8:
            v.append(engine.Image('../res/Char/Scorpion/' + str(i) + '.png'))
            i = i + 1

        self.anim[0].setFrameList(v)

        i = 1
        while i < 8:
            v.append(engine.Image('../res/Char/Scorpion/Akick' + str(i) + '.png'))
            i = i + 1

        self.anim[1].setFrameList(v)


    def update(self,game = None):
        if self.ended:
            self.i = self.i ^ 1
            self.ended = False
            self.anim[self.i].start()
        print("Flag02")
        self.anim[self.i].update()
        self.ended = True

    def render(self, positionInDisplay=(0.0, 0.0), game=None):
        print("Flag04")
        self.anim[self.i].render(positionInDisplay, game)

