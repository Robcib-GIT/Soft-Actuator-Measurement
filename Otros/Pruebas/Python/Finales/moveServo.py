import board
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
import busio

"""
 I2C BUS 0 (SCL: 28 | SDA: 27)
 I2C BUS 1 (SCL: 5  |  SDA: 3)
"""
BUS_I2C_PCA965 = 0

if BUS_I2C_PCA965 == 1:  #
    i2c = board.I2C()  # o busio.I2C(board.SCL, board.SDA)
else:
    i2c = busio.I2C(board.SCL_1, board.SDA_1)


# Create a simple PCA9685 class instance.
pca = PCA9685(i2c)
pca.frequency = 50

myServo = servo.Servo(pca.channels[15], min_pulse=650, max_pulse=2650) #650-2650

try:
    while True:
        angle = int(input("Introduce un angulo: "))
        myServo.angle = max(0, min(180, angle))
except KeyboardInterrupt:
    print("\nInterrumpido por el usuario. Saliendo...")


pca.deinit()