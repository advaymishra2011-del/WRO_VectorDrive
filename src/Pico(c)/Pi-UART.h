struct Commands {
  int motor;
  int steer;
};

struct Touch {
  int s1;
  int s2;
  int s3;
  int s4;
}

Commands receive() {
  if (Serial1.available()) {
      String cmd = Serial1.readStringUntil('\n');

      Commands values; 
      //0: Motor
      //1: Steer

      sscanf(cmd.c_str(), "%d,%d", &values.motor, &values.steer);



      Serial1.print("Motor: ");
      Serial1.println(values.motor);

      Serial1.print("Steering: ");
      Serial1.println(values.steer);

      return values;  

  } else {
    return "err"
  }
}

void send(Touch touch) {
  Serial1.print(touch.s1);
  Serial1.print(",");
  Serial1.print(touch.s2);
  Serial1.print(",");
  Serial1.print(touch.s3);
  Serial1.print(",");
  Serial1.print(touch.s4);
}