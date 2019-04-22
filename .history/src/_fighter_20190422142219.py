
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
    specialLimit = [4,7]
    victoryLimit = 3
    fatalityLimit = 20
    dizzyLimit = 7

    # indexação
    # moves
    dance = 0
    walk = 1
    jump = 2
    crouch = 3
    # punches
    Apunch = 4 # soco fraco
    Bpunch = 5 # soco forte
    Cpunch = 6 # soco agachado fraco
    Dpunch = 7 # soco agachado forte: gancho
    # kicks
    Akick = 8 # chute fraco
    Bkick = 9 # chute forte
    Ckick = 10 # chute agachado fraco
    Dkick = 11 # chute agachado forte: banda
    # hits
    Ahit = 12 # soco fraco
    Bhit = 13 # chute fraco
    Chit = 14 # soco forte
    Dhit = 15 # chute agrachado fraco
    Ehit = 16 # soco agachado fraco
    Fhit = 17 # chute forte e soco forte agachado (gancho)
    Ghit = 18 # chute agachado forte: banda
    #Hhit = 19 # specialMove
    #fatalityHit = 20 # fatality hit
    # block
    Ablock = 19
    #Bblock = 13
    # special move
    special = 20
    # fatality
    fatality = 24 

    def __init__(self, id, scenario):
        self.fighterId = id
        self.name = self.fighterNames[id]
        self.move = self.fightMoves[id]
        self.combat = self.combatMoves[id] 

        # Position
        self.x = 150+id*500
        if scenario == 1:
            self.y = 350
        elif scenario == 2:
            self.y = 370
        elif scenario == 3:
            self.y = 400
        elif scenario == 4:
            self.y = 370
        elif scenario == 5:
            self.y = 380
        elif scenario == 6:
            self.y = 380
        elif scenario == 7:
            self.y = 360
        elif scenario == 8:
            self.y = 395          


        # Loading sprites
        self.spriteList = []
        # moves
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/dance.png', self.danceLimit)) 
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/walk.png', self.walkLimit))
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/jump.png', self.jumpLimit))
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/crouch.png', self.crouchLimit))
        # Punch sprites
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Apunch.png', self.punchLimit[0]))
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Bpunch.png', self.punchLimit[1]))
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Cpunch.png', self.punchLimit[2]))
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Dpunch.png', self.punchLimit[3]))
        # Kick sprites
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Akick.png', self.kickLimit[0]))
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Bkick.png', self.kickLimit[1]))
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Ckick.png', self.kickLimit[2]))
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Dkick.png', self.kickLimit[3]))
        # Hit sprites
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Ahit.png', self.hitLimit[0])) # soco fraco
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Bhit.png', self.hitLimit[1])) # chute fraco
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Chit.png', self.hitLimit[2])) # soco forte
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Dhit.png', self.hitLimit[3])) # chute agrachado fraco
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Ehit.png', self.hitLimit[4])) # soco agachado fraco
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Fhit.png', self.hitLimit[5])) # chute forte e soco forte agachado (gancho)
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Ghit.png', self.hitLimit[6])) # chute agachado forte: banda
        #self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Hhit.png', self.hitLimit[7])) # specialMove
        # blocking sprites
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Ablock.png', self.blockLimit)) # defesa em pé
        #self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Bblock.png', self.blockLimit)) # defesa agachado

        # special sprite ----------------------------------
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Special.png', self.specialLimit[self.fighterId])) # Especial

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
        self.jumpHeight = 10  # Altura do pulo
        self.jumpCounter = 1  # Contador correspodente à subida e descida do pulo
        self.jumping = False  # Variável de status
        self.frame_jumping = 0
        self.jump_step = 1
        self.end_jump = True

        # Crouch vars
        self.crouching = False  # Variável de status
        self.frame_crouching = 0
        self.crouch_step = 1

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
        self.frame_Cpunching = 0
        self.Cpunch_step = 1
        self.end_Cpunch = True
        self.Dpunching = False
        self.frame_Dpunching = 0
        self.Dpunch_step = 1
        self.end_Dpunch = True        

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
        self.frame_Ckicking = 0
        self.Ckick_step = 1
        self.end_Ckick = True
        self.Dkicking = False
        self.frame_Dkicking = 0
        self.Dkick_step = 1
        self.end_Dkick = True

        # Blocking vars
        self.Ablocking = False
        self.frame_Ablocking = 0
        self.Ablock_step = 1
        self.Bblocking = False

        # Special vars
        self.specialMove = False
        self.end_special = True
        self.frame_special = 0
        self.special_step = 1


        # Hit vars
        self.hit = False
        self.downHit = False
        self.hitName = ""
        self.Ahitting = False
        self.Bhitting = False
        self.Chitting = False
        self.Dhitting = False
        self.Ehitting = False
        self.Fhitting = False
        self.Ghitting = False
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


        # Life Vars
        X_inicio = 37
        X_atual = X_inicio
        X_fim = X_inicio + 327

        self.posFighter()

    def fight(self, time, nextFrame):
        frame_step = 60

        if self.fighterId == 1:
            print("downHit =", self.downHit)
            print("self.hitName = "+self.hitName)

        if not self.jumping:
            # fightMoves = [ ["w", "s", "a", "d"], ["up", "down", "left", "right"] ] -> jump
            if keyPressed(self.move[0]) and not self.hit:
                self.jumping = True
                self.end_jump = False
                self.curr_sprite = self.spriteList[self.jump]
            
            # fightMoves = [ ["w", "s", "a", "d"], ["up", "down", "left", "right"] ] -> right
            elif keyPressed(self.move[3]) and not self.hit: 
                self.curr_sprite = self.spriteList[self.walk]
                self.walking = self.setState()
                self.setEndState()
                self.x += 6
                moveSprite(self.spriteList[self.walk], self.x, self.y, True)
                self.setSprite(self.spriteList[self.walk])
                changeSpriteImage(self.spriteList[self.walk], self.frame_walk)
                if time > nextFrame:
                    # There are 9 frames of animation in each direction
                    self.frame_walk = (self.frame_walk+1) % self.walkLimit
                    # so the modulus 9 allows it to loop
                    nextFrame += frame_step
            
            # fightMoves = [ ["w", "s", "a", "d"], ["up", "down", "left", "right"] ] -> left
            elif keyPressed(self.move[2]) and not self.hit:# SEGUNDA MUDANÇA and not self.jumping:
                self.curr_sprite = self.spriteList[self.walk]
                self.walking = self.setState()
                self.setEndState() 
                self.x -= 6
                moveSprite(self.spriteList[self.walk], self.x, self.y, True)
                self.setSprite(self.spriteList[self.walk])
                changeSpriteImage(self.spriteList[self.walk], self.walkLimit-1-self.frame_walk)
                if time > nextFrame:
                    # There are 9 frames of animation in each direction
                    self.frame_walk = (self.frame_walk+1) % self.walkLimit
                    nextFrame += frame_step

            
            # fightMoves = [ ["w", "s", "a", "d"], ["up", "down", "left", "right"] ] -> crouch
            elif (keyPressed(self.move[1]) and not self.hit) or self.downHit: 
                if  self.end_Cpunch and self.end_Dpunch and self.end_Ckick and self.end_Dkick and not self.hit and not self.downHit:
                    self.curr_sprite = self.spriteList[self.crouch]
                    self.crouching = self.setState()
                    self.setEndState() 
                if time > nextFrame:
                    if self.end_Cpunch and self.end_Dpunch and self.end_Ckick and self.end_Dkick and not self.hit and not self.downHit:
                        moveSprite(self.spriteList[self.crouch], self.x, self.y, True)
                        self.setSprite(self.spriteList[self.crouch])
                        changeSpriteImage(self.spriteList[self.crouch], self.frame_crouching)
                        self.frame_crouching = (self.frame_crouching+self.crouch_step) % self.crouchLimit
                    if self.frame_crouching == self.crouchLimit - 2:
                        self.crouch_step = 0

                        # combatMoves = [["j","n","k","m","l","u","f"],["1","4","2","5","3","0","6"]] -> crouch and jab
                        if ( (keyPressed(self.combat[0]) and self.end_Cpunch) or (not keyPressed(self.combat[0]) and not self.end_Cpunch) ) and (not self.hit) and not self.downHit:
                            self.curr_sprite = self.spriteList[self.Cpunch]
                            self.Cpunching = self.setState()
                            self.setEndState() 
                            self.end_Cpunch = False         
                            if time > nextFrame:
                                moveSprite(self.spriteList[self.Cpunch], self.x, self.y, True)
                                self.setSprite(self.spriteList[self.Cpunch])   
                                changeSpriteImage(self.spriteList[self.Cpunch], self.frame_Cpunching)
                                self.frame_Cpunching = (self.frame_Cpunching+self.Cpunch_step) % (self.punchLimit[2]+1)
                                if (self.frame_Cpunching == self.punchLimit[2]-1):
                                    self.Cpunch_step = -1
                                if (self.frame_Cpunching == self.punchLimit[2]):
                                    self.frame_Cpunching = 0
                                    self.Cpunch_step = 1
                                    self.end_Cpunch = True
                        # combatMoves = [["j","n","k","m","l","u","f"],["1","4","2","5","3","0","6"]] -> crouch and strong punch
                        elif ( (keyPressed(self.combat[1]) and self.end_Dpunch) or (not keyPressed(self.combat[1]) and not self.end_Dpunch) ) and (not self.hit) and not self.downHit:
                            self.curr_sprite = self.spriteList[self.Dpunch]
                            self.Dpunching = self.setState()
                            self.setEndState() 
                            self.end_Dpunch = False         
                            if time > nextFrame:
                                moveSprite(self.spriteList[self.Dpunch], self.x, self.y, True)
                                self.setSprite(self.spriteList[self.Dpunch])   
                                changeSpriteImage(self.spriteList[self.Dpunch], self.frame_Dpunching)
                                self.frame_Dpunching = (self.frame_Dpunching+self.Dpunch_step) % (self.punchLimit[3]+1)
                                if (self.frame_Dpunching == self.punchLimit[3]-1):
                                    self.Dpunch_step = -1
                                if (self.frame_Dpunching == self.punchLimit[3]):
                                    self.frame_Dpunching = 0
                                    self.Dpunch_step = 1
                                    self.end_Dpunch = True
                        # combatMoves = [["j","n","k","m","l","u","f"],["1","4","2","5","3","0","6"]] -> crouch and kick
                        elif ( (keyPressed(self.combat[2]) and self.end_Ckick) or (not keyPressed(self.combat[2]) and not self.end_Ckick) ) and (not self.hit) and not self.downHit: 
                            self.curr_sprite = self.spriteList[self.Ckick]
                            self.Ckicking = self.setState()
                            self.end_Ckick = self.setEndState()
                            if time > nextFrame:
                                moveSprite(self.spriteList[self.Ckick], self.x, self.y, True)
                                self.setSprite(self.spriteList[self.Ckick])
                                changeSpriteImage(self.spriteList[self.Ckick], self.frame_Ckicking)                
                                self.frame_Ckicking = (self.frame_Ckicking+self.Ckick_step) % (self.kickLimit[2]+1)
                                if (self.frame_Ckicking == self.kickLimit[2]-1):
                                    self.Ckick_step = -1
                                if (self.frame_Ckicking == self.kickLimit[2]):
                                    self.frame_Ckicking = 0
                                    self.Ckick_step = 1
                                    self.end_Ckick = True
                        # combatMoves = [["j","n","k","m","l","u","f"],["1","4","2","5","3","0","6"]] -> Crouch and strong kick
                        elif ( (keyPressed(self.combat[3]) and self.end_Dkick) or (not keyPressed(self.combat[3]) and not self.end_Dkick) ) and (not self.hit) and not self.downHit: 
                            self.curr_sprite = self.spriteList[self.Dkick]
                            self.Dkicking = self.setState()
                            self.end_Dkick = self.setEndState()
                            if time > nextFrame:
                                moveSprite(self.spriteList[self.Dkick], self.x, self.y, True)
                                self.setSprite(self.spriteList[self.Dkick])
                                changeSpriteImage(self.spriteList[self.Dkick], self.frame_Dkicking)
                                self.frame_Dkicking = (self.frame_Dkicking+self.Dkick_step) % self.kickLimit[3]
                                if (self.frame_Dkicking == 0):
                                    self.end_Dkick = True
                        
                        #--------------Hit em agachado--------------------
                        #Ehit = 16 # chute agachado fraco
                        #Hhit = 19 # specialMove
                        #BblockHit = 21 hit agachado
                        
                        #Ehit = 16 # chute ou soco agachado fraco
                        elif self.downHit and self.hitName == "Ehit":
                            self.curr_sprite = self.spriteList[self.Ehit]
                            self.Ehitting = self.setState()
                            self.crouching = True
                            moveSprite(self.spriteList[self.Ehit], self.x, self.y, True)
                            self.setSprite(self.spriteList[self.Ehit])
                            changeSpriteImage(self.spriteList[self.Ehit], self.frame_Ehit)
                            if time > nextFrame:
                                self.frame_Ehit = (self.frame_Ehit+self.hit_step) % self.hitLimit[4]
                                if (self.frame_Ehit == self.hitLimit[4] - 1):
                                    self.hit_step = -1
                                if (self.frame_Ehit == 0):
                                    self.hit_step = 1
                                    self.downHit = False
                                
                    nextFrame += 1*frame_step
            
            # combatMoves = [["j","n","k","m","l","u","f"],["1","4","2","5","3","0","6"]] -> jab
            elif ((keyPressed(self.combat[0]) and self.end_Apunch) or ( not keyPressed(self.combat[0]) and not self.end_Apunch) ) and (not self.hit) : 
                print("flag!")
                self.curr_sprite = self.spriteList[self.Apunch]
                self.Apunching = self.setState()
                self.setEndState() 
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
                self.end_Bpunch = self.setEndState()
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
                self.end_Akick = self.setEndState()
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
                self.end_Bkick = self.setEndState()
                if time > nextFrame:
                    moveSprite(self.spriteList[self.Bkick], self.x, self.y, True)
                    self.setSprite(self.spriteList[self.Bkick])
                    changeSpriteImage(self.spriteList[self.Bkick], self.frame_Bkicking)
                    self.frame_Bkicking = (self.frame_Bkicking+self.Bkick_step) % self.kickLimit[1]
                    if (self.frame_Bkicking == 0):
                        self.end_Bkick = True
                        
                    nextFrame += 1*frame_step      
            
            # combatMoves = [["j","n","k","m","l","u","f"],["1","4","2","5","3","0","6"]] -> defesa em pé
            elif keyPressed(self.combat[5]) and not self.hit: 
                self.curr_sprite = self.spriteList[self.Ablock]
                self.Ablocking = self.setState()
                self.setEndState() 
                if time > nextFrame:
                    moveSprite(self.spriteList[self.Ablock], self.x, self.y, True)
                    self.setSprite(self.spriteList[self.Ablock])
                    changeSpriteImage(self.spriteList[self.Ablock], self.frame_Ablocking)
                    self.frame_Ablocking = (self.frame_Ablocking+self.Ablock_step) % self.blockLimit
                    if self.frame_Ablocking == self.blockLimit - 2:
                        self.Ablock_step = 0

                    nextFrame += 1*frame_step
            
            # combatMoves = [["j","n","k","m","l","u","f"],["1","4","2","5","3","0","6"]] -> special move
            elif ((keyPressed(self.combat[4]) and self.end_special) or (not keyPressed(self.combat[4]) and not self.end_special) ) and (not self.hit): 
                print("SpecialMove")  
                self.curr_sprite = self.spriteList[self.special]
                self.specialMove = self.setState()
                self.setEndState() 
                self.end_special = False         
                if time > nextFrame:
                    moveSprite(self.spriteList[self.special], self.x, self.y, True)
                    self.setSprite(self.spriteList[self.special])   
                    changeSpriteImage(self.spriteList[self.special], self.frame_special)
                    self.frame_special = (self.frame_special+self.special_step) % (self.specialLimit[self.fighterId]+1)
                    if (self.frame_special == self.specialLimit[self.fighterId]-1):
                        self.special_step = -1
                    if (self.frame_special == self.specialLimit[self.fighterId]):
                        self.frame_special = 0
                        self.special_step = 1
                        self.end_special = True
                    nextFrame += 1*frame_step
            # just dance :)
            elif not self.hit:
                # reset block (hold type)
                self.frame_Ablocking = 0
                self.Ablock_step = 1
                # reset down (hold type)
                self.frame_crouching = 0
                self.crouch_step = 1
                # reset other movement
                self.frame_walk = self.frame_jumping = 0
                # reset combat frames
                self.frame_Apunching = self.frame_Bpunching = self.frame_Cpunching = self.frame_Dpunching = self.frame_Akicking = self.frame_Bkicking = self.frame_Ckicking = self.frame_Dkicking = 0
                #self.setEndState()
                # start to dance
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


            #--------------Hit em pé--------------------
            #Ehit = 16 # chute agachado fraco
            #Hhit = 19 # specialMove
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
                    self.x -=2
                else: self.x +=2
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

            #Dhit = 15 # soco agrachado fraco
            elif self.hit and self.hitName == "Cpunching":
                self.curr_sprite = self.spriteList[self.Dhit]
                self.Dhitting = self.setState()
                moveSprite(self.spriteList[self.Dhit], self.x, self.y, True)
                self.setSprite(self.spriteList[self.Dhit])
                changeSpriteImage(self.spriteList[self.Dhit], self.frame_Dhit)
                if time > nextFrame:
                    self.frame_Dhit = (self.frame_Dhit+self.hit_step) % self.hitLimit[3]
                    if (self.frame_Dhit == self.hitLimit[3] - 1):
                        self.hit_step = -1
                    if (self.frame_Dhit == 0):
                        self.hit_step = 1
                        self.hit = False
                    nextFrame += 1.2*frame_step            

            #Fhit = 17 # chute forte e soco forte agachado (gancho)
            elif self.hit and self.hitName == "Bkicking":
                self.curr_sprite = self.spriteList[self.Fhit]
                self.Fhitting = self.setState()
                if self.frame_Fhit <= 6:
                    if self.fighterId == 0:
                        self.x -=5
                    else: self.x +=5
                moveSprite(self.spriteList[self.Fhit], self.x, self.y, True)
                self.setSprite(self.spriteList[self.Fhit])
                changeSpriteImage(self.spriteList[self.Fhit], self.frame_Fhit)
                if time > nextFrame:
                    self.frame_Fhit = (self.frame_Fhit+self.hit_step) % self.hitLimit[5]
                    if (self.frame_Fhit == self.hitLimit[5] - 1):
                        self.hit = False
                    nextFrame += 1.2*frame_step 

            #Ghit = 18 # chute agachado forte: banda
            elif self.hit and self.hitName == "Dkicking":
                self.curr_sprite = self.spriteList[self.Ghit]
                self.Ghitting = self.setState()
                moveSprite(self.spriteList[self.Ghit], self.x, self.y, True)
                self.setSprite(self.spriteList[self.Ghit])
                changeSpriteImage(self.spriteList[self.Ghit], self.frame_Ghit)
                if time > nextFrame:
                    self.frame_Ghit = (self.frame_Ghit+self.hit_step) % self.hitLimit[6]
                    if (self.frame_Ghit == self.hitLimit[6] - 1):
                        self.hit = False
                    nextFrame += 1.2*frame_step     

            #blockHit! Defesa em pé.
            elif self.hit and self.hitName == "Ablocking":
                self.curr_sprite = self.spriteList[self.Ablock]
                self.Ablocking = self.setState()
                if time > nextFrame:
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
            

        else:              
             # fightMoves = [ ["w", "s", "a", "d"], ["up", "down", "left", "right"] ] -> jump    
                if time > nextFrame:
                    if keyPressed(self.move[2]):
                        self.x -= 15
                    if keyPressed(self.move[3]):
                        self.x += 15
                    moveSprite(self.spriteList[self.jump], self.x, self.y, True)
                    self.setSprite(self.spriteList[self.jump])
                    self.y -= (self.jumpHeight-self.jumpCounter)*7  
                    changeSpriteImage(self.spriteList[self.jump], self.frame_jumping)
                    if (self.jumpCounter < self.jumpHeight -1 or self.jumpCounter > self.jumpHeight +1): # subindo ou descendo
                        self.frame_jumping = 1
                    if (self.jumpHeight - 1 <= self.jumpCounter <= self.jumpHeight + 1): # quase parado
                        self.frame_jumping = 2
                    if (self.jumpCounter == 2*self.jumpHeight-1):
                        self.frame_jumping = 0
                        self.jumpCounter = -1
                        if clock() > nextFrame:
                            self.setSprite(self.spriteList[self.jump])
                            changeSpriteImage(self.spriteList[self.jump], self.frame_jumping)
                            moveSprite(self.spriteList[self.jump], self.x, self.y, True)
                            self.end_jump = self.setState()# MUDANÇA
                            self.jumping = self.setEndState() #MUDANÇA
                    self.jumpCounter += 2
                    nextFrame += 1*frame_step

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

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

    def isCrouching(self):
        return self.crouching

    def isDancing(self):
        return self.dancing

    def isApunching(self):
        return self.Apunching 

    def isBpunching(self):
        return self.Bpunching 
    
    def isCpunching(self):
        return self.Cpunching 

    def isDpunching(self):
        return self.Dpunching 

    def isAkicking(self):
        return self.Akicking

    def isBkicking(self):
        return self.Bkicking

    def isCkicking(self):
        return self.Ckicking

    def isDkicking(self):
        return self.Dkicking

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
    
    def takeDownHit(self,by):
        self.downHit = True
        print("flag")
        self.hitName = by

    def stopHit(self):
        self.hit = False
        self.hitName = ""
        
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
        # kicks
        self.Akicking = False
        self.Bkicking = False
        self.Ckicking = False
        self.Dkicking = False       
        # punch hits
        self.Ahitting = False
        self.Bhitting = False
        self.Chitting = False
        self.Dhitting = False
        self.Ehitting = False
        self.Fhitting = False
        self.Ghitting = False
        self.Hhitting = False
        # blocks
        self.Ablocking = False
        self.Bblocking = False
        # special move
        self.specialMove = False
        # fatality
        self.fatality = False

        # actual states
        return True

    def setEndState(self):
        self.end_jump = True
        self.end_Apunch = True
        self.end_Bpunch = True
        self.end_Cpunch = True
        self.end_Dpunch = True
        self.end_Akick = True
        self.end_Bkick = True
        self.end_Ckick = True
        self.end_Dkick = True
        self.end_special = True

        return False


    def setSprite(self,sprite):
        for i in range(0,len(self.spriteList)):
            if (not sprite == self.spriteList[i]):
                hideSprite(self.spriteList[i])
        showSprite(sprite)    

    def posFighter(self):
        for i in range(0,len(self.spriteList)):
            moveSprite(self.spriteList[i], self.x, self.y, True)