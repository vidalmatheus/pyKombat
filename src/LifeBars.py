import engine
import pygame

class LifeBar:
    """É a barra de HP dos lutadores"""
    def __init__(self,fighterName = "Scorpion"):
        self.hp = 100
        self.damage = 0
        self.lifeBarImg = engine.Image('../res/' + fighterName + 'lifebar')
        self.lifeUnit = engine.Image('../res/LifeUnity')
        self.unitWidth = self.lifeUnit.getWidth()
        self.pos = [0.0, 0.0]
        self.firstUnitRelativePos = [0.0,0.0]"Posição da posição da primeira unidade de dano"

    def addDamage(self,dmg):
        """Adciona dano ao hp do personagem,se quizer curar basta um numero inteiro negativo"""
        self.hp = self.hp - dmg
        self.damage = self.damage + dmg
    def getDamage(self):
        """Retorna o dano já sofrido pelo personagem"""
        return self.damage
    def returnLife(self):
        """retorna o life para '100' e damage para '0'"""
        self.hp = 100
        self.damage = 0


