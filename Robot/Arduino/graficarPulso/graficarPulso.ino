void setup() {
  // Inicia la comunicación serial a 9600 baudios
  Serial.begin(9600);
}

void loop() {
  // Lee el valor del pin A0 (valor entre 0 y 1023)
  const int maxValue=600;
  const int minValue=420;
  int sensorValue = constrain(analogRead(A0),minValue,maxValue);
  float processedValue = (sensorValue-minValue)/float(maxValue-minValue);

  // Envía el valor leído al monitor serial
  Serial.println(processedValue*100);

  // Espera un breve tiempo antes de leer el valor de nuevo
  delay(40);  // Retardo de 100 ms (ajustable)
}
