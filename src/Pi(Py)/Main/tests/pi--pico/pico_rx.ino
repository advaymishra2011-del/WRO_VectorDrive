void setup() {
  Serial.begin(115200);

  Serial1.setTX(0);
  Serial1.setRX(1);
  Serial1.begin(115200);

  Serial.println("Pico RX test ready");
}

void loop() {
  if (Serial1.available()) {
    String msg = Serial1.readStringUntil('\n');
    Serial.print("RECEIVED: ");
    Serial.println(msg);
  }
}