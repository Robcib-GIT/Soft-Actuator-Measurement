/*
Este código permite solicitar información de distintos sensores enviando una cadena de caracteres 
por el puerto serie y devuelve un JSON por serie con los valores de los sensores solicitados, con 
una frecuencia regulable para cada sensor.
*/

unsigned long previousMillisSensor1 = 0; // Tiempo anterior de Sensor1
unsigned long previousMillisSensor2 = 0; // Tiempo anterior Sensor2
unsigned long previousMillisSensor3 = 0; // Tiempo anterior Sensor3
const long intervalSensor1 = 2000; // Intervalo Sensor1
const long intervalSensor2 = 500;  // Intervalo Sensor2
const long intervalSensor3 = 100;  // Intervalo Sensor3

// Definición de los pines de los sensores
const int sensor1Pin = A0;  // Sensor 1 en el pin A0
const int sensor2Pin = A1;  // Sensor 2 en el pin A1
const int sensor3Pin = A2;  // Sensor 3 en el pin A2

// Variables para almacenar las lecturas de los sensores
float sensor1Value = 0;
float sensor2Value = 0;
float sensor3Value = 0;

bool readSensor1 = false;
bool readSensor2 = false;
bool readSensor3 = false;

bool sendData = false;


void setup() {
  // Inicializar la comunicación serie
  Serial.begin(9600);
}

void loop() {
  // Comprobar si hay datos disponibles en el puerto serie
  if (Serial.available() > 0) {
    unsigned long currentMillis = millis();
    String command = Serial.readString();  // Leer la instrucción completa
    command.trim(); //Eliminar sobrantes (para tests con monitor serie)

    /* Comprobar que sensores hay que leer segun el comando recibido
     *  "all": se leen todos los sensores
     *  "none": no se lee ningun dato
     *  char 1-3: se invierte el estado de lectura del sensor especificado 
    */
    if(command == "all"){ 
      readSensor1 = true;
      readSensor2 = true;
      readSensor3 = true;
    }else if(command == "none"){
      readSensor1 = false;
      readSensor2 = false;
      readSensor3 = false;
    }else{
      if(command.indexOf('1') != -1) readSensor1 =! readSensor1;
      if(command.indexOf('2') != -1) readSensor2 =! readSensor2;
      if(command.indexOf('3') != -1) readSensor3 =! readSensor3;
    }

    
    while(!Serial.available()){
      currentMillis = millis();
      
      // Creación del mensaje JSON
      String message = "{\"sensor1\": ";
  
      if(readSensor1){
        if (currentMillis - previousMillisSensor1 >= intervalSensor1) {
          previousMillisSensor1 = currentMillis;
          sensor1Value = random(0, 50000) / 100.0;//analogRead(sensor1Pin)
          sendData = true;
        }
        
        message += String(sensor1Value,2);
      }else{
        message += "null";
      }
  
      message += ", \"sensor2\": ";
      if(readSensor2){
        if (currentMillis - previousMillisSensor2 >= intervalSensor2) {
          previousMillisSensor2 = currentMillis;
          sensor2Value = random(0, 50000) / 100.0;//analogRead(sensor2Pin)
          sendData = true;
        }
      
        message +=  String(sensor2Value,2);
      }else{
        message += "null";
      }
  
      message += ", \"sensor3\": ";
      if(readSensor3){
        if (currentMillis - previousMillisSensor3 >= intervalSensor3) {
          previousMillisSensor3 = currentMillis;
          sensor3Value = random(0, 50000) / 100.0;//analogRead(sensor1Pin)
          sendData = true;
        }
        
        message +=  String(sensor3Value,2);
      }else{
        message += "null";
      }
  
      message += "}";

      // Enviar el mensaje por serie cuando se complete algun intervalo
      if(sendData){
        Serial.println(message);
        sendData = false;
      }   

    }
  }
}
