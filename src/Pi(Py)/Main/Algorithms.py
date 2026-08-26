import time
import cv2
#from flask import config
import numpy as np
import serial
import board
import busio
import threading

from picamera2 import Picamera2
# from adafruit_bno08x.i2c import BNO08X_I2C
import adafruit_tcs34725
import adafruit_tca9548a
import adafruit_vl53l0x


from Camera.CVcam import get_frame, cv, detect_parking
from Pico import sendCommand, receiveData
from Sensing.ToF import getDistances
from Sensing.IMU import getRot, angleDiff
#from Sensing.TCS import getColor

#NOTES: 
# - gz represents yaw

#==================== PID VALUES ======================
val2 = [3, 0.001, 0.001] #PID for back
val = [4, 0.001, 0.001] #PID for tofs
val3 = [4, 0.001, 0.001] #PID for cx
val4 = [3, 0.001, 0.001] #Gyro PID


#-----------------------------------------------STATE HELPER (PID variables)-------------------------
def pid_step(error, gains, state, dt):
    dt = max(dt, 0.001)


    state["integral"] += error*dt

    derivative = (error - state["last_error"])/dt
    state["last_error"] = error

    return (
        gains[0] * error +
        gains[1] * state["integral"] +
        gains[2] * derivative
    )


#-------------------------------------------------------CV CONFIG-------------------------------------------------------
# 2. Optimized HSV Boundaries (Tweak based on your room's light)
LOWER_GREEN = np.array([35, 60, 60])
UPPER_GREEN = np.array([85, 255, 255])

# Red spans across the HSV 0/180 boundary
LOWER_RED1, UPPER_RED1 = np.array([0, 70, 70]), np.array([10, 255, 255])
LOWER_RED2, UPPER_RED2 = np.array([170, 70, 70]), np.array([180, 255, 255])

RESOLUTION = (640, 480)

kernel = np.ones((3, 3), np.uint8)

picam2 = Picamera2()

config = picam2.create_video_configuration(
    main={"size": RESOLUTION, "format": "RGB888"}
)

picam2.configure(config)
picam2.start()  # Initialize the camera configuration


#-----------------------------------------------------SENSOR SETUP-----------------------------------------------------
#================================PICO===========================
pico = serial.Serial(
    "/dev/serial0",
    baudrate=115200,
    timeout=0.1
)

touch_front_left = 2
touch_front_right = 3
touch_rear_left = 0
touch_rear_right = 1

#================================TCS===============================

i2c = board.I2C()

tcs = adafruit_tcs34725.TCS34725(i2c)


#=================================ToF=============================


# Main Pi I²C bus
i2c = board.I2C()

# TCA9548A multiplexer
tca = adafruit_tca9548a.TCA9548A(i2c)

# VL53L0X sensors
tofs = {
    "front": adafruit_vl53l0x.VL53L0X(tca[0]),
    "left": adafruit_vl53l0x.VL53L0X(tca[1]),
    "right": adafruit_vl53l0x.VL53L0X(tca[2]),
    "rear_left": adafruit_vl53l0x.VL53L0X(tca[3]),
    "rear_right": adafruit_vl53l0x.VL53L0X(tca[4])
}


#---------------------------------------------MOVEMENT PROTOCOLS--------------------------------------
#==========================BACK ALIGN========================

def mod(x):
    if x<0:
        return -x
    elif x>=0:
        return x
    else:
        return None

def backPID(speed, tofs, gains, state):
    sendCommand(speed, 0)
    
    distances = getDistances(tofs)
    left = distances["rear_left"]
    right = distances["rear_right"]
    
    if speed<0:
        error = left - right
    elif speed>=0:
        error = right - left
    # integral += error
    # derivative = error - last_error
    # last_error = error

    now = time.monotonic()
    dt = now - state["last_time"]
    state["last_time"] = now

    pid = pid_step(error, gains, state, dt)

    sendCommand(speed, pid)
    time.sleep(0.01)

def wallAlign(tofs, dist, gains, buffer):

    state = {
        "integral": 0,
        "last_error": 0,
        "last_time": time.monotonic()
    }

    distances = getDistances(tofs)
    left = distances["rear_left"]
    right = distances["rear_right"]
    if left is not None or right is not None:
        gap = min(left, right)

    
    while(gap>=dist):
        backPID(-100, tofs, gains, state)
        data = receiveData()
        if data is not None:
            if data[touch_rear_left] == 1:
                turn(100, 20, 15)
            elif data[touch_rear_right] == 1:
                turn(100, -20, -15)

        distances = getDistances(tofs)
        left = distances["rear_left"]
        right = distances["rear_right"]
        gap = min(left, right)

    n = 30
    while mod(left-right) >= buffer:
        for i in range(n):
            backPID(100, tofs, gains, state)
        for i in range(n):
            backPID(-100, tofs, gains, state)

        left = getDistances(tofs)["rear_left"]
        right = getDistances(tofs)["rear_right"]

#=================================WALL FOLLOW=====================================

stop_switch = threading.Event()
worker_thread = None


def loop_worker(switch, tofs, dist, side, gains, speed):
    state = {
        "integral": 0,
        "last_error": 0,
        "last_time": time.monotonic()
    }

    gz = 0
    gz_set = getRot()
    while not switch.is_set():
        sendCommand(speed, 0)
        tof = getDistances(tofs)[side]

        if side == "left":
            error = dist - tof
        elif side == "right":
            error = tof - dist

        # derivative = error - last_error
        # integral += error
        # last_error = error

        now = time.monotonic()
        dt = now - state["last_time"]
        state["last_time"] = now

        pid = pid_step(error, gains, state, dt)

        gz = mod(getRot() - gz_set)

        if gz < 31:
            sendCommand(speed, pid)
        elif gz > 31:
            sendCommand(speed, 0)
            time.sleep(0.05)

        touch = receiveData()
        
        if touch is not None:
            if touch[touch_front_right] == 1:
                interrupt("left")

            elif touch[touch_front_left] == 1:
                interrupt("right")
        
        time.sleep(0.05)  
        


def startPid(tofs, dist, side, gains, speed=150):
    global worker_thread
    if worker_thread and worker_thread.is_alive():
        return
        
    stop_switch.clear()
    worker_thread = threading.Thread(target=loop_worker, args=(stop_switch, tofs, dist, side, gains, speed), daemon=True)
    worker_thread.start()


def stopPid():
    global worker_thread
    stop_switch.set()
    if worker_thread:
        worker_thread.join()

#=============================STEER=======================================
# def turn(speed, sharpness, deg):
#     gz = 0
#     gz_set = getRot()
#     sendCommand(speed, sharpness)
#     if deg > 0:
#         while gz < deg:
#             gz = getRot() - gz_set

#             if receiveData()[touch_front_right] == 1: interrupt("left")
#             elif receiveData()[touch_front_left] == 1: interrupt("right")
                    
#             time.sleep(0.005)
#     elif deg < 0:
#         while gz > deg:
#             gz = getRot() - gz_set

#             if receiveData()[touch_front_right] == 1: interrupt("left")
#             elif receiveData()[touch_front_left] == 1: interrupt("right")
                    
#             time.sleep(0.005)
#     sendCommand(0, 0)

def turn(speed, sharpness, deg, check = True):
    start_yaw = getRot()

    sendCommand(speed, sharpness)

    while True:
        current_yaw = getRot()
        rotated = angleDiff(current_yaw, start_yaw)

        if deg > 0 and rotated >= deg:
            break

        if deg < 0 and rotated <= deg:
            break

        touch = receiveData()

        if touch is not None and check:
            if touch[touch_front_right] == 1:
                interrupt("left")

            elif touch[touch_front_left] == 1:
                interrupt("right")

        time.sleep(0.005)

    sendCommand(0, 0)


#=============================OBSTACLE ALGORITHM=======================================


def obstacleAvoidance(tofs, val3, speed, val, color):
    run = True
    cx_state = {
        "integral": 0,
        "last_error": 0,
        "last_time": time.monotonic()
    }
    while run:
        frame = get_frame()
        two = cv(frame)
        distances = getDistances(tofs)
        front = distances["front"]
        left = distances["left"]
        right = distances["right"]

        dist = 10
        buffer = 7
        dist_front = 10
        touch = receiveData()
        if color == "RED":
            if left > dist and front > dist_front:
                #PID to stay on fixed path with obstacle at fixed distance from path using x coordinate
                pidcx(val3, RESOLUTION[0] // 3, speed, color, two, cx_state)
            elif left <= dist and front > dist_front:
                #When next to the obstacle uses PID to "wall follow" on the obstacle until the obstacle ends
                startPid(tofs, 9, "left", val, 150)
                
                L = getDistances(tofs)["left"]
                while(L<= (dist+buffer)):
                    L = getDistances(tofs)["left"]
                    time.sleep(0.01)
                stopPid()
                sendCommand(100, 0, 1.5)
                run = False
                return
            elif front <= dist_front or touch[touch_front_left] == 1 or touch[touch_front_right] == 1:
                #Avoid hitting obstacle
                interrupt("right")
            else:
                #In case some error causes nothing to be true just move forward
                sendCommand(100, 0)
        if color == "GREEN": #Reversed for green (left-right, cx on other side)
            if right > dist and front > dist_front:
                pidcx(val3, (2*RESOLUTION[0]) // 3, speed, color, two, cx_state)
            elif right <= dist and front > dist_front:
                startPid(tofs, 9, "right", val, 150)

                R = getDistances(tofs)["right"]
                while(R <= (dist+buffer)):
                    R = getDistances(tofs)["right"]
                    time.sleep(0.01)
                stopPid()
                gyroPid(getRot(), 150, val4, None, 1.5)
                
                run = False
                return
            elif front <= dist_front or touch[touch_front_left] == 1 or touch[touch_front_right] == 1:
                interrupt("left")
            else:
                sendCommand(100,0)
            time.sleep(0.01)

             

def interrupt(dir):
    if dir == "left":
        sign = -1
    elif dir == "right":
        sign = 1
    else: return
    turn(-150, sign*(-20), sign*20, False)
    turn(150, sign*10, sign*15, False)
    turn(150, sign*(-15), sign*(-35), False)

    

def pidcx(gains, cx_desired, speed, color, two, state):
    if two[0] is not None and two[0]["color"] == color:
        i = 0
    elif len(two) > 1 and two[1] is not None and two[1]["color"] == color:
        i = 1
    else:
        sendCommand(speed, 0)
        return

    cx = two[i]["cx"]
    # cx = cv(frame)[0]["cx"]

    error = cx_desired - cx
    # integral += error
    # derivative = error - last_error
    # last_error = error

    now = time.monotonic()
    dt = now - state["last_time"]
    state["last_time"] = now

    pid = pid_step(error, gains, state, dt)

    sendCommand(speed, pid)

    return


def gyroPid(gz_0, speed, gains, dist1, rot):
    state = {
        "integral": 0,
        "last_error": 0,
        "last_time": time.monotonic()
    }

    if rot is not None: 
        sendCommand(speed, 0, rot)
    if dist1 is not None:
        sendCommand(speed, 0)
    if (dist1 is not None and rot is not None) or (dist1 is None and rot is None): return
    while True:
        gz = getRot()
        error = angleDiff(gz, gz_0)
        # integral += error
        # derivative = error - last_error
        # last_error = error

        now = time.monotonic()
        dt = now - state["last_time"]
        state["last_time"] = now

        pid = pid_step(error, gains, state, dt)

        sendCommand(None, pid)

        if rot is not None:
            data = receiveData()
            if data is not None and data[4] == 1: break
        
        front = getDistances(tofs)["front"]
    
        if dist1 is not None and front is not None and front <= dist1: break

        time.sleep(0.01)

    return






                    
