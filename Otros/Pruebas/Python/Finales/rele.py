import Jetson.GPIO as GPIO
import time

# Configuracion pin
RELAY_PIN = 18
GPIO.setmode(GPIO.BOARD)
GPIO.setup(RELAY_PIN, GPIO.OUT)

try:
    print("Activando relé...")
    GPIO.output(RELAY_PIN, GPIO.LOW)  # LOW si el relé es activo a nivel bajo
    time.sleep(5)
    print("Desactivando relé...")
    GPIO.output(RELAY_PIN, GPIO.HIGH)
finally:
    GPIO.cleanup()
