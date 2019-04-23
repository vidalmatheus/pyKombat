
from pygame_functions import *
import fightScene
import engine
import menu
import LifeBars
import projectile

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
    specialLimit = [12,7]
    hitSpecialLimit = [3,1]
    specialSound = [["iceSound","Hit10"],["ComeHere","IceSound2"]]
    victoryLimit = 3
    fatalityLimit = 20
    dizzyLimit = 7
    deadLimit = 6

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
    Hhit = 19 # specialMove
    # block
    Ablock = 20
    Bblock = 21
    # special move
    special = 22
    # dizzy
    dizzy = 23
    # dead
    dead = 18
    # fatality
    fatality = 25 
    fatalityHit = 26 # fatality hit

    def __init__(self, id, scenario):
        self.fighterId = id
        self.name = self.fighterNames[id]
        self.move = self.fightMoves[id]
        self.combat = self.combatMoves[id]
        self.lostOnce = False
        self.waitingFatality = False
        self.waitTime = [48,240]# '0' é pos derrota e '1' espera do fatality   
        self.wait = 0
        self.isDead = False
        if id == 0:
            self.life = LifeBars.Player1LifeBar("Subzero")
            self.life.setLifePosition([200-self.life.getLifeImage().get_width()/2,10])

        else:
            self.life = LifeBars.Player2LifeBar("Scorpion")
            self.life.setLifePosition([600-self.life.getLifeImage().get_width()/2,10])

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
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/hitSpecial.png', self.hitSpecialLimit[self.fighterId])) # specialMove
        # blocking sprites
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Ablock.png', self.blockLimit)) # defesa em pé
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Bblock.png', self.blockLimit)) # defesa agachado

        # special sprite ----------------------------------
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/Special.png', self.specialLimit[self.fighterId])) # Especial

        # dizzy sprite ----------------------------------
        self.spriteList.append(makeSprite('../res/Char/'+str(self.name)+'/dizzy.png', self.dizzyLimit)) # Dizzy


        self.act()


    def getLife(self):
        return self.life

    def act(self):

        # projétil 
        self.projectileFighter = projectile.Projectile([self.getX(),self.getY()],self.fighterId)
        self.projectileFighter.moveProjectile()

        # Combat control


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
        self.frame_Bblocking = 0
        self.Bblock_step = 1

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
        self.hitSpecial = False
        self.frame_Ahit = 0
        self.frame_Bhit = 0
        self.frame_Chit = 0
        self.frame_Dhit = 0
        self.frame_Ehit = 0
        self.frame_Fhit = 0
        self.frame_Ghit = 0
        self.frame_Hhit = 0
        self.hit_step = 1

        # dizzy vars
        self.dizzing = False
        self.frame_dizzy = 0
        self.dizzy_counter = 1

        # dead vars
        self.deading = False
        self.frame_dead = 0

        self.posFighter()

    def fight(self, time, nextFrame):
        frame_step = 60
        """if self.isDead:
            if self.wait > 0:
                self.wait = self.wait - 1
                self.curr_sprite = self.spriteList[self.Ckick]
                self.Ckicking = self.setState()
                self.crouching = True
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
            elif not self.lostOnce:
                self.isDead = False
                self.lostOnce = True
                self.life.returnLife()
            else:
                """

        # Animação dos projéteis (iceshot e snake)
        if not self.projectileFighter.isProjectileEnded() and self.fighterId == 0:
            self.projectileFighter.drawProjectile(time,nextFrame)
        elif not self.projectileFighter.isProjectileEnded() and self.fighterId == 1:
            if not self.end_special and self.projectileFighter.isProjectileEnded():
                    self.frame_special = 0
                    self.special_step = 1
                    self.end_special = True
                    self.projectileFighter.endProjectile()
            else:
                print("SpecialMove")
                print("self.end_special: " + str(self.end_special))  
                self.curr_sprite = self.spriteList[self.special]
                self.projectileFighter.startProjectile()
                self.projectileFighter.setPos([self.getX(),self.getY()])
                        
                self.specialMove = self.setState()
                self.setEndState() 
                self.end_special = False         
                if time > nextFrame:
                    moveSprite(self.spriteList[self.special], self.x, self.y, True)
                    self.setSprite(self.spriteList[self.special])   
                    changeSpriteImage(self.spriteList[self.special], self.frame_special)
                    self.projectileFighter.drawProjectile(clock(),nextFrame)
                    self.frame_special = (self.frame_special+self.special_step) % (self.specialLimit[self.fighterId]+1)
                    if (self.frame_special == self.specialLimit[self.fighterId]-1):
                        self.special_step = -1
                    if (self.frame_special == self.specialLimit[self.fighterId]):
                        self.frame_special = 0
                        self.special_step = 1
                        self.end_special = True
                        self.projectileFighter.endProjectile()
                    nextFrame += 1*frame_step
            return nextFrame

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
                if  self.end_Cpunch and self.end_Dpunch and self.end_Ckick and self.end_Dkick and not self.hit and not self.downHit and not self.Bblocking:
                    self.curr_sprite = self.spriteList[self.crouch]
                    self.crouching = self.setState()
                    self.setEndState() 
                if time > nextFrame:
                    if self.end_Cpunch and self.end_Dpunch and self.end_Ckick and self.end_Dkick and not self.hit and not self.downHit and not self.Bblocking:
                        moveSprite(self.spriteList[self.crouch], self.x, self.y, True)
                        self.setSprite(self.spriteList[self.crouch])
                        changeSpriteImage(self.spriteList[self.crouch], self.frame_crouching)
                        self.frame_crouching = (self.frame_crouching+self.crouch_step) % self.crouchLimit
                    if self.frame_crouching == self.crouchLimit - 2:
                        self.crouch_step = 0
                        # combatMoves = [["j","n","k","m","l","u","f"],["1","4","2","5","3","0","6"]] -> crouch and jab
                        if ( (keyPressed(self.combat[0]) and self.end_Cpunch) or (not self.end_Cpunch) ) and (not self.hit) and not self.downHit:
                            self.curr_sprite = self.spriteList[self.Cpunch]
                            self.Cpunching = self.setState()
                            self.crouching = True
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
                        elif ( (keyPressed(self.combat[1]) and self.end_Dpunch) or ( not self.end_Dpunch) ) and (not self.hit) and not self.downHit:
                            self.curr_sprite = self.spriteList[self.Dpunch]
                            self.Dpunching = self.setState()
                            self.crouching = True
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
                        elif ( (keyPressed(self.combat[2]) and self.end_Ckick) or ( not self.end_Ckick) ) and (not self.hit) and not self.downHit: 
                            print("Crouch_Kick!")
                            self.curr_sprite = self.spriteList[self.Ckick]
                            self.Ckicking = self.setState()
                            self.crouching = True
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
                        elif ( (keyPressed(self.combat[3]) and self.end_Dkick) or ( not self.end_Dkick) ) and (not self.hit) and not self.downHit: 
                            self.curr_sprite = self.spriteList[self.Dkick]
                            self.Dkicking = self.setState()
                            self.crouching = True
                            self.end_Dkick = self.setEndState()
                            if time > nextFrame:
                                moveSprite(self.spriteList[self.Dkick], self.x, self.y, True)
                                self.setSprite(self.spriteList[self.Dkick])
                                changeSpriteImage(self.spriteList[self.Dkick], self.frame_Dkicking)
                                self.frame_Dkicking = (self.frame_Dkicking+self.Dkick_step) % self.kickLimit[3]
                                if (self.frame_Dkicking == 0):
                                    self.end_Dkick = True
                        
                        # combatMoves = [["j","n","k","m","l","u","f"],["1","4","2","5","3","0","6"]] -> defesa agachado
                        elif keyPressed(self.combat[5]) and not self.hit and not self.downHit: 
                            self.curr_sprite = self.spriteList[self.Bblock]
                            self.Bblocking = self.setState()
                            self.crouching = True
                            self.setEndState() 
                            if time > nextFrame:
                                moveSprite(self.spriteList[self.Bblock], self.x, self.y, True)
                                self.setSprite(self.spriteList[self.Bblock])
                                changeSpriteImage(self.spriteList[self.Bblock], self.frame_Bblocking)
                                self.frame_Bblocking = (self.frame_Bblocking+self.Bblock_step) % self.blockLimit
                                if self.frame_Bblocking == self.blockLimit - 2:
                                    self.Bblock_step = 0      


                        #--------------Hits em agachado--------------------
                        
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

                        #BblockHit = 21 hit agachado
                        elif (self.downHit or self.hit) and self.hitName == "Bblocking":
                            self.curr_sprite = self.spriteList[self.Bblock]
                            self.Bblocking = self.setState()
                            self.crouching = True
                            if time > nextFrame:
                                moveSprite(self.spriteList[self.Bblock], self.x, self.y, True)
                                self.setSprite(self.spriteList[self.Bblock])
                                changeSpriteImage(self.spriteList[self.Bblock], self.frame_Bblocking)
                                self.frame_Bblocking = (self.frame_Bblocking+self.hit_step) % self.blockLimit
                                if self.frame_Bblocking == self.blockLimit - 1:
                                    self.hit_step = -1
                                if self.frame_Bblocking == 1:
                                    self.hit_step = 1
                                    self.hit = False
                                    self.downHit = False

                        elif not self.downHit:
                            self.frame_Bblocking = 0
                            self.Bblock_step = 1
                            self.Bblocking = False
                                            
                    nextFrame += 1*frame_step
            
            # combatMoves = [["j","n","k","m","l","u","f"],["1","4","2","5","3","0","6"]] -> jab
            elif ((keyPressed(self.combat[0]) and self.end_Apunch) or ( not self.end_Apunch) ) and (not self.hit) : 
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
            elif ( (keyPressed(self.combat[1]) and self.end_Bpunch) or ( not self.end_Bpunch) ) and (not self.hit) : 
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
            elif ( (keyPressed(self.combat[2]) and self.end_Akick) or ( not self.end_Akick) ) and (not self.hit): 
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
            elif ( (keyPressed(self.combat[3]) and self.end_Bkick) or ( not self.end_Bkick) ) and (not self.hit): 
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
            elif ((keyPressed(self.combat[4]) and self.end_special) or ( not self.end_special) ) and (not self.hit): 
                if not self.end_special and self.projectileFighter.isProjectileEnded():
                    self.frame_special = 0
                    self.special_step = 1
                    self.end_special = True
                    self.projectileFighter.endProjectile()
                else:
                    print("SpecialMove")
                    print("self.end_special: " + str(self.end_special))  
                    if (self.frame_special == 0): engine.Sound(self.specialSound[self.fighterId][0]).play()
                    self.curr_sprite = self.spriteList[self.special]
                    self.projectileFighter.startProjectile()
                    self.projectileFighter.setPos([self.getX(),self.getY()])
                        
                    self.specialMove = self.setState()
                    self.setEndState()
                    if self.end_special and self.fighterId == 1:
                        self.frame_special = 0
                        self.special_step = 1
                    self.end_special = False         
                    if time > nextFrame:
                        moveSprite(self.spriteList[self.special], self.x, self.y, True)
                        self.setSprite(self.spriteList[self.special])   
                        changeSpriteImage(self.spriteList[self.special], self.frame_special)
                        self.projectileFighter.drawProjectile(clock(),nextFrame)
                        self.frame_special = (self.frame_special+self.special_step) % (self.specialLimit[self.fighterId]+1)
                        if (self.frame_special == self.specialLimit[self.fighterId]-1):
                            self.special_step = -1
                        if (self.frame_special == self.specialLimit[self.fighterId]):
                            self.frame_special = 0
                            self.special_step = 1
                            self.end_special = True
                            self.projectileFighter.endProjectile()
                        nextFrame += 1*frame_step
            # just dance :)
            elif not self.hit :
                # reset block (hold type)
                self.frame_Ablocking = 0
                self.Ablock_step = 1
                self.frame_Bblocking = 0
                self.Bblock_step = 1
                # reset down (hold type)
                self.frame_crouching = 0
                self.crouch_step = 1
                # reset other movement
                self.frame_walk = self.frame_jumping = 0
                # reset combat frames
                self.frame_Apunching = self.frame_Bpunching = self.frame_Cpunching = self.frame_Dpunching = self.frame_Akicking = self.frame_Bkicking = self.frame_Ckicking = self.frame_Dkicking = 0
                self.setEndState()
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

            #Hhit = 19 # specialHit
            elif self.hit and self.hitName == "special":
                if (self.frame_Hhit == 0): engine.Sound(self.specialSound[self.fighterId][1]).play()  
                self.curr_sprite = self.spriteList[self.Hhit]
                self.hitSpecial = self.setState()
                moveSprite(self.spriteList[self.Hhit], self.x, self.y, True)
                if self.fighterId == 0: # subzero
                    self.x += 20
                self.setSprite(self.spriteList[self.Hhit])
                changeSpriteImage(self.spriteList[self.Hhit], self.frame_Hhit)
                if time > nextFrame:
                    self.frame_Hhit = (self.frame_Hhit+self.hit_step) % self.hitSpecialLimit[self.fighterId]
                    if (self.frame_Hhit == self.hitSpecialLimit[self.fighterId] - 1):
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
            # dizzy
            elif self.hitName == "dizzy":
                self.curr_sprite = self.spriteList[self.dizzy]
                self.dizzing = self.setState()
                moveSprite(self.spriteList[self.dizzy], self.x, self.y, True)
                self.setSprite(self.spriteList[self.dizzy])
                changeSpriteImage(self.spriteList[self.dizzy], self.frame_dizzy)
                if time > nextFrame:
                    self.frame_dizzy = (self.frame_dizzy+self.hit_step) % self.dizzyLimit
                    nextFrame += 1.8*frame_step

            # Dead
            elif self.hitName == "dead":
                self.curr_sprite = self.spriteList[self.dead]
                self.deading = self.setState()
                moveSprite(self.spriteList[self.dead], self.x, self.y, True)
                self.setSprite(self.spriteList[self.dead])
                changeSpriteImage(self.spriteList[self.dead], self.frame_dead)
                if time > nextFrame:
                    self.frame_dead = (self.frame_dead+self.hit_step) % self.deadLimit
                    if (self.frame_dead == self.deadLimit - 1):
                        self.frame_dead = 0
                    nextFrame += 1.2*frame_step
            


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

    
        return nextFrame

    def getProjectile(self):
        return self.projectileFighter

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

    def isJumping(self):
        return self.jumping

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

    def isSpecialMove(self):
        return self.specialMove

    def isAblocking(self):
        return self.Ablocking      

    def isBblocking(self):
        return self.Bblocking    
    
    def isHit(self):
        return self.hit

    def ishitSpecial(self):
        return self.hitSpecial

    def isAlive(self):
        return not self.isDead

    def killPlayer(self):
        for i in range(0,len(self.spriteList)):
            killSprite(self.spriteList[i])

    def currentSprite(self):
        return self.curr_sprite

    def takeHit(self,by):
        self.hit = True
        self.hitName = by
        dicionario = {"Apunching":8,"Bpunching":12,"Akicking":10,"Ablocking":0,"Bkicking":15,"Cpunching":6,"Dkicking":10,"special":5}
        if by in dicionario:
            self.life.addDamage(dicionario[by])
            if self.life.isDead():
                pygame.mixer.music.stop()
                engine.Sound("FinishHim").play()
                self.isDead = True
                if not self.lostOnce:
                    self.lostOnce = True
                    self.wait = self.waitTime[0]
                else:
                    self.waitingFatality = True
                    self.wait = self.waitTime[1]

    def takeDownHit(self,by):
        self.downHit = True
        self.hitName = by

    def setHitName(self,by):
        self.hitName = by

    def stopHit(self,by = ""):
        self.hit = False
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
        self.hitSpecial = False
        # blocks
        self.Ablocking = False
        self.Bblocking = False
        # special move
        self.specialMove = False
        # dizzy
        self.dizzing = False
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