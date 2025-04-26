import ADS1x15
import time

ADS = ADS1x15.ADS1115(1, 0x48)   
ADS.setGain(ADS.PGA_0_512V)

def getPressure(sensor: int = 1, offset=27.0, pressureRef = 200.0, valueRef=2960.0):
    if sensor == 1:
        pressure_raw = ADS.readADC_Differential_0_1()
    else:
        pressure_raw = ADS.readADC_Differential_2_3()

    pressure = (pressure_raw-offset)*pressureRef/valueRef
    return float(pressure)

# Intervalo de tiempo en segundos
interval = 0.1  # Cambia este valor por el que necesites

try:
    while True:
        pressure1 = getPressure(sensor=1)
        pressure2 = getPressure(sensor=2)
        print(f"\rPresión manguito: {pressure1:.2f} mmHg    |   Presión actuador: {pressure2:.2f} mmHg     ", end="")
        time.sleep(interval)
except KeyboardInterrupt:
    print("\nLectura interrumpida por el usuario.")
