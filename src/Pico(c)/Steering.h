#include <servo.h>

#DEFINE SERVO_PIN 9

#DEFINE left -15
#DEFINE right 15

Servo steer;

//-------------------------------------------SERVO---------------------------------------------------
void steer(int deg) {
  steer.write(deg);
}