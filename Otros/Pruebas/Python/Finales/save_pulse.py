import time
from typing import List
import matplotlib.pyplot as plt
import numpy as np

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

# --- Configuración del relé ---
RELAY_PIN = 18

try:
    GPIO.setmode(GPIO.BOARD)
except ValueError:
    GPIO.cleanup()
    GPIO.setmode(GPIO.BOARD)

GPIO.setup(RELAY_PIN, GPIO.OUT)

# --- Constantes y variables presión arterial ---
BUS_I2C_ADS115 = 1
ADS_1 = ADS1x15.ADS1115(BUS_I2C_ADS115, 0x49)  # Para pulso y temperatura
ADS_1.setGain(ADS_1.PGA_0_512V)
PULSE_INTERVAL = 1 / 25  # ms


# --- Declaracion de funciones presion arterial ---
def get_pulse():
    pulse = ADS_1.readADC(0)
    time.sleep(PULSE_INTERVAL)
    return int(pulse)


if __name__ == "__main__":
    steps = int(20 / PULSE_INTERVAL)
    pulse_samples = []
    for sample in range(steps+1):
        pulse_samples.append(get_pulse())
        print(f"\rProgreso: {sample / steps * 100:.2f}%          ", end="")

    data = {
        "Time": np.arange(0, len(pulse_samples)) * PULSE_INTERVAL,
        "Pulse": pulse_samples
    }

    real_results = {}
    print("Introduce las lecturas reales:")
    try:
        real_ppm = int(input("PPM real: "))
        real_results["PPM"] = real_ppm
    except Exception:
        print("No se registraron datos reales")

    save_data(data_dict=data, results_dict=real_results)
