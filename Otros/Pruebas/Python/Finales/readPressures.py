import ADS1x15
import time
import numpy as np








import time
from typing import List
import matplotlib.pyplot as plt

import ADS1x15
import board
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685


"""
 I2C BUS 0 (SCL: 28 | SDA: 27)
 I2C BUS 1 (SCL: 5  |  SDA: 3)
"""

# --- Constantes y variables presión arterial --- TODO: refinar cuando complete el actuador
BUS_I2C_ADS115 = 1
ADS = ADS1x15.ADS1115(BUS_I2C_ADS115, 0x48)
ADS.setGain(ADS.PGA_0_512V)

pressure_fs = 40  # Hz
INTERVAL = 1/pressure_fs

# --- Constantes y variables servos --- TODO: refinar rangos servo y angulos
INFLATE_ANGLE = 90
DEFLATE_ANGLE = 0
IDLE_ANGLE = 18
BUS_I2C_PCA965 = 0

if BUS_I2C_PCA965 == 1:  #
    i2c = board.I2C()  # o busio.I2C(board.SCL, board.SDA)
else:
    i2c = busio.I2C(board.SCL_1, board.SDA_1)

pca = PCA9685(i2c)
pca.frequency = 50
cuffServo = servo.Servo(pca.channels[15], min_pulse=650, max_pulse=2650)

# --- Declaracion de funciones

def getPressure(sensor: int = 1, offset=27.0, pressureRef = 200.0, valueRef=2960.0):
    if sensor == 1:
        pressure_raw = ADS.readADC_Differential_0_1()
    else:
        pressure_raw = ADS.readADC_Differential_2_3()

    pressure = (pressure_raw-offset)*(pressureRef)/(valueRef-offset)
    return float(pressure)

def convertPressure(p_raw, offset, pressureRef, valueRef):
    pressure = (p_raw-offset)*(pressureRef)/(valueRef-offset)
    return float(pressure)

if __name__ == "__main__":

    try:
        while True:
            raw01 = ADS.readADC_Differential_0_1()
            pre01 = convertPressure(p_raw=raw01, offset=11, pressureRef=200.0, valueRef=2960)

            raw23 = ADS.readADC_Differential_2_3()
            pre23 = convertPressure(p_raw=raw23, offset=-21, pressureRef=200.0, valueRef=2870)

            print(f"\rPresión 0-1: {pre01:.2f}   |   Presión 2-3: {pre23:.2f}mmHg           ", end="")

            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print("\nLectura interrumpida por el usuario.")
