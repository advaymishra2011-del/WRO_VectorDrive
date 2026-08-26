from Main.Algorithms import *
import statistics

center_stop = threading.Event()
center_thread = None

val5 = [4, 0.001, 0.001]

def center_worker(switch, tofs, speed, gains):
    state = {
        "integral": 0,
        "last_error": 0,
        "last_time": time.monotonic()
    }

    while not switch.is_set():

        distances = getDistances(tofs)

        left = distances["left"]
        right = distances["right"]

        if left is None or right is None:
            time.sleep(0.01)
            continue

        # Goal: left == right
        error = left - right

        now = time.monotonic()
        dt = max(now - state["last_time"], 0.001)
        state["last_time"] = now

        pid = pid_step(error, gains, state, dt)

        pid = max(-30, min(30, pid))

        sendCommand(speed, pid)

        time.sleep(0.01)

    sendCommand(0, 0)


def startCenterPID(tofs, speed, gains):
    global center_thread

    if center_thread and center_thread.is_alive():
        return

    center_stop.clear()

    center_thread = threading.Thread(
        target=center_worker,
        args=(center_stop, tofs, speed, gains),
        daemon=True
    )

    center_thread.start()


def stopCenterPID():
    global center_thread

    center_stop.set()

    if center_thread and center_thread.is_alive():
        center_thread.join()

    center_thread = None


startCenterPID(tofs, 200, val5)
distances = getDistances(tofs)
left = distances["left"]
right = distances["right"]

jump = left - right

contin = False
while (contin == False):
    if abs(jump) >= 50:
        dataleft = []
        dataright = []

        for i in range(5):
            dist = getDistances(tofs)
            L = dist["left"]
            R = dist["right"]
            if L is not None: dataleft.append(L)
            if R is not None: dataright.append(R)
        if dataleft != []: leftmean = statistics.mean(dataleft)
        if dataright != []: rightmean = statistics.mean(dataright)

        jump_verify = leftmean - rightmean
        if abs(jump_verify) >= 30:
            contin = True

        if contin == True:
            if jump < 0:
                turndir = "Right"
                sign  = 1
            elif jump > 0:
                turndir = "left"
                sign = -1
    time.sleep(0.05)
stopCenterPID()
turn(200, sign*25, sign*85)
run = True
counter = 0
while run:
    startCenterPID(tofs, 200, val5)
    distances = getDistances(tofs)
    left = distances["left"]
    right = distances["right"]

    jump = left - right

    contin = False
    while (contin == False):
        if abs(jump) >= 50:
            dataleft = []
            dataright = []

            for i in range(5):
                dist = getDistances(tofs)
                L = dist["left"]
                R = dist["right"]
                if L is not None: dataleft.append(L)
                if R is not None: dataright.append(R)
            if dataleft != []: leftmean = statistics.mean(dataleft)
            if dataright != []: rightmean = statistics.mean(dataright)

            jump_verify = leftmean - rightmean
            if abs(jump_verify) >= 30:
                contin = True

        time.sleep(0.05)
    stopCenterPID()
    turn(200, sign*25, sign*85)
    counter+=1
    if counter == 11:
        run = False
        break

quit




    
