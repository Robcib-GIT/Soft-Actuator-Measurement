import ADS1x15
import time

ADS = ADS1x15.ADS1115(0, 0x48)   
ADS.setGain(ADS.PGA_0_512V)

def getPressure():
    pressure_raw = ADS.readADC_Differential_0_1()
    pressure = (pressure_raw-27.0)*200/2960.0
    return float(pressure)

# Intervalo de tiempo en segundos
interval = 0.1  # Cambia este valor por el que necesites

try:
    while True:
        pressure = getPressure()
        print(f"\rPresión: {pressure:.2f} mmHg     ", end="")
        time.sleep(interval)
except KeyboardInterrupt:
    print("\nLectura interrumpida por el usuario.")
