from pygame_functions import *

screenSize(800, 500,"pyKombat")
setBackgroundImage("../res/Background/Scenario1.png")


x = 100
y = 350
# links.gif contains 32 separate frames of animation.
walk = makeSprite("../res/Char/Sub-Zero/walk.png", 9)
dance = makeSprite("../res/Char/Sub-Zero/dance.png", 7)


moveSprite(walk, x, y, True)
moveSprite(dance, x, y, True)


nextFrame = clock()
frame_walk = -1
frame_dance = -1
aux = 1
step = 0
step_back = 0
while True:
    # We only animate our character every 80ms.
    print(clock(),nextFrame)
    if clock() > nextFrame:
        # There are 8 frames of animation in each direction
        frame_dance = (frame_dance+aux) % 7
        if (frame_dance == 6): aux = -1
        if (frame_dance == 0): aux = 1
        frame_walk = (frame_walk+1) % 9
        nextFrame += 80                             # so the modulus 8 allows it to loop

    if keyPressed("right"):
        #hideSprite(dance)
        showSprite(walk)
        x += 1.5
        # 0*8 because right animations are the 0th set in the sprite sheet
        changeSpriteImage(walk, frame_walk)
        moveSprite(walk, x, y, True)

    elif keyPressed("down"):
        # down facing animations are the 1st set
        changeSpriteImage(walk, frame_walk)

    elif keyPressed("left"):
        hideSprite(dance)
        showSprite(walk)
        x -= 1.5
        # 0*8 because right animations are the 0th set in the sprite sheet
        changeSpriteImage(walk, 7-frame_walk)
        moveSprite(walk, x, y, True)

    elif keyPressed("up"):
        changeSpriteImage(walk, frame_walk)

    else:
        hideSprite(walk)
        showSprite(dance)
        changeSpriteImage(dance, frame_dance)  # the static facing front look
        moveSprite(dance, x, y, True)

    tick(120)

#endWait()