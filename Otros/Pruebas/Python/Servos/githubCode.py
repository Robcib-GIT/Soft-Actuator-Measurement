"""
https://github.com/madara-tribe/HW-Jetson-PWM-PX3.1/tree/main
"""
import RPi.GPIO as GPIO
import time

output_pins = {
    'JETSON_XAVIER': 18,
    'JETSON_NANO': 33,
    'JETSON_NX': 33,
    'CLARA_AGX_XAVIER': 18,
    'JETSON_TX2_NX': 32,
    'JETSON_ORIN': 18,
}
output_pin = output_pins.get(GPIO.model, None)
if output_pin is None:
    raise Exception('PWM not supported on this board')


def main():
    # Pin Setup:
    # Board pin-numbering scheme
    GPIO.setmode(GPIO.BOARD)
    # set pin as an output pin with optional initial state of HIGH
    GPIO.setup(32, GPIO.OUT, initial=GPIO.HIGH)
    p = GPIO.PWM(output_pin, 50)
    val = 7.25
    incr = 0.25
    p.start(val)

    print("PWM running. Press CTRL+C to exit.")
    try:
        while True:
            time.sleep(1)
            if val >= 12:
                incr = -incr
            if val <= 2.5:
                incr = -incr
            val += incr
            p.ChangeDutyCycle(val)
    finally:
        p.stop()
        GPIO.cleanup()

if __name__ == '__main__':
    main()