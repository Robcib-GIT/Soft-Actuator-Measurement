void setup() {
  // Inicia la comunicación serial a 9600 baudios
  Serial.begin(9600);
}

void loop() {
  int sensorValue = analogRead(A0);
  //float processedValue = (sensorValue-minValue)/float(maxValue-minValue);

  // Envía el valor leído al monitor serial
  Serial.println(sensorValue);

  // Espera un breve tiempo antes de leer el valor de nuevo
  delay(40);  // Retardo de 100 ms (ajustable)
}
