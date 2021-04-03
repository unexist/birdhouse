#!/usr/bin/python3 

##
# @package birdhouse
#
# @file Cam test
# @copyright 2021 Christoph Kappel <christoph@unexist.dev>
# @version $Id$
#
# This program can be distributed under the terms of the GNU GPLv2.
# See the file LICENSE for details.
##

from picamera import PiCamera
from time import sleep
import os

# Globals
camera = PiCamera()
camera.start_preview()
sleep(1)
camera.capture(os.getcwd() + "/image.jpg")
camera.stop_preview()
