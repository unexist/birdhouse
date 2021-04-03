#!/usr/bin/python3 

##
# @package birdhouse
#
# @file Animation test
# @copyright 2021 Christoph Kappel <christoph@unexist.dev>
# @version $Id$
#
# This program can be distributed under the terms of the GNU GPLv3.
# See the file LICENSE for details.
##

from picamera import PiCamera
from time import sleep
from os import system

# Globals
camera = PiCamera()
camera.start_preview()
sleep(1)

for i in range(10):
    camera.capture("image{0:04d}.jpg".format(i))

system("convert -delay 10 -loop 0 image*.jpg animation.gif")

print("Done")

camera.stop_preview()
