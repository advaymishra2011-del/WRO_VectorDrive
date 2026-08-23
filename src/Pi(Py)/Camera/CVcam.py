import time
import numpy as np
from picamera2 import Picamera2
import cv2

# Green
LOWER_GREEN = np.array([35, 60, 60])
UPPER_GREEN = np.array([85, 255, 255])

# Red 
LOWER_RED1, UPPER_RED1 = np.array([0, 70, 70]), np.array([10, 255, 255])
LOWER_RED2, UPPER_RED2 = np.array([170, 70, 70]), np.array([180, 255, 255])

RESOLUTION = (640, 480)

kernel = np.ones((3, 3), np.uint8)

#Pi cam 
picam2 = Picamera2()

config = picam2.create_video_configuration(
    main={"size": RESOLUTION, "format": "RGB888"}
)

picam2.configure(config)
picam2.start()


def get_frame():
    frame = picam2.capture_array()

    if frame is None:
        return None
    
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) 

    cropped = frame[0:(RESOLUTION[1]//2), 0:RESOLUTION[0]]

    return cropped

def cv(frame):

    candidates = []

    img = frame.copy()
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask_g = cv2.inRange(hsv, LOWER_GREEN, UPPER_GREEN)
    mask_g = cv2.morphologyEx(mask_g, cv2.MORPH_OPEN, kernel)

    mask_r1 = cv2.inRange(hsv, LOWER_RED1, UPPER_RED1)
    mask_r2 = cv2.inRange(hsv, LOWER_RED2, UPPER_RED2)
    mask_r = cv2.bitwise_or(mask_r1, mask_r2)
    mask_r = cv2.morphologyEx(mask_r, cv2.MORPH_OPEN, kernel)


    #Contours and left-right direction detection
    left_pillar = None
    right_pillar = None

    contours_g, _ = cv2.findContours(mask_g, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in contours_g:
        area = cv2.contourArea(c)
        if area > 600: # Filter out tiny noise spots
            x, y, w, h = cv2.boundingRect(c)
            # Find the center point of this specific pillar
            cx = x + (w // 2)
            cy = y + (h // 2)
            
            candidates.append({
                "color": "GREEN",
                "area": area,
                "x": x,
                "y": y,
                "w": w,
                "h": h,
                "cx": cx,
                "cy": cy
            })

    contours_r, _ = cv2.findContours(mask_r, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in contours_r:
        area = cv2.contourArea(c)
        if area > 600:
            x, y, w, h = cv2.boundingRect(c)
            cx = x + (w // 2)
            cy = y + (h // 2)

            candidates.append({
                "color": "RED",
                "area": area,
                    "x": x,
                "y": y,
                "w": w,
                "h": h,
                "cx": cx,
                "cy": cy
            })

    # Sort candidates by area and keep the two largest, Left-Right      
    top_two = sorted(candidates, key=lambda c: c["area"], reverse=True)[:2]

    if len(top_two) == 2:
        if top_two[0]["cx"] < top_two[1]["cx"]:
            top_two[0]["dir"], top_two[1]["dir"] = "left", "right"
        else:
            top_two[0]["dir"], top_two[1]["dir"] = "right", "left"
    elif len(top_two) == 1:
        top_two[0]["dir"] = "center"
    else:
        top_two = []

    return top_two


LOWER_PURPLE = np.array([125, 50, 50])
UPPER_PURPLE = np.array([160, 255, 255])

def detect_parking(frame):

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, LOWER_PURPLE, UPPER_PURPLE)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    largest = None
    largest_area = 0

    for c in contours:

        area = cv2.contourArea(c)

        if area > largest_area:
            largest_area = area
            largest = c

    if largest is None or largest_area < 600:
        return None

    x, y, w, h = cv2.boundingRect(largest)

    cx = x + w // 2

    return cx

last_print = 0

try:
    while True:

        start = time.perf_counter()

        frame = get_frame()

        if frame is None:
            continue

        pillars = cv(frame)
        parking_x = detect_parking(frame)

        # Actual processing FPS
        elapsed = time.perf_counter() - start
        fps = 1 / elapsed if elapsed > 0 else 0

        now = time.time()

        if now - last_print >= 0.2:
            last_print = now

            # Clear terminal
            print("\033[2J\033[H", end="")

            print("========================================")
            print("          PI 5 CAMERA / CV")
            print("========================================")
            print(f"FPS:       {fps:6.1f}")
            print(f"Frame:     {frame.shape[1]} x {frame.shape[0]}")
            print("----------------------------------------")

            print("PILLARS:")

            if len(pillars) == 0:
                print("  None detected")

            else:
                for p in pillars:
                    print(
                        f"  {p['dir']:>6} | "
                        f"{p['color']:<5} | "
                        f"cx={p['cx']:3d} | "
                        f"cy={p['cy']:3d} | "
                        f"area={p['area']:7.0f}"
                    )

            print("----------------------------------------")

            if parking_x is None:
                print("Parking:  None")
            else:
                print(f"Parking X: {parking_x}")

            print("========================================")
            print("Ctrl+C to stop")

except KeyboardInterrupt:
    print("\nStopping camera...")

finally:
    picam2.stop()
    