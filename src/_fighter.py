
from pygame_functions import *
import fightScene
import engine


class Fighter:

    fighterNames = ["Sub-Zero", "Scorpion"]
    fightMoves = [["w", "s", "a", "d"], ["up", "down", "left", "right"]]
    combatMoves = [["j","n","k","m","l","u","f"],["1","4","2","5","3","0","6"]]
    danceLimit = 7
    walkLimit = 9
    punchLimit = [3, 11, 3, 5, 3]
    kLimit = [7, 9, 7, 6, 3]
    hitLimit = [3, 3, 6, 2, 3, 14, 11, 10]
    bLimit = 3
    specialLimit = 4
    victoryLimit = 3
    fatalityLimit = 20
    dizzyLimit = 7

    def __init__(self, id):
        self.fighterId = id
        self.name = self.fighterNames[id]
        self.move = self.fightMoves[id]
        self.combat = self.combatMoves[id] 

        # Position
        self.x = 100+id*600
        self.y = 350

        # Loading sprites
        self.dance = makeSprite('../res/Char/'+str(self.name)+'/dance.png', self.danceLimit)
        self.walk = makeSprite('../res/Char/'+str(self.name)+'/walk.png', self.walkLimit)
        # Punch sprites
        self.Apunch = makeSprite('../res/Char/'+str(self.name)+'/Apunch.png', self.punchLimit[0])
        # Hit sprites
        self.Ahit = makeSprite('../res/Char/'+str(self.name)+'/Ahit.png', self.hitLimit[0]) 

        self.act()

    def act(self):
        # Combat control
        combat = False
        block = False
        alive = False
        fatality = False
        dizzyCounter = 1
        dizzyCounterAux = 1
        fatalityCounter = 8
        fatalityCounterAux = 1

        # Control reflection var
        reflection = False

        # Dance vars
        self.dancing = True
        self.frame_dance = 0
        self.dance_step = 1

        # Walk vars
        self.frame_walk = 0
        self.walking = False  # Variável de status

        # Jump vars
        self.jumpHeight = 5  # Altura do pulo
        self.jumpCounter = 2*self.jumpHeight+1  # Contador correspodente à subida e descida do pulo
        self.jumping = False  # Variável de status

        # Crouch vars
        crouchCounter = 1
        self.crouching = False  # Variável de status
        auxCrouch = 1

        # Spin vars
        spinLeft = False
        spinRight = False
        spin = False  # Variável de status

        # Punch vars
        self.Apunching = False
        self.frame_Apunching = 0
        self.Apunch_step = 1
        self.end_Apunch = True
        self.Bpunching = False
        self.Cpunching = False
        self.Dpunching = False
        self.Epunching = False
        punchingCounter = 1

        # Kick vars
        self.Akicking = False
        self.Bkicking = False
        self.Ckicking = False
        self.Dkicking = False
        self.Ekicking = False
        kickingCounter = 1

        # Blocking vars
        self.Ablocking = False
        self.Bblocking = False
        blockingCounter = 1

        # Special vars
        self.special = False
        specialCounter = 1
        specialCounterAux = self.specialLimit

        # Hit vars
        self.hit = False
        self.hitName = ""
        self.Apunch_hitting = False
        self.frame_Ahit = 0
        self.hit_step = 1
        hitCounter = 1
        comeHere = False

        # Life Vars
        X_inicio = 37
        X_atual = X_inicio
        X_fim = X_inicio + 327

        moveSprite(self.walk, self.x, self.y, True)
        moveSprite(self.dance, self.x, self.y, True)

    def fight(self, time, nextFrame):
        frame_step = 70
        # fightMoves = [ ["w", "s", "a", "d"], ["up", "down", "left", "right"] ] -> right
        if keyPressed(self.move[3]) and not self.hit:
            self.curr_sprite = self.walk
            self.walking = self.setState()
            hideSprite(self.dance)
            hideSprite(self.Apunch)
            hideSprite(self.Ahit)
            self.x += 2.5
            moveSprite(self.walk, self.x, self.y, True)
            showSprite(self.walk)
            changeSpriteImage(self.walk, self.frame_walk)
            if time > nextFrame:
                # There are 9 frames of animation in each direction
                self.frame_walk = (self.frame_walk+1) % self.walkLimit
                # so the modulus 9 allows it to loop
                nextFrame += frame_step

        # fightMoves = [ ["w", "s", "a", "d"], ["up", "down", "left", "right"] ] -> crouch
        elif keyPressed(self.move[1]) and not self.hit:
            # down facing animations are the 1st set
            changeSpriteImage(self.walk, self.frame_walk)

        # fightMoves = [ ["w", "s", "a", "d"], ["up", "down", "left", "right"] ] -> left
        elif keyPressed(self.move[2]) and not self.hit:
            self.curr_sprite = self.walk
            self.walking = self.setState()
            hideSprite(self.dance)
            hideSprite(self.Apunch)
            hideSprite(self.Ahit)
            self.x -= 2.5
            moveSprite(self.walk, self.x, self.y, True)
            showSprite(self.walk)
            changeSpriteImage(self.walk, self.walkLimit-1-self.frame_walk)
            if time > nextFrame:
                # There are 9 frames of animation in each direction
                self.frame_walk = (self.frame_walk+1) % self.walkLimit
                nextFrame += frame_step

        # fightMoves = [ ["w", "s", "a", "d"], ["up", "down", "left", "right"] ] -> jump
        elif keyPressed(self.move[0]) and not self.hit:
            print("JUMP")

        # combatMoves = [["j","n","k","m","l","u","f"],["1","4","2","5","3","0","6"]] -> jab
        elif ( (keyPress(self.combat[0]) and self.end_Apunch) or (not keyPress(self.combat[0]) and not self.end_Apunch) ) and (not self.hit): 
            self.curr_sprite = self.Apunch
            self.Apunching = self.setState()
            self.end_Apunch = False
            hideSprite(self.dance)
            hideSprite(self.walk)
            hideSprite(self.Ahit)
            moveSprite(self.Apunch, self.x, self.y, True)
            showSprite(self.Apunch)
            changeSpriteImage(self.Apunch, self.frame_Apunching)
            if time > nextFrame:
                self.frame_Apunching = (self.frame_Apunching+self.Apunch_step) % self.punchLimit[0]
                if (self.frame_Apunching == self.punchLimit[0]-1):
                    self.Apunch_step = -1
                if (self.frame_Apunching == 0):
                    self.end_Apunch = True
                nextFrame += 1.2*frame_step

        # just dance :)
        elif not self.hit:
            self.frame_Apunching = self.frame_walk = 0
            self.curr_sprite = self.dance
            self.dancing = self.setState()
            hideSprite(self.Apunch)
            hideSprite(self.walk)
            hideSprite(self.Ahit)
            moveSprite(self.dance, self.x, self.y, True)
            showSprite(self.dance)
            changeSpriteImage(self.dance, self.frame_dance)
            if time > nextFrame:
                self.frame_dance = (self.frame_dance+self.dance_step) % self.danceLimit
                if (self.frame_dance == self.danceLimit-1):
                    self.dance_step = -1
                if (self.frame_dance == 0):
                    self.dance_step = 1
                nextFrame += frame_step

        # Ouch! Punch on a face
        elif self.hit and self.hitName == "Apunching":
            self.curr_sprite = self.Ahit
            self.Apunch_hitting = self.setState()
            hideSprite(self.Apunch)
            hideSprite(self.walk)
            hideSprite(self.dance)
            moveSprite(self.Ahit, self.x, self.y, True)
            showSprite(self.Ahit)
            changeSpriteImage(self.Ahit, self.hitLimit[0]-1-self.frame_Ahit)
            if time > nextFrame:
                # There are 8 frames of animation in each direction
                self.frame_Ahit = (self.frame_Ahit+self.hit_step) % self.hitLimit[0]
                if (self.frame_Ahit == self.hitLimit[0] - 1):
                    self.hit_step = -1
                if (self.frame_Ahit == 0):
                    self.hit = False
                nextFrame += 1.6*frame_step

        #tick(120)
        return nextFrame

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def setX(self,X):
        self.x = X
        moveSprite(self.curr_sprite,self.x,self.y,True)

    def setY(self,Y):
        self.y = Y
        moveSprite(self.curr_sprite,self.x,self.y,True)

    def isWalking(self):
        return self.walking

    def isDancing(self):
        return self.dancing
        print(self.walking)

    def isPunching(self):
        return self.Apunching
    
    def isHit(self):
        return self.hit

    def killPlayer(self):
        killSprite(self.walk)
        killSprite(self.dance)

    def currentSprite(self):
        return self.curr_sprite

    def takeHit(self,by):
        self.hit = True
        self.hitName = by
        
    def setState(self):
        # moves
        self.walking = False
        self.dancing = False
        self.jumping = False
        self.crouching = False
        # punches
        self.Apunching = False
        self.Bpunching = False
        self.Cpunching = False
        self.Dpunching = False
        self.Epunching = False
        # kicks
        self.Akicking = False
        self.Bkicking = False
        self.Ckicking = False
        self.Dkicking = False
        self.Ekicking = False        
        # punch hits
        self.Apunch_hitting = False
        # blocks
        self.Ablocking = False
        self.Bblocking = False
        # special move
        self.special = False
        # fatality
        self.fatality = False

        # actual states
        return True

