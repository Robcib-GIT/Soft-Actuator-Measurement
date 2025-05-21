import time
from typing import List
import matplotlib.pyplot as plt
import numpy as np
import math

import ADS1x15
import board
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
import Jetson.GPIO as GPIO

from Utilities.blood_pressure import BloodPressure
from Utilities.data_operations import save_data


"""
 I2C BUS 0 (SCL: 28 | SDA: 27)
 I2C BUS 1 (SCL: 5  |  SDA: 3)
"""

# --- Constantes y variables presión arterial ---
BUS_I2C_ADS115 = 1
ADS_1 = ADS1x15.ADS1115(BUS_I2C_ADS115, 0x49)  # Para pulso y temperatura
ADS_1.setGain(ADS_1.PGA_0_512V)
PULSE_INTERVAL = 40E-3  #ms

# Constantes generales para sensores
VCC = 5.0

# Constantes para la temperatura
R_AUX = 10000.0  # Resistencia en serie (ohmios)
R0 = 10000.0  # Resistencia del NTC a T0 (ohmios)
BETA = 3950.0  # Constante beta del NTC (K)
T0 = 25.0 + 273.15  # Temperatura nominal en Kelvin (25°C)

# --- Declaracion de funciones presion arterial ---
def get_temperature() -> float:
    voltage = ADS_1.toVoltage(ADS_1.readADC(1))
    print(voltage)

    if voltage == 0:
        return 25.0  # Evitar división por cero o log(0)

    r_ntc = R_AUX * (VCC / voltage - 1)
    temperature_k = 1.0 / ((math.log(r_ntc / R0) / BETA) + (1.0 / T0))
    return temperature_k - 273.15  # Convertir de Kelvin a Celsius

if __name__ == "__main__":
    try:
        while True:
            temperature = get_temperature()
            #print(f"r\Temperature: {temperature:.2f}       ")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nEjecución interrumpida por el usuario. Saliendo...")