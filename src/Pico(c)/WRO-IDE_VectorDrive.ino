void setup() {
  steer.attach();

  pinMode(encoderA, INPUT_PULLUP);
  pinMode(encoderB, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(encoderA), readEncoder, RISING);
}

void loop() {
  // put your main code here, to run repeatedly:

}

void pivotTurn(int deg) {
  simpleMoveMotor(fwdSpeed);
  
}
