import numpy as np
import cv2
#from picamera2 import Picamera2

# 2. Optimized HSV Boundaries (Tweak based on your room's light)
LOWER_GREEN = np.array([35, 60, 60])
UPPER_GREEN = np.array([85, 255, 255])

# Red spans across the HSV 0/180 boundary
LOWER_RED1, UPPER_RED1 = np.array([0, 70, 70]), np.array([10, 255, 255])
LOWER_RED2, UPPER_RED2 = np.array([170, 70, 70]), np.array([180, 255, 255])

RESOLUTION = (640, 480)

kernel = np.ones((3, 3), np.uint8)

#Pi cam
# picam2 = Picamera2()

# config = picam2.create_video_configuration(
#     main={"size": RESOLUTION, "format": "RGB888"}
# )

# picam2.configure(config)
# picam2.start()

#Computer cam
cap = cv2.VideoCapture(0)

def get_frame():
    ok, frame = cap.read()
    if not ok or frame is None:
        return None
    
    frame = cv2.resize(frame, (640, 480))
    return frame




# def get_frame():
#     frame = picam2.capture_array()

#     if frame is None:
#         return None
    
#     frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) 

#     return frame



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
    candidates.sort(key=lambda c: c["area"], reverse=True)
    candidates = candidates[:2]

    candidates.sort(key=lambda c: c["cx"])            

    # Interface for drawing detected pillars

    if len(candidates) == 2:

        # Candidates were already sorted by cx
        left_pillar = candidates[0]
        right_pillar = candidates[1]

        for name, pillar in [("LEFT", left_pillar), ("RIGHT", right_pillar)]:

            color_name = pillar["color"]
            x = pillar["x"]
            y = pillar["y"]
            w = pillar["w"]
            h = pillar["h"]

            # OpenCV uses BGR
            if color_name == "RED":
                box_color = (0, 0, 255)
            else:
                box_color = (0, 255, 0)

            # Draw bounding box
            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                box_color,
                3
            )

            # Draw label above box
            cv2.putText(
                frame,
                f"{name}: {color_name}",
                (x, max(y - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                box_color,
                2
            )

    else:

        # If we don't have exactly two candidates
        cv2.putText(
            frame,
            f"Candidates: {len(candidates)}"
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )
    
    return frame


while True:
    frame = get_frame()
    if frame is None:
        print("No frame captured")
        break

    frame = cv(frame)
    cv2.imshow('cam', frame)
    
    #cv2.imshow('Pi cam', frame)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()