
from pygame_functions import *
import fightScene
import engine


class Fighter:

    fighterNames = ["Sub-Zero", "Scorpion"]
    fightMoves = [["w", "s", "a", "d"], ["up", "down", "left", "right"]]
    combatMoves = [["j","n","k","m","l","u","f"],["1","4","2","5","3","0","6"]]
    danceLimit = 7
    walkLimit = 9
    jumpLimit = 3
    crouchLimit = 3
    punchLimit = [3, 11, 3, 5, 3]
    kickLimit = [7, 9, 7, 6, 3]
    hitLimit = [3, 3, 6, 2, 3, 14, 11, 10]
    bLimit = 3
    specialLimit = 4
    victoryLimit = 3
    fatalityLimit = 20
    dizzyLimit = 7

    # indexação
    # moves
    dance = 0
    walk = 1
    #jump = 2
    #crouch = 3
    # punches
    Apunch = 2 # soco fraco
    #Bpunch = 5 # soco forte
    #Cpunch = 6 # soco agachado fraco
    #DPunch = 7 # soco agachado forte: gancho
    # kicks
    Akick = 3 # chute fraco
    #Bkick = 9 # chute forte
    #Ckick = 10 # chute agachado fraco
    #Dkick = 11 # chute agachado forte: banda
    # hits
    Ahit = 4 # soco fraco
    Bhit = 5 # chute fraco
    #Chit = 14 # soco forte
    #Dhit = 15 # chute agrachado fraco
    #Ehit = 16 # soco agachado fraco
    #Fhit = 17 # chute forte e soco forte agachado (gancho)
    #Ghit = 18 # chute agachado forte: banda
    #Hhit = 19 # specialMove
    #fatalityHit = 20 # fatality hit
    # block
    Ablock = 21
    Bblock = 22
    # special move
    special = 23
    # fatality
    fatality = 24 

    def __init__(self, id):
        self.fighterId = id
        self.name = self.fighterNames[id]
        self.move = self.fightMoves[id]
        self.combat = self.combatMoves[id] 

        # Position
        self.x = 100+id*600
        self.y = 350

        # Loading sprites
        self.spriteList = []
        # moves
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/dance.png', self.danceLimit)) 
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/walk.png', self.walkLimit))
        #self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/jump.png', self.jumpLimit))
        #self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/crouch.png', self.crouchLimit))
        # Punch sprites
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Apunch.png', self.punchLimit[0]))
        #self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Bpunch.png', self.punchLimit[1]))
        #self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Cpunch.png', self.punchLimit[2]))
        #self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Dpunch.png', self.punchLimit[3]))
        # Kick sprites
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Akick.png', self.kickLimit[0]))
        #self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Bkick.png', self.kickLimit[1]))
        #self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Ckick.png', self.kickLimit[2]))
        #self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Dkick.png', self.kickLimit[3]))
        # Hit sprites
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Ahit.png', self.hitLimit[0])) # soco fraco
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Bhit.png', self.hitLimit[1])) # chute fraco
        #self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Chit.png', self.hitLimit[2])) # soco forte
        #self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Dhit.png', self.hitLimit[3])) # chute agrachado fraco
        #self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Ehit.png', self.hitLimit[4])) # soco agachado fraco
        #self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Fhit.png', self.hitLimit[5])) # chute forte e soco forte agachado (gancho)
        #self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Ghit.png', self.hitLimit[6])) # chute agachado forte: banda
        #self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Hhit.png', self.hitLimit[7])) # specialMove

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
        self.frame_Akicking = 0
        self.Akick_step = 1
        self.end_Akick = True
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
        self.Ahitting = False
        self.Bhitting = False
        self.Chitting = False
        self.Dhitting = False
        self.Ehitting = False
        self.Fhitting = False
        self.GAhitting = False
        self.Hhitting = False
        self.frame_Ahit = 0
        self.frame_Bhit = 0
        self.hit_step = 1
        hitCounter = 1
        comeHere = False

        # Life Vars
        X_inicio = 37
        X_atual = X_inicio
        X_fim = X_inicio + 327

        self.posFighter()

    def fight(self, time, nextFrame):
        frame_step = 70

        # fightMoves = [ ["w", "s", "a", "d"], ["up", "down", "left", "right"] ] -> right
        if keyPressed(self.move[3]) and not self.hit:
            self.curr_sprite = self.spriteList[self.walk]
            self.walking = self.setState()
            self.x += 2.5
            moveSprite(self.spriteList[self.walk], self.x, self.y, True)
            self.setSprite(self.spriteList[self.walk])
            changeSpriteImage(self.spriteList[self.walk], self.frame_walk)
            if time > nextFrame:
                # There are 9 frames of animation in each direction
                self.frame_walk = (self.frame_walk+1) % self.walkLimit
                # so the modulus 9 allows it to loop
                nextFrame += frame_step

        # fightMoves = [ ["w", "s", "a", "d"], ["up", "down", "left", "right"] ] -> crouch
        elif keyPressed(self.move[1]) and not self.hit:
            print("CROUCH")

        # fightMoves = [ ["w", "s", "a", "d"], ["up", "down", "left", "right"] ] -> left
        elif keyPressed(self.move[2]) and not self.hit:
            self.curr_sprite = self.spriteList[self.walk]
            self.walking = self.setState()
            self.x -= 2.5
            moveSprite(self.spriteList[self.walk], self.x, self.y, True)
            self.setSprite(self.spriteList[self.walk])
            changeSpriteImage(self.spriteList[self.walk], self.walkLimit-1-self.frame_walk)
            if time > nextFrame:
                # There are 9 frames of animation in each direction
                self.frame_walk = (self.frame_walk+1) % self.walkLimit
                nextFrame += frame_step

        # fightMoves = [ ["w", "s", "a", "d"], ["up", "down", "left", "right"] ] -> jump
        elif keyPressed(self.move[0]) and not self.hit:
            print("JUMP")

        # combatMoves = [["j","n","k","m","l","u","f"],["1","4","2","5","3","0","6"]] -> jab
        elif ( (keyPress(self.combat[0]) and self.end_Apunch) or (not keyPressed() and not self.end_Apunch) ) and (not self.hit): 
            self.curr_sprite = self.spriteList[self.Apunch]
            self.Apunching = self.setState()
            self.end_Apunch = False
            moveSprite(self.spriteList[self.Apunch], self.x, self.y, True)
            self.setSprite(self.spriteList[self.Apunch])
            changeSpriteImage(self.spriteList[self.Apunch], self.frame_Apunching)
            if time > nextFrame:
                self.frame_Apunching = (self.frame_Apunching+self.Apunch_step) % self.punchLimit[0]
                if (self.frame_Apunching == self.punchLimit[0]-1):
                    self.Apunch_step = -1
                if (self.frame_Apunching == 0):
                    self.Apunch_step = 1
                    self.end_Apunch = True
                nextFrame += 1.2*frame_step

        # combatMoves = [["j","n","k","m","l","u","f"],["1","4","2","5","3","0","6"]] -> kick
        elif ( (keyPress(self.combat[2]) and self.end_Akick) or (not keyPressed() and not self.end_Akick) ) and (not self.hit): 
            self.curr_sprite = self.spriteList[self.Akick]
            print("frame_kicking = ", self.frame_Akicking)
            self.Akicking = self.setState()
            self.end_Akick = False
            moveSprite(self.spriteList[self.Akick], self.x, self.y, True)
            self.setSprite(self.spriteList[self.Akick])
            changeSpriteImage(self.spriteList[self.Akick], self.frame_Akicking)
            if time > nextFrame:
                self.frame_Akicking = (self.frame_Akicking+self.Akick_step) % self.kickLimit[0]
                if (self.frame_Akicking == self.kickLimit[0]-1):
                    self.Akick_step = -1
                if (self.frame_Akicking == 0):
                    self.Akick_step = 1
                    self.end_Akick = True
                nextFrame += 1.2*frame_step

        # just dance :)
        elif not self.hit:
            self.frame_Apunching = self.frame_walk = 0
            self.curr_sprite = self.spriteList[self.dance]
            self.dancing = self.setState()
            moveSprite(self.spriteList[self.dance], self.x, self.y, True)
            self.setSprite(self.spriteList[self.dance])
            changeSpriteImage(self.spriteList[self.dance], self.frame_dance)
            if time > nextFrame:
                self.frame_dance = (self.frame_dance+self.dance_step) % self.danceLimit
                if (self.frame_dance == self.danceLimit-1):
                    self.dance_step = -1
                if (self.frame_dance == 0):
                    self.dance_step = 1
                nextFrame += frame_step


            #Chit = 14 # soco forte
            #Dhit = 15 # chute agrachado fraco
            #Ehit = 16 # soco agachado fraco
            #Fhit = 17 # chute forte e soco forte agachado (gancho)
            #Ghit = 18 # chute agachado forte: banda
            #Hhit = 19 # specialMove

        # Ouch! Punch on a face (Ahit = 12 # soco fraco)
        elif self.hit and self.hitName == "Apunching":
            self.curr_sprite = self.spriteList[self.Ahit]
            self.Ahitting = self.setState()
            moveSprite(self.spriteList[self.Ahit], self.x, self.y, True)
            self.setSprite(self.spriteList[self.Ahit])
            changeSpriteImage(self.spriteList[self.Ahit], self.frame_Ahit)
            if time > nextFrame:
                # There are 8 frames of animation in each direction
                print("fram_Ahit =",self.frame_Ahit)
                self.frame_Ahit = (self.frame_Ahit+self.hit_step) % self.hitLimit[0]
                if (self.frame_Ahit == self.hitLimit[0] - 1):
                    self.hit_step = -1
                if (self.frame_Ahit == 0):
                    self.hit_step = 1
                    self.hit = False
                nextFrame += 1.6*frame_step
                
        # Ouch! kick on a face (Bhit = 13 # chute fraco)
        elif self.hit and self.hitName == "Akicking":
            self.curr_sprite = self.spriteList[self.Bhit]
            self.Apunch_hitting = self.setState()
            if self.fighterId == 0:
                self.x -=0.8
            else: self.x +=0.8
            moveSprite(self.spriteList[self.Bhit], self.x, self.y, True)
            self.setSprite(self.spriteList[self.Bhit])
            changeSpriteImage(self.spriteList[self.Bhit], self.frame_Bhit)
            if time > nextFrame:
                # There are 8 frames of animation in each direction
                self.frame_Bhit = (self.frame_Bhit+self.hit_step) % self.hitLimit[1]
                if (self.frame_Bhit == self.hitLimit[1] - 1):
                    self.hit_step = -1
                if (self.frame_Bhit == 0):
                    self.hit_step = 1
                    self.hit = False
                nextFrame += 1.6*frame_step

        tick(120)
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

    def isApunching(self):
        return self.Apunching 
    
    def isAkicking(self):
        return self.Akicking
    
    def isHit(self):
        return self.hit

    def killPlayer(self):
        for i in range(0,len(self.spriteList)):
            killSprite(self.spriteList[i])

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
        self.Ahitting = False
        self.Bhitting = False
        self.Chitting = False
        self.Dhitting = False
        self.Ehitting = False
        self.Fhitting = False
        self.GAhitting = False
        self.Hhitting = False
        # blocks
        self.Ablocking = False
        self.Bblocking = False
        # special move
        self.special = False
        # fatality
        self.fatality = False

        # actual states
        return True

    def setSprite(self,sprite):
        for i in range(0,len(self.spriteList)):
            if (not sprite == self.spriteList[i]):
                hideSprite(self.spriteList[i])
        showSprite(sprite)    

    def posFighter(self):
        for i in range(0,len(self.spriteList)):
            moveSprite(self.spriteList[i], self.x, self.y, True)