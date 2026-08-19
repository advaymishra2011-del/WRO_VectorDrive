from Main.main import *

def getDirection():
    lef = getDistances(tofs)["left"]
    rig = getDistances(tofs)["right"]
    if lef<rig:
        direction = "clockwise"
    elif rig<lef:
        direction = "counterclockwise"
    while(lef1 == rig1):
        lef1 = getDistances(tofs)["left"]
        rig1 = getDistances(tofs)["right"]
        if lef1<rig1:
            direction = "clockwise"
        elif rig1<lef1:
            direction = "counterclockwise"
    return direction

def captureFrame():
    pass

#Algorithm
Laps = False
while Laps:
    direction = getDirection()
    if(direction == "clockwise"):
        sign = 1
    elif(direction == "counterclockwise"):
        sign = -1
    wallAlign(tofs, 3, val2, 4)
    turn(150, sign*30, sign*90)
    turn(150, sign*(-1)*30, sign*(-1)*45)
    obstacleAvoidance(tofs, bno, val3, 200, val)
    turn(200, sign*15, sign*90, bno)
    for i in range(11):
        for i in range(2):
            obstacleAvoidance(tofs, bno, val3, 200, val)
        turn(200, sign*15, sign*90, bno)







