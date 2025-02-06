const int pinEntrada = 7;  // Pin digital a leer
int estadoAnterior = LOW;  // Estado previo del pin

void setup() {
    pinMode(pinEntrada, INPUT);
    Serial.begin(115200);
}

void loop() {
    int estadoActual = digitalRead(pinEntrada);
    
    if (estadoActual != estadoAnterior) {
        Serial.println(estadoActual);
        estadoAnterior = estadoActual;
    }
}
