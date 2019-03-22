import engine
import fighter
class TesteScene(engine.GameScene):
    def __init__(self,game = engine.Game()):
        super().__init__(game)
        print("Flag01")
        figh = fighter.Scorpion()
        print("Flag100")
        self.gameObjectList.append(figh)
        print("Flag200")
game = engine.Game()
testeScene = TesteScene(game)
print("Flag00")
testeScene.startScene()
print("Flag400")

game.start()

testeScene.updateScene()