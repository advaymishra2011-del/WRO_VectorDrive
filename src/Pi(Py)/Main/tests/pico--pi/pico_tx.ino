void setup() {
  Serial.begin(115200);          // USB debug

  Serial1.setTX(0);              // GP0 = TX
  Serial1.setRX(1);              // GP1 = RX
  Serial1.begin(115200);

  Serial.println("UART started");
}

void loop() {
  Serial1.write("HELLO\n");
  Serial.println("Sent HELLO");
  delay(1000);
}