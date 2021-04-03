#!/usr/bin/python3

##
# @package birdhouse
#
# @file Birdhouse main
# @copyright 2021 Christoph Kappel <christoph@unexist.dev>
# @version $Id$
#
# This program can be distributed under the terms of the GNU GPLv3.
# See the file LICENSE for details.
##

from time import sleep, time
from copy import copy
from glop import glob
import os
import logging

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, PicklePersistence

import RPi.GPIO as GPIO
from picamera import PiCamera

# Globals
SENSOR_PIN = 23
CAMERA = None
BOT = None

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

LOGGER = logging.getLogger(__name__)

# Event handler
def alarm(context: CallbackContext) -> None:
    LOGGER.info("Alarm called - scanning files")

    imgList = glob(os.getcwd() + "/image-*.jpg")

    if 1 < len(imgList):
        LOGGER.info("Converting {:d} images..", len(imgList))
        system("convert -delay 5 -loop 0 image-*.jpg anim.gif")

    # Send to subscribers
    for userid, username in context.bot.user_data.items():
        LOGGER.info("Send message to %s", username)
        BOT.send_message(chat_id=userid, text="Chirp! Chirp!")

        # Select file
        if os.path.isFile("anim.gif"):
            BOT.send_animation(chat_id=userid, animation=open("anim.gif", "rb"))
            os.remove("anim.gif")
        else:
            for img in imgList:
                BOT.send_photo(chat_id=userid, photo=open(img, "rb"))
                os.remove(img)

def motion_callback(channel):
    # Take photo for current timestamp
    LOGGER.info("Taking photo")
    CAMERA.start_preview()
    sleep(1)
    CAMERA.capture(getcwd() + "/image-{:d}.jpg".format(int(time())))
    CAMERA.stop_preview()

    # Schedule job
    for job in BOT.job_queue.get_jobs_by_name("motion"):
        LOGGER.info("Rescheduling alarm..")
        job.schedule_removal()

    BOT.job_queue.run_once(alarm, 3, context=None, name="motion")

# Commands
def sub_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Hi %s, thanks for the subscription!" % update.message.from_user.username)

    # Store user
    context.user_data[update.message.from_user.id] = update.message.from_user.username

    LOGGER.info("%s subscribed to updates", update.message.from_user.username)

def unsub_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Bye bye %!" % update.message.from_user.username)

    # Delete user
    del context.user_data[update.message.from_user.id]

    LOGGER.info("%s unsubscribed from updates", update.message.from_user.username)

def pic_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Say cheese!")

    LOGGER.info("Taking photo")
    CAMERA.start_preview()
    sleep(1)
    CAMERA.capture(os.getcwd() + "/pic.jpg")
    CAMERA.stop_preview()

    context.bot.send_photo(chat_id=update.message.from_user.id, photo=open(os.getcwd() + "/pic.jpg", "rb"))

def die_command(update: Update, context: CallbackContext) -> None:
    # Send to subscribers
    for userid, username in context.user_data.items():
        LOGGER.info("Send message to %s" % username)
        context.bot.send_message(chat_id=userid, text="Going back to slumber! zZzZ")

def help_command(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(
        "Available commands:"
        "/sub   - Subcribe to updates"
        "/unsub - Unsubscribe from updates"
        "/pic   - Take a picture"
        "/die   - Shutdown"
    )

if __name__ == "__main__":
    # Sanity check
    if os.environ.get("TOKEN") is None:
        LOGGER.info("Env var TOKEN is required!")
        exit()

    # Set up cam
    CAMERA = PiCamera()
    CAMERA.rotation = 180

    # Set up GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SENSOR_PIN, GPIO.IN)

    GPIO.add_event_detect(SENSOR_PIN, GPIO.RISING, callback=motion_callback)

    # Set up telegram / persistence
    pickle_data = PicklePersistence(filename="birdhouse.dat")

    updater = Updater(os.environ.get("TOKEN"), persistence=pickle_data, use_context=True)

    # Add dispatcher commands
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("sub", sub_command))
    dispatcher.add_handler(CommandHandler("unsub", unsub_command))
    dispatcher.add_handler(CommandHandler("pic", pic_command))
    dispatcher.add_handler(CommandHandler("die", die_command))
    dispatcher.add_handler(CommandHandler("help", help_command))

    updater.start_polling()

    # FIXME: STUPID!
    BOT = copy(updater.bot)

    # Say all known users hello
    for userid, username in dispatcher.user_data.items():
        BOT.send_message(chat_id=userid, text="Ready for duty!")

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    updater.idle()

    GPIO.cleanup()
