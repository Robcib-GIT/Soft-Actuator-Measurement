/*
Este código permite solicitar información de distintos sensores enviando una cadena de caracteres 
por el puerto serie y devuelve un JSON por serie con los valores de los sensores solicitados, con 
una frecuencia regulable para cada sensor.
*  "all": se leen todos los sensores
*  "none": no se lee ningun dato
*  char 1-3: se invierte el estado de lectura del sensor especificado 
*  
*  Además, para añadir más mediciones por envio sin saturar el puerto serie, se ha añadido la 
*  posibilidad de enviar un array de "samples" muestras tomadas cada "interval" ms
*/

#include <ArduinoJson.h>

// Configuración de los sensores
struct SensorConfig {
  int pin;
  unsigned long interval;
  unsigned long previousMillis;
  bool read;
  bool previousRead;
  int* samplesArray;
  int samples; //Muestras a tomar
  int samplesCount; //Contador de muestras tomadas
};

SensorConfig sensors[] = {
    {A0, 1000, 0, false, false, nullptr, 1, 0}, // Sensor 1: Temperatura
    {A1, 40, 0, false, false, nullptr, 5, 0},  // Sensor 2: Pulso
    {A2, 40, 0, false, false, nullptr, 5, 0}  // Sensor 3
};

const int sensorCount = sizeof(sensors) / sizeof(sensors[0]);


//Declaracion de funciones
void setAllSensors(bool state);
void toggleSensors(const String &command);
void sendSensorData();
float randomWithDecimals();

void setup() {
  Serial.begin(9600);

  for (int i = 0; i < sensorCount; i++) {
    // Inicializar el array con asignación dinámica
    SensorConfig &sensor = sensors[i];
    if(sensor.samples>1){
      sensors[i].samplesArray = new int[sensor.samples];
      for (int j = 0; j < sensor.samples; j++) {
        sensor.samplesArray[j] = -1;  // Inicialización de las muestras
      }
    }
  }
}

void loop() {
  bool sendData = handleSerialInput();
  while(!Serial.available() and sendData){
    sendSensorData();
  }
}

bool handleSerialInput() {
  bool sendData = false;
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
    for (int i = 0; i < sensorCount; i++) {
      SensorConfig &sensor = sensors[i];
      if(sensor.read or sensor.previousRead) sendData = true;
    }
    return sendData;
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
  JsonDocument json;
  bool sendData = false;

  for (int i = 0; i < sensorCount; i++) {
    SensorConfig &sensor = sensors[i];
    String sensorKey = "sensor" + String(i + 1);

    if (sensor.read && currentMillis - sensor.previousMillis >= sensor.interval) {
      sensor.previousMillis = currentMillis;
      
      //Tomar muestra
      if(sensor.samples > 1){
        sensor.samplesArray[sensor.samplesCount] = analogRead(sensor.pin);
      }
      sensor.samplesCount += 1;

      //Tomar muestra y enviar
      if(sensor.samplesCount >= sensor.samples){
        sensor.samplesCount = 0;
        sendData = true;

        // Diferenciar si es valor unico o array
        if(sensor.samples == 1){
          json[sensorKey] = analogRead(sensor.pin);
        }else{
          JsonObject sensorData = json[sensorKey].to<JsonObject>();
          sensorData["offset"] = sensor.interval;
          JsonArray data = sensorData["data"].to<JsonArray>();
          //Añadir lecturas al array del json a la vez que se reinicia
          for (int j = 0; j < sensor.samples; j++) {
            data.add(sensor.samplesArray[j]);
            sensor.samplesArray[j] = -1;
          }
        }
      }
      
    } else if (!sensor.read && sensor.previousRead) {
        sensor.samplesCount = 0;
        sensor.previousMillis = currentMillis; //Intento de evitar que se desfasen a veces
        // Diferenciar si es valor unico o array
        if(sensor.samples == 1){
          json[sensorKey] = -1;
        }else{
          //Se mandan los leidos hasta que se cancele
          JsonObject sensorData = json[sensorKey].to<JsonObject>();
          sensorData["offset"] = sensor.interval;
          JsonArray data = sensorData["data"].to<JsonArray>();
          //Añadir lecturas al array del json a la vez que se reinicia
          for (int j = 0; j < sensor.samples; j++) {
            data.add(sensor.samplesArray[j]);
            sensor.samplesArray[j] = -1;
          }
        }
        sendData = true;
    }
 
    sensor.previousRead = sensor.read;
  }

  if (sendData) {
    String jsonString;
    serializeJson(json, jsonString);
    Serial.println(jsonString);
  }
}

/*
// TODO borrar cuando conecte sensores
float randomWithDecimals() {
  int wholePart = random(0, 500);
  int decimalPart = random(0, 100);

  return wholePart + decimalPart / 100.0;
}
*/
