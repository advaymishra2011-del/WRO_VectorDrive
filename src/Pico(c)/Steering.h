#include <Servo.h>

const int SERVO_PIN = 9;
int servo_center = y; //Test

Servo steerServo;

//-------------------------------------------SERVO---------------------------------------------------
void steer(int steering) {
  float deg = map(steering, -30, 30, -x, x) //Test
  steerServo.write(servo_center + deg);
}