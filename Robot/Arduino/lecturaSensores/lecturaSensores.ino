/*
Este código permite solicitar información de distintos sensores enviando una cadena de caracteres 
por el puerto serie y devuelve un JSON por serie con los valores de los sensores solicitados, con 
una frecuencia regulable para cada sensor.
*  "all": se leen todos los sensores
*  "none": no se lee ningun dato
*  char 1-3: se invierte el estado de lectura del sensor especificado 
*/




#include <Arduino_JSON.h>

// Configuración de los sensores
struct SensorConfig {
  int pin;
  unsigned long interval;
  unsigned long previousMillis;
  float value;
  bool read;
  bool previousRead;
};

SensorConfig sensors[] = {
    {A0, 2000, 0, 0, false, false},  // Sensor 1
    {A1, 200, 0, 0, false, false},  // Sensor 2
    {A2, 200, 0, 0, false, false}   // Sensor 3
};

const int sensorCount = sizeof(sensors) / sizeof(sensors[0]);

void setup() {
  Serial.begin(9600);
}

void loop() {
  handleSerialInput();
  sendSensorData();
}

void handleSerialInput() {
  if (Serial.available() > 0) {
    String command = Serial.readString();
    command.trim();

    if (command == "all") {
      setAllSensors(true);
    } else if (command == "none") {
      setAllSensors(false);
    } else {
      toggleSensors(command);
    }
  }
}

void setAllSensors(bool state) {
  for (int i = 0; i < sensorCount; i++) {
    sensors[i].read = state;
  }
}

void toggleSensors(const String &command) {
  for (int i = 0; i < sensorCount; i++) {
    if (command.indexOf('1' + i) != -1) {
      sensors[i].read = !sensors[i].read;
    }
  }
}

void sendSensorData() {
  unsigned long currentMillis = millis();
  JSONVar json; // Usamos JSONVar de la biblioteca Arduino_JSON

  bool sendData = false;

  for (int i = 0; i < sensorCount; i++) {
    SensorConfig &sensor = sensors[i];
    String sensorKey = "sensor" + String(i + 1);

    if (sensor.read && currentMillis - sensor.previousMillis >= sensor.interval) {
      sensor.previousMillis = currentMillis;
      sensor.value = randomWithDecimals(); // analogRead(sensor.pin);
      json[sensorKey] = sensor.value;
      sendData = true;
    } else if (!sensor.read && sensor.previousRead) {
      json[sensorKey] = -1; //Fin del envío
      sendData = true;
    } else {
      json[sensorKey] = undefined; //No hace falta incluirlo en el json
    }

    sensor.previousRead = sensor.read;
  }

  if (sendData) {
    String jsonString = JSON.stringify(json);
    Serial.println(jsonString);
  }
}


//TODO borrar cuando conecte sensores
float randomWithDecimals() {
  int wholePart = random(0, 500);
  int decimalPart = random(0, 100);

  return wholePart + decimalPart / 100.0;
}
