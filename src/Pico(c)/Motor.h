#DEFINE encoderA 8
#DEFINE encoderB 7
#DEFINE fwd 4
#DEFINE bwd 5

const int fwdSpeed = 200;
const int bwdSpeed = -100;
const int rotation = 300;
volatile long encoderTicks = 0;


//------------------MOTOR------------------------------------
void moveMotor(int speed, ticks) {
  constrain(speed, -255, 255);
  resetTicks();
  if(speed<0){
    analogWrite(bwd, -speed);
  } else {
    analogWrite(fwd, speed)
  }
  while(getTicks()<=rotation){

  }
}

void simpleMoveMotor(int speed) { 
  constrain(speed, -255, 255);
  if(speed<0){
    analogWrite(bwd, -speed);
  } else {
    analogWrite(fwd, speed)
  }
}


//---------------------ENCODER------------------
void resetTicks() { 
  noInterrupts();
  encoderTicks = 0;
  interrupts();
}

int getTicks() {
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