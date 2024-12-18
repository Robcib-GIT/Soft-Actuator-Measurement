const int analogPin = A0; 
const int arraySize = 5;
int readings[arraySize];  
int index = 0;  
unsigned long lastMillis = 0;
const unsigned long interval = 500;


#include <ArduinoJson.h>

void setup() {
  Serial.begin(9600);

  // Inicializar array
  for (int i = 0; i < arraySize; i++) {
    readings[i] = 0;
  }
}

void loop() {
  if (millis() - lastMillis >= interval) {
    lastMillis = millis();

    int value = analogRead(analogPin);
    readings[index] = value;
    index++;
    
    if (index >= arraySize) {
      printJson(readings, arraySize);
      index = 0; 
      for (int i = 0; i < arraySize; i++) {
        readings[i] = 0;
      }
    }
    

    
  }
}

void printJson(int *temp, int temSize){
  JsonDocument doc;
  JsonArray data = doc["Sensor"].to<JsonArray>();
  for (int i = 0; i < temSize; i++) {
    data.add(temp[i]);
  }
  serializeJson(doc, Serial);
  
}
