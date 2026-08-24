from Main.Algorithms import *
import statistics

turn = 75
large_buffer = 100
bufpark = 4

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
    data = []
    for i in range(5):
        frame = get_frame()
        color = cv(frame)[0][color]
        data.append(color)
        time.sleep(0.01)
    mode = statistics.mode(data)
    return mode

def obstacleMain(tofs, bno, val3, speed, val, sign, turndir):
    tracker = True
    counter = 0
    while tracker:
        color = captureFrame()
        if color is None: 
            while True:
                startPid(tofs, 20, turndir, val, bno)
                
                time.sleep(0.1)

                if captureFrame() is not None: break
                if getDistances(tofs)[turndir]   >= large_buffer:
                    tracker = False
                    break
        else:
            if counter < 2:
                obstacleAvoidance(tofs, bno, val3, speed, val, color)
                counter += 1
            else: pass
            if getDistances(tofs)[turndir]   >= large_buffer: tracker = False
                
    turn(200, sign*25, sign*75, bno)
    return

front_buffer = 7

def parkAlign(tofs, bno, val3, speed, val, sign, turndir, gz_0):
    tracker = True
    counter = 0
    while tracker:
        color = captureFrame()
        if color is None: 
            while True:
                startPid(tofs, 10, turndir, val, bno)
                
                time.sleep(0.1)

                if captureFrame() is not None: break
                if getDistances(tofs)[turndir]   >= large_buffer:
                    tracker = False
                    break
        else:
            if counter < 1:
                obstacleAvoidance(tofs, bno, val3, speed, val, color)
                counter += 1
            else: pass
            if getDistances(tofs)[turndir]   >= large_buffer: tracker = False

    gyroPid(bno, gz_0, 200, val4, 15)
    turn(175, sign*(-30), sign*(-180))
    frame = get_frame()
    if detect_parking(frame) is None: gyroPid(bno, gz_0, 175, val4, None, 1)
    else: 
        parking_detected = False
        while not parking_detected:
            frame = get_frame()
            cx = detect_parking(frame)

            distances = getDistances(tofs)
            front = distances["front"]
            main = distances[turndir]

            if turndir == "left":
                fake = [
                    {"color": "GREEN", "cx":cx}
                ]
                
                if cx is not None: pidcx(val3, cx, 175, "GREEN", fake)

                elif front <= front_buffer or receiveData()[touch_front_right] == 1:
                    interrupt("left", bno)

            if turndir == "right":
                fake = [
                    {"color": "RED", "cx":cx}
                ]
                
                if cx is not None: pidcx(val3, cx, 175, "RED", fake)

                elif front <= front_buffer or receiveData()[touch_front_left] == 1:
                    interrupt("right", bno)

            if main <= bufpark:
                sendCommand(0, 0)
                data = []
                for i in range(5):
                    data.append(getDistances(tofs)[main])
                mean = statistics.mean(data)
                if mean <= bufpark: 
                    while True:
                        park(turndir, sign)


def park(turndir, sign):
    stage = 1
    startPid(tofs, 3, turndir,  val, bno, 125)
    if getDistances(tofs)[turndir]>=18: 
        stopPid()
        startPid(tofs, 23, turndir, val, bno, 150)
        stage = 2
    if getDistances(tofs)[turndir] <= 3 and stage == 2:
        stopPid()
        startPid(tofs, 3, turndir, val, bno, 125)
        stage = 3
    if getDistances(tofs)[turndir] >= 18 and stage == 3:
        stopPid()
        gyroPid(bno, getRot(), 150, val4, None, 4)
        turn(-200, sign*30, sign*(-180), bno)
        wallAlign(tofs, 3, val2, 4)
        quit

#=========================START BUTTON==============================
from gpiozero import Button

switch = Button(5)

#=========================================================================
#==================================MAIN===================================
#=========================================================================
switch.wait_for_press()
print("Starting...")
Run = True
while Run:
    gz_0 = getRot(bno)
    direction = getDirection()
    if(direction == "clockwise"):
        sign = 1
        turndir = "right"
    elif(direction == "counterclockwise"):
        sign = -1
        turndir = "left"

    #Exit parking
    wallAlign(tofs, 3, val2, 4)
    turn(150, sign*30, sign*90)
    turn(150, sign*(-1)*30, sign*(-1)*turn)

    for i in range(12):
        obstacleMain(tofs, bno, val3, 200, val, sign, turndir)

    #Parallel park
    parkAlign(tofs, bno, val3, 200, val, sign, turndir, gz_0)
        







