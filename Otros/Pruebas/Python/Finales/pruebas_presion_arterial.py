import time

import ADS1x15
import board
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685

from Utilities.blood_pressure import BloodPressure
from Utilities.data_operations import save_data

"""
 I2C BUS 0 (SCL: 28 | SDA: 27)
 I2C BUS 1 (SCL: 5  |  SDA: 3)
"""

# --- Constantes y variables presión arterial --- TODO: refinar cuando complete el actuador
BUS_I2C_ADS115 = 0
ADS = ADS1x15.ADS1115(BUS_I2C_ADS115, 0x48)
ADS.setGain(ADS.PGA_0_512V)

pressure_fs = 25  # Hz
bp = BloodPressure(pressure_fs)

# --- Constantes y variables servos --- TODO: refinar rangos servo y angulos
INFLATE_ANGLE = 90
DEFLATE_ANGLE = 26
IDLE_ANGLE = 180
BUS_I2C_PCA965 = 0

if BUS_I2C_PCA965 == 1:  #
    i2c = board.I2C()  # o busio.I2C(board.SCL, board.SDA)
else:
    i2c = busio.I2C(board.SCL_1, board.SDA_1)

pca = PCA9685(i2c)
pca.frequency = 50
cuffServo = servo.Servo(pca.channels[15], min_pulse=650, max_pulse=2650)
#TODO: añadir servo actuador


# --- Declaracion de funciones presion arterial ---
def get_pressure(offset=27.0, pressure_ref=200.0, value_ref=2960.0):     # TODO: quitar al usar ROS
    pressure_raw = ADS.readADC_Differential_0_1()
    pressure = (pressure_raw - offset) * pressure_ref / value_ref
    time.sleep(bp.sample_interval)
    return float(pressure)


# --- Declaracion de funciones servos ---
def initialize_servo_pos():
    cuffServo.angle = 0
    while True:
        cuff_pressure = get_pressure()
        if cuff_pressure >= 5.0:
            print(f"Desinflando manguito: {cuff_pressure}mmHg        ", end="\r")
        else:
            break
    time.sleep(2)

    # TODO: añadir inicializacion de actuador


# --- Bucle principal con PID ---
if __name__ == "__main__":
    print("Proceso de lectura de presión arterial iniciado")
    initialize_servo_pos()
    cuffServo.angle = INFLATE_ANGLE
    time.sleep(0.5)

    # Medir presiones
    deflating = False
    pressures = [0.0]  # Vector para guardar todas las presiones

    while True:
        pressure = get_pressure()
        pressures.append(pressure)
        p_velocity = bp.calculate_velocity(pressures)
        print(f"\rPresión: {pressure:.2f} mmHg  |   V_presión: {p_velocity:.2f} mmHg/s   |  Ángulo: {cuffServo.angle}         ",
              end="")

        # Cuando llega a cierta presión comienza a desinflarse
        if not deflating and pressure > 190:
            cuffServo.angle = DEFLATE_ANGLE
            deflating = True
        # Se abre completamente para terminar de desinflarse
        elif deflating and pressure < 15:
            print("\nTerminada medición")
            cuffServo.angle = 0
            break
        # Proceso de desinflado controlado
        elif deflating:  # TODO: ajustar y mejorar
            if p_velocity > -3 and (pressures[-1] - pressures[-2]) > 50:
                cuffServo.angle -= 2

    # Procesar información
    sys, dia = bp.get_blood_pressure(pressures)
    bp.plot_results()
    save_data([bp.time, bp.pressures], ["Pressure [mmHg]", "Time [s]"])



