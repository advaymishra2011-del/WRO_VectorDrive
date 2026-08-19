import time
import cv2
from flask import config
import numpy as np
import serial
import board
import busio
import threading

from picamera2 import Picamera2
from adafruit_bno08x.i2c import BNO08X_I2C
import adafruit_tcs34725
import adafruit_tca9548a
import adafruit_vl53l0x


from Camera.CVcam import get_frame, cv
from Pico import sendCommand, receiveData
from Sensing.ToF import getDistances
from Sensing.IMU import getRot
from Sensing.TCS import getColor

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
#================BNO===========================

from adafruit_bno08x import (
    BNO_REPORT_ACCELEROMETER,
    BNO_REPORT_GYROSCOPE,
    BNO_REPORT_MAGNETOMETER,
    BNO_REPORT_ROTATION_VECTOR
)

i2c = busio.I2C(
    board.SCL,
    board.SDA,
    frequency=400000
)

bno = BNO08X_I2C(i2c)

bno.enable_feature(BNO_REPORT_ACCELEROMETER)
bno.enable_feature(BNO_REPORT_GYROSCOPE)
bno.enable_feature(BNO_REPORT_MAGNETOMETER)
bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)

#================================PICO===========================
pico = serial.Serial(
    #"/dev/ttyAMA0", Check on pi
    115200,
    timeout=0.1
)

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
val2 = [2, 0.01, 0.01] #PID for back

def mod(x):
    if x<0:
        return -x
    elif x>=0:
        return x
    else:
        return None

def backPID(speed, tofs, val2):
    sendCommand(speed, 0)
    
    distances = getDistances(tofs)
    left = distances["rear_left"]
    right = distances["rear_right"]
    
    if speed<0:
        error = left - right
    elif speed>=0:
        error = right - left
    integral += error
    derivative = error - last_error
    last_error = error

    pid = (val2[0]*error) + (val2[1]*integral) + (val2[2]*derivative)

    sendCommand(speed, pid)
    time.sleep(0.01)

def wallAlign(tofs, dist, val2, buffer):

    distances = getDistances(tofs)
    left = distances["rear_left"]
    right = distances["rear_right"]
    gap = min(left, right)

    
    while(gap>=dist):
        backPID(-100, tofs, val2)

    while mod(left-right) >= buffer:
        for i in range(100):
            backPID(100, tofs, val2)
        for i in range(100):
            backPID(-100, tofs, val2)

#=================================WALL FOLLOW=====================================

stop_switch = threading.Event()
worker_thread = None

val = [2, 0.01, 0.01] #PID for tofs

def loop_worker(switch, tofs, dist, side, val, bno, speed):
    gz = 0
    gz_set = getRot(bno)
    while not switch.is_set():
        sendCommand(speed, 0)
        tof = getDistances(tofs)[side]

        if side == "left":
            error = dist - tof
        elif side == "right":
            error = tof - dist

        derivative = error - last_error
        integral += error
        last_error = error

        pid = (val[0]*error)+(val[1]*integral)+(val[2]*derivative)
        if gz < 31:
            sendCommand(speed, pid)
        elif gz > 31:
            sendCommand(speed, 0)
            time.sleep(0.05)

        gz = mod(getRot(bno) - gz_set)
        
        time.sleep(0.05)  
        


def startPid(tofs, dist, side, val, bno, speed):
    global worker_thread
    if worker_thread and worker_thread.is_alive():
        return
        
    stop_switch.clear()
    worker_thread = threading.Thread(target=loop_worker, args=(stop_switch, tofs, dist, side, val, bno, speed), daemon=True)
    worker_thread.start()


def stopPid():
    global worker_thread
    stop_switch.set()
    if worker_thread:
        worker_thread.join()

#=============================STEER=======================================
def turn(speed, sharpness, deg, bno):
    gz = 0
    gz_set = getRot(bno)
    sendCommand(speed, sharpness)
    while mod(gz) < mod(deg):
        gz = getRot(bno) - gz_set
        time.sleep(0.005)
    sendCommand(0, 0)


#=============================OBSTACLE ALGORITHM=======================================
val3 = [2, 0.01, 0.01] #PID for cx
touch_front_left = 0
touch_front_right = 1

def obstacleAvoidance(tofs, bno, val3, speed, val):
    run = True
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
        if two[0]["color"] == "RED":
            if left > dist and front > dist_front:
                #PID to stay on fixed path with obstacle at fixed distance from path using x coordinate
                pidcx(val3, RESOLUTION[0] // 3, speed)
            elif left <= dist and front > dist_front:
                #When next to the obstacle uses PID to "wall follow" on the obstacle until the obstacle ends
                startPid(tofs, 9, "left", val, bno, 150)
                while(L<= (dist+buffer)):
                    L = getDistances(tofs)["left"]
                    time.sleep(0.01)
                stopPid()
                sendCommand(100, 0)
                time.sleep(0.5)
                return
            elif front <= dist_front or receiveData()[touch_front_left] == 1 or receiveData()[touch_front_right] == 1:
                #Avoid hitting obstacle
                interrupt("right", bno)
            else:
                #In case some error causes nothing to be true just move forward
                sendCommand(100, 0)
        if two[0]["color"] == "GREEN": #Reversed for green (left-right, cx on other side)
            if right > dist and front > dist_front:
                pidcx(val3, (2*RESOLUTION[0]) // 3, speed)
            elif right <= dist and front > dist_front:
                startPid(tofs, 9, "right", val, bno, 150)
                while(R <= (dist+buffer)):
                    R = getDistances(tofs)["right"]
                    time.sleep(0.01)
                stopPid()
            elif front <= dist_front or receiveData()[touch_front_left] == 1 or receiveData()[touch_front_right] == 1:
                interrupt("left", bno)
            else:
                sendCommand(100, 0)

             

def interrupt(dir, bno):
    if dir == "left":
        sign = -1
    elif dir == "right":
        sign = 1
    else: return
    turn(-150, sign*(-20), sign*20, bno)
    turn(150, sign*10, sign*15, bno)
    turn(150, sign*(-15), sign*(-35), bno)

    

def pidcx(val3, cx_desired, speed):
    frame = get_frame()
    cx = cv(frame)[0]["cx"]

    error = cx_desired - cx
    integral += error
    derivative = error - last_error
    last_error = error

    pid = (val3[0]*error) + (val3[1]*integral) + (val3[2]*derivative)

    sendCommand(speed, pid)






                    
