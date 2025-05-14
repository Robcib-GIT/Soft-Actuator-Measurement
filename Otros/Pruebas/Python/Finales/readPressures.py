import math
import time
from typing import List

import ADS1x15
import Jetson.GPIO as GPIO
import board
import busio
import numpy as np
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685

RELAY_PIN = 18

try:
    GPIO.setmode(GPIO.BOARD)
except ValueError:
    GPIO.cleanup()
    GPIO.setmode(GPIO.BOARD)

GPIO.setup(RELAY_PIN, GPIO.OUT)

"""
 I2C BUS 0 (SCL: 28 | SDA: 27)
 I2C BUS 1 (SCL: 5  |  SDA: 3)
"""

# --- Constantes y variables presión arterial --- TODO: refinar cuando complete el actuador
BUS_I2C_ADS115 = 1
ADS = ADS1x15.ADS1115(BUS_I2C_ADS115, 0x48)
ADS.setGain(ADS.PGA_0_512V)

pressure_fs = 40  # Hz
INTERVAL = 1 / pressure_fs

ACTUATOR_GOAL_PRESSURE = 600.0
CUFF_GOAL_PRESSURE = 190.0

# --- Constantes y variables servos
CUFF_INFLATE_ANGLE = 180
CUFF_DEFLATE_ANGLE = 115
CUFF_FULL_DEFLATE_ANGLE = 90
CUFF_BRIDGE_ANGLE = 0

ACTUATOR_INFLATE_ANGLE = 90
ACTUATOR_DEFLATE_ANGLE = 0
ACTUATOR_BRIDGE_ANGLE = 180

BUS_I2C_PCA965 = 0

if BUS_I2C_PCA965 == 1:  #
    i2c = board.I2C()  # o busio.I2C(board.SCL, board.SDA)
else:
    i2c = busio.I2C(board.SCL_1, board.SDA_1)

pca = PCA9685(i2c)
pca.frequency = 50
cuff_servo = servo.Servo(pca.channels[15], min_pulse=650, max_pulse=2650)
actuator_servo = servo.Servo(pca.channels[14], min_pulse=650, max_pulse=2650)


# --- Declaracion de funciones

def get_pressure(sensor: str):
    if sensor == "actuator":  # Actuator
        offset = -21
        pressure_ref = 200.0
        value_ref = 2870

        ADS.requestADC_Differential_0_1()  # TODO: ver si con esto soluciona
        pressure_raw = ADS.getValue()
        # pressure_raw = ADS.readADC_Differential_0_1()
    else:  # Cuff
        offset = 11
        pressure_ref = 200.0
        value_ref = 2960
        ADS.requestADC_Differential_2_3()
        pressure_raw = ADS.getValue()
        # pressure_raw = ADS.readADC_Differential_2_3()

    pressure = (pressure_raw - offset) * pressure_ref / (value_ref - offset)
    return float(pressure)


def set_pump_state(on: bool = False):
    if on:
        GPIO.output(RELAY_PIN, GPIO.HIGH)
        print("Bomba neumática activada")
    else:
        GPIO.output(RELAY_PIN, GPIO.LOW)
        print("Bomba neumática desactivada")

def calculate_velocity(pressures_list: List[float], sample_time=0.5):
    samples = max(2, math.ceil(sample_time * pressure_fs))  # al menos 2 muestras
    if len(pressures_list) < samples:
        return 0.0
    """
    delta_pressures = pressures[-1] - pressures[-samples]
    velocity = delta_pressures / samples * self.fs
    """
    delta_pressures = np.diff(samples)
    velocity = float(np.mean(delta_pressures))
    return velocity


if __name__ == "__main__":
    cuff_pressures = []
    actuator_pressures = []

    actuator_servo.angle = ACTUATOR_BRIDGE_ANGLE
    cuff_servo.angle = CUFF_INFLATE_ANGLE
    set_pump_state(on=True)
    try:
        while True:
            cuff_pressure = get_pressure("cuff")
            cuff_pressures.append(cuff_pressure)
            cuff_p_velocity = calculate_velocity(cuff_pressures, 0.5)
            if cuff_pressure >= CUFF_GOAL_PRESSURE:
                set_pump_state(on=False)

            actuator_pressure = get_pressure("actuator")
            actuator_pressures.append(actuator_pressure)
            actuator_p_velocity = calculate_velocity(actuator_pressures, 0.5)
            if actuator_pressure >= ACTUATOR_GOAL_PRESSURE:
                set_pump_state(on=False)

            print(f"\rCuff pressure: {cuff_pressure:.2f}mmHg   ({}mmHg/s)   |   Actuator pressure: {actuator_pressure:.2f}mmHg   ({}mmHg/s)           ", end="")

            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print("\nLectura interrumpida por el usuario.")
    finally:
        set_pump_state(on=False)
