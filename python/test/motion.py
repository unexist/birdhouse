#!/usr/bin/python3 

##
# @package birdhouse
#
# @file Motion test
# @copyright 2021 Christoph Kappel <christoph@unexist.dev>
# @version $Id$
#
# This program can be distributed under the terms of the GNU GPLv3.
# See the file LICENSE for details.
##

import RPi.GPIO as GPIO
from time import sleep
 
SENSOR_PIN = 23
 
GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSOR_PIN, GPIO.IN)

def motion_callback(channel):
    print("Motion!")
 
try:
    GPIO.add_event_detect(SENSOR_PIN , GPIO.RISING, callback=motion_callback)
    while True:
        sleep(100)
except KeyboardInterrupt:
    print("Exit")

GPIO.cleanup()
