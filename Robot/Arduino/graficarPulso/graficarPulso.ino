void setup() {
  // Inicia la comunicación serial a 9600 baudios
  Serial.begin(9600);
}

void loop() {
  // Lee el valor del pin A0 (valor entre 0 y 1023)
  int sensorValue = analogRead(A1);

  // Envía el valor leído al monitor serial
  Serial.println(sensorValue);

  // Espera un breve tiempo antes de leer el valor de nuevo
  delay(100);  // Retardo de 100 ms (ajustable)
}
