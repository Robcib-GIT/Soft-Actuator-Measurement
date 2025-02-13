import Jetson.GPIO as GPIO
import time

# Configuración del pin GPIO para el servo
SERVO_PIN = 33  # Cambia esto según el pin que estés usando
FREQ = 50  # Frecuencia del PWM en Hz

# Configurar el modo de la Jetson Nano
GPIO.setmode(GPIO.BOARD)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Crear el objeto PWM
pwm = GPIO.PWM(SERVO_PIN, FREQ)
pwm.start(0)

def set_angle(angle):
    min_dc = 5    # 1ms → 5% (0°)
    max_dc = 10   # 2ms → 10% (180°)
    duty_cycle = ((angle / 180) * (max_dc - min_dc)) + min_dc
    pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(0.5)


try:
    while True:
        angle = float(input("Introduce el ángulo (0-180): "))
        if 0 <= angle <= 180:
            set_angle(angle)
        else:
            print("Por favor, introduce un ángulo entre 0 y 180 grados.")

except KeyboardInterrupt:
    print("\nSaliendo...")
    pwm.stop()
    GPIO.cleanup()
