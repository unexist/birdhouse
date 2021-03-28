#!/usr/bin/python3 
import RPi.GPIO as GPIO
#from picamera import PiCamera
from time import sleep
 
SENSOR_PIN = 23
 
GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSOR_PIN, GPIO.IN)

#camera = PiCamera()
 
def motion_callback(channel):
    #camera.start_preview()
    #sleep(5)
    #camera.capture('/home/pi/image.jpg')
    #camera.stop_preview()    

    print('Es gab eine Bewegung!')
 
try:
    GPIO.add_event_detect(SENSOR_PIN , GPIO.RISING, callback=motion_callback)
    while True:
        sleep(100)
except KeyboardInterrupt:
    print("Exit")

GPIO.cleanup()
