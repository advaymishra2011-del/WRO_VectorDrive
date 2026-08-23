from gpiozero import Button
from signal import pause
import datetime

#Pin
switch = Button(5)

def switch_pressed():
    print("Switch Pressed")
    return True

def switch_released():
    print("Switch Released")


switch.when_pressed = switch_pressed
switch.when_released = switch_released

print("Starting...")

# Keep the script running to listen for inputs
pause()

