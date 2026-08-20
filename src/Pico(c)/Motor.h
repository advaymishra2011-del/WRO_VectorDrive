const int encoderA = 8;
const int encoderB = 7;
#include <Pi-UART.h>
#include <Steering.h>

const int fwd = 4;
const int bwd = 5;

const int fwdSpeed = 200;
const int bwdSpeed = -100;
const int rotation = 300;
volatile long encoderTicks = 0;

//Touch
const int pin1 = 10;
const int pin2 = 11;
const int pin3 = 12;
const int pin4 = 13;


//------------------MOTOR------------------------------------
void moveMotor(int speed, float rot) {
  long targetTicks = abs(rot*300); //Test
  speed = constrain(speed, -255, 255);
  resetTicks();
  if(speed<0){
    analogWrite(bwd, -speed);
  } else {
    analogWrite(fwd, speed);
  }
  while(getTicks()<=targetTicks){
    //Run main loop code while waiting
    
    receive(current);

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
  serial1.println("D");
}

void simpleMoveMotor(int speed) { 
  speed = constrain(speed, -255, 255);
  if(speed<0){
    analogWrite(bwd, -speed);
  } else {
    analogWrite(fwd, speed);
  }
}


//---------------------ENCODER------------------
void resetTicks() { 
  noInterrupts();
  encoderTicks = 0;
  interrupts();
}

long getTicks() {
  noInterrupts();
  long safe =   encoderTicks;
  interrupts();
  return safe;
}

void readEncoder() {
  if(digitalRead(encoderB)==HIGH){
    encoderTicks++;
  } else {
    encoderTicks--;
  }
}