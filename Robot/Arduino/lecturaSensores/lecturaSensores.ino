// Definición de los pines de los sensores
const int sensor1Pin = A0;  // Sensor 1 en el pin A0
const int sensor2Pin = A1;  // Sensor 2 en el pin A1
const int sensor3Pin = A2;  // Sensor 3 en el pin A2

// Variables para almacenar las lecturas de los sensores
float sensor1Value = 0;
float sensor2Value = 0;
float sensor3Value = 0;


void setup() {
  // Inicializar la comunicación serie
  Serial.begin(9600);
}

void loop() {
  // Comprobar si hay datos disponibles en el puerto serie
  if (Serial.available() > 0) { //Serial.available() > 0
    String command = Serial.readString();  // Leer la instrucción completa

    // Leer los valores de los sensores
    sensor1Value = 2.5;//analogRead(sensor1Pin);
    sensor2Value = 4;//analogRead(sensor2Pin);
    sensor3Value = 2.67;//analogRead(sensor3Pin);

    // Creación del mensaje JSON
    String message = "{\"sensor1\": ";

    if(command.indexOf('1') != -1){
      message += String(sensor1Value,2);
    }else{
      message += "null";
    }

    message += ", \"sensor2\": ";
    if(command.indexOf('2') != -1){
      message +=  String(sensor2Value,2);
    }else{
      message += "null";
    }

    
    message += ", \"sensor3\": ";
    if(command.indexOf('3') != -1){
      message +=  String(sensor3Value,2);
    }else{
      message += "null";
    }

    message += "}";


    // Enviar el mensaje por serie
    Serial.println(message);
    //delay(1000);
  }
}
