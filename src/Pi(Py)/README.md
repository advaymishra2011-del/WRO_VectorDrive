# Pi5 Code 
Computer vision and sensor control, the main hub of the bot

## Computer Vision (CV)
Use of openCV library "cv2" in python:
- Creates a mask for red, green and purple detection separately and creates contours
- Uses area to filter for the largest object and returns its coordinates and color
- Flexible and able to handle if no object is seen / only 1 is seen
- If 2 as expected are seen, it figures out which is closest and uses its position to navigate

## Start Switch
gpiozero library is used to directly read no/nc/c type switch and run as soon as pressed

## Initialization
When the bot starts, it instantly detects 2 things:
1. Which direction its supposed to run by checking which side its facing using the wall of the parking -- the direction sets 2 values (1) sign and (2) turndir which govern the turning algorithms
2. Zero for the gyro angle, such that if it is at this angle it is exactly straight

It then runs a tested park algorithm by aligning and turning outwards

## Navigation
Captures multiple frames in hopes of seeing an obstacle and its color
   -> If obstacle doesnt exist, PID to align with the wall and move straight
   -> If obstacle exists, run obstacle algorithm

### Obstacle Algorithm
1. The camera looks for the obstacle of the right color and gives its x position
2. A unique PID algorithm is applied to keep the obstacle at the same x position from the bots POV, creating a perfect line of movement and preventing collision
   - The x position is decided by color
3. After the bot reaches the obstacle, it's ToFs detect where the obstacle is and use a short period of PID to stay at a good distance from it
4. After the obstacle is passed, the bot moves forward a bit to prevent collision from the back side

## Laps
The main loop counts the number of proper turns taken as a tracker to see that when 12 have been taken it is time to park

## Park
1. The bot goes forward to the end of the straight with the parking
2. It uses the gyroscope to move perfectly straight and take a U-Turn towards the parking
3. It moves forward till it finds the purple contour of the parking and uses similar-to-obstacle x coordinate alignment
4. It moves forward till it finds the parking seen by a drop in ToF distance -- it checks this 5 times to prevent false detection and failure to park
5. It then slowly moves forward till it finds the other wall and then takes a tested backward U-Turn manouever to park parallel

