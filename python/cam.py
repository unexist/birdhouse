#!/usr/bin/python3 

from picamera import PiCamera
from time import sleep

# Globals
camera = PiCamera()
camera.start_preview()
sleep(1)
camera.capture('/home/pi/image.jpg')
camera.stop_preview()
