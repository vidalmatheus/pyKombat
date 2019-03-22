import engine

"""Usa a classe GameObject como superClasse e veja as classes Animation,AnimationManager e Transform"""
"""criado um condigo pra facilitar os testes renderizados,então pra testar vai ter que criar vc mesmo,
susar a classe Game e Camera pode ajudar"""

class Fighter(engine.GameObject):
    def __init__(self, name="object", vec=Vector2(0.0, 0.0)):
        super().__init__(name,vec)
        self.fighterName = name
        self.position = vec
        #self.loadImages = #Tem que upar as imagens do Scorpion
         
    
    def initializeScorpion(self,position,game):
        engine.ImageManager.drawImage(image, self.position, game)        





