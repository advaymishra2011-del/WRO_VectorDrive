# Pico Code 
Motor controls and steering

## Main Loop
- Via UART, the Pi5 sends a command in the format "C, {motorspeed}, {steeringdeg}, {rotations}". C helps it identify that it is send from  Pi5, and the others get updates in the storage of latest message
  -> The main loop keeps listening for these and uses the simple "moveMotor" and "simpleMoveMotor" to turn the motor
- The Pico also keeps listening for touch sensor changes and sends them to the Pi5 in format "T, 0,0,1,1" (e.g.)

## N20 Encoder Motor
- If rotation is None, then the motor simply turns on and off via the function "simpleMoveMotor"
- If rotation is not None, then "moveMotor(speed, rot)" is run which uses a tick system to count rotations
  -> The code is in a sort of "sleep" while the motor is running the given no. of rotations as it waits for the rotation to finish so it can do some other task
  -> In case it is needed by the Pi5, the Pico also sends a message as "D" when the rotations are complete, signaling "You can run further code now"

