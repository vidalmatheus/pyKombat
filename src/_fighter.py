
from pygame_functions import *
import fightScene
import engine
import menu


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
    blockLimit = 3
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
    Bpunch = 3 # soco forte
    #Cpunch = 6 # soco agachado fraco
    #DPunch = 7 # soco agachado forte: gancho
    # kicks
    Akick = 4 # chute fraco
    Bkick = 5 # chute forte
    #Ckick = 10 # chute agachado fraco
    #Dkick = 11 # chute agachado forte: banda
    # hits
    Ahit = 6 # soco fraco
    Bhit = 7 # chute fraco
    Chit = 8 # soco forte
    #Dhit = 15 # chute agrachado fraco
    #Ehit = 16 # soco agachado fraco
    Fhit = 9 # chute forte e soco forte agachado (gancho)
    #Ghit = 18 # chute agachado forte: banda
    #Hhit = 19 # specialMove
    #fatalityHit = 20 # fatality hit
    # block
    Ablock = 10
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
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Bpunch.png', self.punchLimit[1]))
        #self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Cpunch.png', self.punchLimit[2]))
        #self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Dpunch.png', self.punchLimit[3]))
        # Kick sprites
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Akick.png', self.kickLimit[0]))
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Bkick.png', self.kickLimit[1]))
        #self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Ckick.png', self.kickLimit[2]))
        #self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Dkick.png', self.kickLimit[3]))
        # Hit sprites
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Ahit.png', self.hitLimit[0])) # soco fraco
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Bhit.png', self.hitLimit[1])) # chute fraco
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Chit.png', self.hitLimit[2])) # soco forte
        #self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Dhit.png', self.hitLimit[3])) # chute agrachado fraco
        #self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Ehit.png', self.hitLimit[4])) # soco agachado fraco
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Fhit.png', self.hitLimit[5])) # chute forte e soco forte agachado (gancho)
        #self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Ghit.png', self.hitLimit[6])) # chute agachado forte: banda
        #self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Hhit.png', self.hitLimit[7])) # specialMove
        # blocking sprites
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Ablock.png', self.blockLimit)) # defesa em pé
        #self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Bblock.png', self.blockLimit)) # defesa agachado

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
        self.frame_Bpunching = 0
        self.Bpunch_step = 1
        self.end_Bpunch = True
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
        self.frame_Bkicking = 0
        self.Bkick_step = 1
        self.end_Bkick = True
        self.Ckicking = False
        self.Dkicking = False
        self.Ekicking = False
        kickingCounter = 1

        # Blocking vars
        self.Ablocking = False
        self.frame_Ablocking = 0
        self.Ablock_step = 1
        self.Bblocking = False
        blockingCounter = 1

        # Special vars
        self.special = False
        self.end_special = True
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
        self.frame_Chit = 0
        self.frame_Dhit = 0
        self.frame_Ehit = 0
        self.frame_Fhit = 0
        self.frame_Ghit = 0
        self.frame_Hhit = 0
        self.hit_step = 1
        hitCounter = 1
        comeHere = False

        # Life Vars
        X_inicio = 37
        X_atual = X_inicio
        X_fim = X_inicio + 327

        self.posFighter()

    def fight(self, time, nextFrame):
        frame_step = 65

        # fightMoves = [ ["w", "s", "a", "d"], ["up", "down", "left", "right"] ] -> right
        if keyPressed(self.move[3]) and not self.hit:
            self.curr_sprite = self.spriteList[self.walk]
            self.walking = self.setState()
            self.x += 3.5
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
            self.x -= 3.5
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
        elif ( (keyPressed(self.combat[0]) and self.end_Apunch) or (not keyPressed(self.combat[0]) and not self.end_Apunch) ) and (not self.hit) : 
            self.curr_sprite = self.spriteList[self.Apunch]
            self.Apunching = self.setState()
            self.end_Apunch = False         
            if time > nextFrame:
                moveSprite(self.spriteList[self.Apunch], self.x, self.y, True)
                self.setSprite(self.spriteList[self.Apunch])   
                changeSpriteImage(self.spriteList[self.Apunch], self.frame_Apunching)
                self.frame_Apunching = (self.frame_Apunching+self.Apunch_step) % (self.punchLimit[0]+1)
                if (self.frame_Apunching == self.punchLimit[0]-1):
                    self.Apunch_step = -1
                if (self.frame_Apunching == self.punchLimit[0]):
                    self.frame_Apunching = 0
                    self.Apunch_step = 1
                    self.end_Apunch = True
                nextFrame += 1*frame_step

        # combatMoves = [["j","n","k","m","l","u","f"],["1","4","2","5","3","0","6"]] -> strong punch
        elif ( (keyPressed(self.combat[1]) and self.end_Bpunch) or (not keyPressed(self.combat[1]) and not self.end_Bpunch) ) and (not self.hit) : 
            self.curr_sprite = self.spriteList[self.Bpunch]
            self.Bpunching = self.setState()
            self.end_Bpunch = False
            if time > nextFrame:
                moveSprite(self.spriteList[self.Bpunch], self.x, self.y, True)
                self.setSprite(self.spriteList[self.Bpunch])                
                changeSpriteImage(self.spriteList[self.Bpunch], self.frame_Bpunching)
                self.frame_Bpunching = (self.frame_Bpunching+self.Bpunch_step) % self.punchLimit[1]
                if (self.frame_Bpunching == 0):
                    self.end_Bpunch = True
                nextFrame += 1*frame_step

        # combatMoves = [["j","n","k","m","l","u","f"],["1","4","2","5","3","0","6"]] -> kick
        elif ( (keyPressed(self.combat[2]) and self.end_Akick) or (not keyPressed(self.combat[2]) and not self.end_Akick) ) and (not self.hit): 
            self.curr_sprite = self.spriteList[self.Akick]
            self.Akicking = self.setState()
            self.end_Akick = False
            if time > nextFrame:
                moveSprite(self.spriteList[self.Akick], self.x, self.y, True)
                self.setSprite(self.spriteList[self.Akick])
                changeSpriteImage(self.spriteList[self.Akick], self.frame_Akicking)                
                self.frame_Akicking = (self.frame_Akicking+self.Akick_step) % (self.kickLimit[0]+1)
                if (self.frame_Akicking == self.kickLimit[0]-1):
                    self.Akick_step = -1
                if (self.frame_Akicking == self.kickLimit[0]):
                    self.frame_Akicking = 0
                    self.Akick_step = 1
                    self.end_Akick = True 
                nextFrame += 1*frame_step
        
        # combatMoves = [["j","n","k","m","l","u","f"],["1","4","2","5","3","0","6"]] -> strong kick
        elif ( (keyPressed(self.combat[3]) and self.end_Bkick) or (not keyPressed(self.combat[3]) and not self.end_Bkick) ) and (not self.hit): 
            self.curr_sprite = self.spriteList[self.Bkick]
            self.Bkicking = self.setState()
            self.end_Bkick = False
            if time > nextFrame:
                moveSprite(self.spriteList[self.Bkick], self.x, self.y, True)
                self.setSprite(self.spriteList[self.Bkick])
                changeSpriteImage(self.spriteList[self.Bkick], self.frame_Bkicking)
                self.frame_Bkicking = (self.frame_Bkicking+self.Bkick_step) % self.kickLimit[1]
                if (self.frame_Bkicking == 0):
                    self.end_Bkick = True
                    
                nextFrame += 1*frame_step

        # combatMoves = [["j","n","k","m","l","u","f"],["1","4","2","5","3","0","6"]] -> special move
        elif ( (keyPressed(self.combat[4]) and self.end_special) or (not keyPressed(self.combat[4]) and not self.end_special) ) and (not self.hit): 
            print("SpecialMove")        
        
        # combatMoves = [["j","n","k","m","l","u","f"],["1","4","2","5","3","0","6"]] -> defesa em pé
        elif keyPressed(self.combat[5]) and not self.hit: 
            self.curr_sprite = self.spriteList[self.Ablock]
            self.Ablocking = self.setState()
            if time > nextFrame:
                moveSprite(self.spriteList[self.Ablock], self.x, self.y, True)
                self.setSprite(self.spriteList[self.Ablock])
                changeSpriteImage(self.spriteList[self.Ablock], self.frame_Ablocking)
                self.frame_Ablocking = (self.frame_Ablocking+self.Ablock_step) % self.blockLimit
                print("frame_Ablocking = ", self.frame_Ablocking)
                if self.frame_Ablocking == self.blockLimit - 2:
                    self.Ablock_step = 0
                #if self.frame_Ablocking == 0:
                    
                nextFrame += 1*frame_step

        # just dance :)
        elif not self.hit:
            # reset block
            self.frame_Ablocking = 0
            self.Ablock_step = 1
            self.frame_Apunching = self.frame_walk = 0
            self.curr_sprite = self.spriteList[self.dance]
            self.dancing = self.setState()
            if time > nextFrame:
                moveSprite(self.spriteList[self.dance], self.x, self.y, True)
                self.setSprite(self.spriteList[self.dance])
                changeSpriteImage(self.spriteList[self.dance], self.frame_dance)                
                self.frame_dance = (self.frame_dance+self.dance_step) % self.danceLimit
                if (self.frame_dance == self.danceLimit-1):
                    self.dance_step = -1
                if (self.frame_dance == 0):
                    self.dance_step = 1
                nextFrame += frame_step


        
        #Dhit = 15 # chute agrachado fraco
        #Ehit = 16 # soco agachado fraco
        #Fhit = 17 # chute forte e soco forte agachado (gancho)
        #Ghit = 18 # chute agachado forte: banda
        #Hhit = 19 # specialMove
        #AblockHit = 20 hit em pé
        #BblockHit = 21 hit agachado
        
        # Ouch! Punch on a face (Ahit = 12 # soco fraco)
        elif self.hit and self.hitName == "Apunching":
            self.curr_sprite = self.spriteList[self.Ahit]
            self.Ahitting = self.setState()
            moveSprite(self.spriteList[self.Ahit], self.x, self.y, True)
            self.setSprite(self.spriteList[self.Ahit])
            changeSpriteImage(self.spriteList[self.Ahit], self.frame_Ahit)
            if time > nextFrame:
                self.frame_Ahit = (self.frame_Ahit+self.hit_step) % self.hitLimit[0]
                if (self.frame_Ahit == self.hitLimit[0] - 1):
                    self.hit_step = -1
                if (self.frame_Ahit == 0):
                    self.hit_step = 1
                    self.hit = False
                nextFrame += 1.2*frame_step
                
        # Ouch! kick on a face (Bhit = 13 # chute fraco)
        elif self.hit and self.hitName == "Akicking":
            self.curr_sprite = self.spriteList[self.Bhit]
            self.Bhitting = self.setState()
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
                nextFrame += 1.2*frame_step

        # Ouch! combo punch (Chit = 14 # soco forte)
        elif self.hit and self.hitName == "Bpunching":
            self.curr_sprite = self.spriteList[self.Chit]
            self.Chitting = self.setState()
            if self.fighterId == 0:
                self.x -=0.1
            else: self.x +=0.1
            moveSprite(self.spriteList[self.Chit], self.x, self.y, True)
            self.setSprite(self.spriteList[self.Chit])
            changeSpriteImage(self.spriteList[self.Chit], self.frame_Chit)
            if time > nextFrame:
                self.frame_Chit = (self.frame_Chit+self.hit_step) % self.hitLimit[2]
                if (self.frame_Chit == self.hitLimit[2] - 1):
                    self.hit_step = -1
                if (self.frame_Chit == 0):
                    self.hit_step = 1
                    self.hit = False
                nextFrame += 1.2*frame_step

        #Fhit = 17 # chute forte e soco forte agachado (gancho)
        elif self.hit and self.hitName == "Bkicking":
            self.curr_sprite = self.spriteList[self.Fhit]
            self.Fhitting = self.setState()
            if self.frame_Fhit <= 6:
                if self.fighterId == 0:
                    self.x -=3
                else: self.x +=3
            moveSprite(self.spriteList[self.Fhit], self.x, self.y, True)
            self.setSprite(self.spriteList[self.Fhit])
            changeSpriteImage(self.spriteList[self.Fhit], self.frame_Fhit)
            if time > nextFrame:
                self.frame_Fhit = (self.frame_Fhit+self.hit_step) % self.hitLimit[5]
                if (self.frame_Fhit == self.hitLimit[5] - 1):
                    self.hit = False
                nextFrame += 1.2*frame_step     

        #blockHit! Defesa em pé.
        elif self.hit and self.hitName == "Ablocking":
            self.curr_sprite = self.spriteList[self.Ablock]
            self.Ablocking = self.setState()
            if time > nextFrame:
                print("frame_Ablocking = ",self.frame_Ablocking)
                moveSprite(self.spriteList[self.Ablock], self.x, self.y, True)
                self.setSprite(self.spriteList[self.Ablock])
                changeSpriteImage(self.spriteList[self.Ablock], self.frame_Ablocking)
                self.frame_Ablocking = (self.frame_Ablocking+self.hit_step) % self.blockLimit
                if self.frame_Ablocking == self.blockLimit - 1:
                    self.hit_step = -1
                if self.frame_Ablocking == 1:
                    self.hit_step = 1
                    self.hit = False
                nextFrame += 1*frame_step
                 
        

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

    def isBpunching(self):
        return self.Bpunching 

    def isAkicking(self):
        return self.Akicking

    def isBkicking(self):
        return self.Bkicking

    def isAblocking(self):
        return self.Ablocking        
    
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