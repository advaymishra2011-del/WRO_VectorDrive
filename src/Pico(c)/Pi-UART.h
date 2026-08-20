struct Commands {
  int motor;
  int steer;
  float rot;
};

struct Touch {
  int s1;
  int s2;
  int s3;
  int s4;
};

Commands current = {0, 0, 0.0};
Touch touch = {0,0,0,0};

unsigned long lastTouchSend = 0;


void receive(Commands &current) {

    if (!Serial1.available()) {
        return;
    }

    String cmd = Serial1.readStringUntil('\n');

    int first = cmd.indexOf(',');
    int second = cmd.indexOf(',', first + 1);
    int third = cmd.indexOf(',', second + 1);

    if (first == -1 || second == -1 || third == -1) {
        return;
    }

    if (cmd.substring(0, first) != "C") {
        return;
    }

    String motor = cmd.substring(first + 1, second);
    String steer = cmd.substring(second + 1, third);
    String rot = cmd.substring(third + 1);

    if (motor != "None")
        current.motor = motor.toInt();

    if (steer != "None")
        current.steer = steer.toInt();

    if (rot != "None")
        current.rot = rot.toFloat();
}


void send(Touch touch) {
    Serial1.print("T,");
    Serial1.print(touch.s1);
    Serial1.print(",");
    Serial1.print(touch.s2);
    Serial1.print(",");
    Serial1.print(touch.s3);
    Serial1.print(",");
    Serial1.println(touch.s4);
}