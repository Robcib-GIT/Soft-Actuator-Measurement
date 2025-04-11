# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
import board
import busio

# Crear objeto I2C (usa el bus 1 en Jetson Nano)
i2c = busio.I2C(board.SCL, board.SDA)

# Crear la instancia del controlador PCA9685
pca = PCA9685(i2c)
pca.frequency = 50

# Inicializar el servo en el canal 0 con min/max personalizados
servo7 = servo.Servo(pca.channels[0], min_pulse=500, max_pulse=2400)

# Mover el servo
servo7.angle = 90
time.sleep(1)
servo7.angle = 100
time.sleep(1)
servo7.angle = 80
time.sleep(1)

# Apagar todos los canales para evitar que queden activos después
for i in range(16):
    pca.channels[i].duty_cycle = 0

# Finalizar
pca.deinit()
