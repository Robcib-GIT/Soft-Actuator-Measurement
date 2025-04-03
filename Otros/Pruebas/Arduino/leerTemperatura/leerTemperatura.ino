/*
 * https://www.rinconingenieril.es/como-usar-un-termistor-ntc/
*/
#include <math.h>

#define ADC_MAX 1023.0  // Resolución del ADC de 10 bits
#define ALIMENTACION 5000.0  // Voltaje de alimentación en mV
#define R_SERIE 9962.0  // Resistencia en serie con el NTC (10kΩ)
#define BETA 3950.0  // Coeficiente β del termistor
#define R0 10000.0  // Resistencia del termistor a T0 (10kΩ)
#define T0 298.15  // Temperatura de referencia en Kelvin (25°C)

float calcularTemperatura(int valorADC) {
    float Vout = (valorADC * ALIMENTACION) / ADC_MAX;  // Convertir lectura a voltaje
    float R_NTC = R_SERIE * (ALIMENTACION / Vout - 1);  // Calcular resistencia del NTC
    float temperaturaK = 1.0 / ((log(R_NTC / R0) / BETA) + (1.0 / T0));  // Aplicar ecuación
    return temperaturaK - 273.15;  // Convertir de Kelvin a Celsius
}

void setup() {
    Serial.begin(9600);
}

void loop() {
    int valorADC = analogRead(A0);
    float temperatura = calcularTemperatura(valorADC);
    
    Serial.print("Temperatura (°C): ");
    Serial.println(temperatura);
    
    delay(1000);
}
