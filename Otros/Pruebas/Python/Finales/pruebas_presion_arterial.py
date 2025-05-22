import time
from typing import List
import matplotlib.pyplot as plt

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
ADS = ADS1x15.ADS1115(BUS_I2C_ADS115, 0x48)
ADS.setGain(ADS.PGA_0_512V)

pressure_fs = 100  # Hz  # TODO: variar si eso pero con 100 va bien
bp = BloodPressure(pressure_fs)

ACTUATOR_GOAL_PRESSURE = 600.0
CUFF_GOAL_PRESSURE = 190.0

# --- Constantes y variables servos --- TODO: refinar rangos servo y angulos
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


# --- Declaracion de funciones presion arterial ---
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

    time.sleep(bp.sample_interval)  # TODO: para pruebas solo
    return float(pressure)


# --- Declaracion de funciones servos ---


# --- Otros---

def set_pump_state(on: bool = False):
    if on:
        GPIO.output(RELAY_PIN, GPIO.HIGH)
        print("Bomba neumática activada")
    else:
        GPIO.output(RELAY_PIN, GPIO.LOW)
        print("Bomba neumática desactivada")


def measure_bp():
    pressures = []

    print("-----------------------------------")
    print("Midiendo presión arterial", end="\n")

    print("\n1- Desinflando completo manguito")
    actuator_servo.angle = ACTUATOR_BRIDGE_ANGLE
    cuff_servo.angle = CUFF_FULL_DEFLATE_ANGLE
    while True:
        cuff_pressure = get_pressure(sensor="cuff")
        print(f"\rCuff pressure: {cuff_pressure:.2f}", end="")
        if cuff_pressure <= 5:
            print("\nManguito completamente vacío")
            break

    print("\n2- Inflado manguito")
    cuff_servo.angle = CUFF_INFLATE_ANGLE
    set_pump_state(on=True)
    while True:
        cuff_pressure = get_pressure(sensor="cuff")
        print(f"\rCuff pressure: {cuff_pressure:.2f}", end="")
        pressures.append(cuff_pressure)
        if cuff_pressure >= CUFF_GOAL_PRESSURE:
            set_pump_state(on=False)
            # cuff_servo.angle = CUFF_DEFLATE_ANGLE
            print("\nManguito inflado")
            break

    print("\n3- Desinfado controlado manguito")
    while True:
        cuff_pressure = get_pressure(sensor="cuff")

        if cuff_pressure <= 40.0:
            print("\nMedición terminada")
            # Dejar salir el resto del aire al terminar
            cuff_servo.angle = CUFF_FULL_DEFLATE_ANGLE
            break

        pressures.append(cuff_pressure)
        p_velocity = bp.calculate_velocity(pressures=pressures, sample_time=0.5) 

        print(
            f"\rCuff pressure: {cuff_pressure:.2f}  |  Cuff v_pressure: {p_velocity:.2f}     ", end="")

    return pressures


def open_actuator():
    print("-----------------------------------")
    print("Abriendo actuador", end="\n")
    # Colocar válvulas
    cuff_servo.angle = CUFF_BRIDGE_ANGLE
    actuator_servo.angle = ACTUATOR_DEFLATE_ANGLE

    while True:
        actuator_pressure = get_pressure(sensor="actuator")
        print(f"\rActuator pressure: {actuator_pressure:.2f}      ", end="")
        if actuator_pressure <= 5:
            cuff_servo.angle = CUFF_BRIDGE_ANGLE
            actuator_servo.angle = ACTUATOR_BRIDGE_ANGLE
            print("\nActuador abierto")
            break


def close_actuator():
    print("-----------------------------------")
    print("Cerrando actuador", end="\n")
    # Colocar válvulas
    cuff_servo.angle = CUFF_DEFLATE_ANGLE
    actuator_servo.angle = ACTUATOR_INFLATE_ANGLE
    time.sleep(1)
    set_pump_state(on=True)

    while True:
        actuator_pressure = get_pressure(sensor="actuator")
        print(f"\rActuator pressure: {actuator_pressure:.2f}      ", end="")
        if actuator_pressure >= ACTUATOR_GOAL_PRESSURE:
            set_pump_state(on=False)
            cuff_servo.angle = CUFF_BRIDGE_ANGLE
            actuator_servo.angle = ACTUATOR_BRIDGE_ANGLE
            print("\nActuador cerrado")
            break


# --- Bucle principal con PID ---
if __name__ == "__main__":
    open_actuator()
    time.sleep(1)
    close_actuator()
    time.sleep(5)  # Para que me de tiempo
    pressures_data = measure_bp()
    time.sleep(3)
    open_actuator()

    try:
        # Procesar información
        sys, dia, ppm = bp.get_blood_pressure(pressures_data)
        print(f"SAM_SYS:  {sys}  |  SAM_DIA:  {dia}  |  SAM_PPM:  {ppm}")

    except Exception as e:
        print("Ocurrió un error al procesar los datos.")
    finally:
        bp.plot_results()

        data = {"Time": bp.time, "Pressure": bp.pressures}

        real_results = {}
        print("Introduce las lecturas reales:")
        try:
            real_sys = int(input("SYS real: "))
            real_dia = int(input("DIA real: "))
            real_ppm = int(input("PPM real: "))

            real_results["SYS"] = real_sys
            real_results["DIA"] = real_dia
            real_results["PPM"] = real_ppm

        except Exception:
            print("No se registraron datos reales")

        save_data(data_dict=data, results_dict=real_results)
        
    GPIO.cleanup()  # FIXME: error de no se qué
