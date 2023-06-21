import RPi.GPIO as GPIO
import time


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

# Cofigurar pin de salida. Set initial state
GPIO.setup(7, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(5, GPIO.OUT, initial=GPIO.LOW)

time.sleep(1)

while(True):
    GPIO.output(7,GPIO.HIGH)
    GPIO.output(5,GPIO.HIGH)
    time.sleep(1)

    GPIO.output(7,GPIO.LOW)
    GPIO.output(5,GPIO.LOW)
    time.sleep(1)
