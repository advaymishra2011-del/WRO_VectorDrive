#include <Motor.h>
#include <Pi-UART.h>
#include <Steering.h>

void setup() {
  steerServo.attach(SERVO_PIN);

  pinMode(encoderA, INPUT_PULLUP);
  pinMode(encoderB, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(encoderA), readEncoder, RISING);

  Serial1.setRX(1);
  Serial1.setTX(0);
  Serial1.begin(115200);

  pinMode(pin1, INPUT_PULLUP);
  pinMode(pin2, INPUT_PULLUP);
  pinMode(pin3, INPUT_PULLUP);
  pinMode(pin4, INPUT_PULLUP);
}

void loop() {
  receive(current);

  if (current.rot == 0){
    simpleMoveMotor(current.motor)
  }
  else {
    moveMotor(current.motor, current.rot);
  }
  steer(current.steer);

  if (millis() - lastTouchSend >= 30) {
      lastTouchSend = millis();
      touch = {
          digitalRead(pin1) == LOW,
          digitalRead(pin2) == LOW,
          digitalRead(pin3) == LOW,
          digitalRead(pin4) == LOW
      };
      send(touch);
  }

  delay(1);
}


