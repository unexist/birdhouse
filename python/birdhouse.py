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
from glob import glob
import os
import logging

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, PicklePersistence

import RPi.GPIO as GPIO
from picamera import PiCamera

# Globals
SENSOR_PIN = 23
CAMERA = None
DISPATCHER = None

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

LOGGER = logging.getLogger(__name__)

# Event handler
def alarm_callback(context: CallbackContext) -> None:
    LOGGER.info("Alarm called")

    # Ignore future motion callbacks to avoid stacking
    DISPATCHER.bot_data["ignore_callbacks"] = True

    # Collect images
    imgList = glob(os.getcwd() + "/image-*.jpg")

    LOGGER.info("Found %d images", len(imgList))

    # Convert if more than one
    if 1 < len(imgList):
        LOGGER.info("Convert images - start")
        os.system("convert -delay 15 -loop 0 image-*.jpg anim.gif")
        LOGGER.info("Convert images - stop")

    # Send to subscribers
    LOGGER.info("Send file - start")
    for userid, username in DISPATCHER.user_data.items():
        LOGGER.info("Send message to %s", username)
        DISPATCHER.bot.send_message(chat_id=userid, text="Chirp! Chirp!")

        # Select file
        if os.path.isfile("anim.gif"):
            DISPATCHER.bot.send_animation(chat_id=userid, animation=open("anim.gif", "rb"))
        else:
            for img in imgList:
                DISPATCHER.bot.send_photo(chat_id=userid, photo=open(img, "rb"))
    LOGGER.info("Send file - stop")

    # Tidy up
    LOGGER.info("Tidy up - start")
    if os.path.isfile("anim.gif"):
        os.remove("anim.gif")

    for img in imgList:
        if os.path.isfile(img):
            os.remove(img)
    LOGGER.info("Tidy up - stop")

    # Lift ignore
    DISPATCHER.bot_data["ignore_callbacks"] = False

def motion_callback(channel):
    if True != DISPATCHER.bot_data["ignore_callbacks"]:
        # Take photo for current timestamp
        LOGGER.info("Take photo - start")
        CAMERA.start_preview()
        sleep(1)
        CAMERA.capture(os.getcwd() + "/image-{:d}.jpg".format(int(time())))
        CAMERA.stop_preview()
        LOGGER.info("Take photo - stop")

        # Schedule job
        LOGGER.info("Reschedule jobs - start")
        for job in DISPATCHER.job_queue.get_jobs_by_name("motion"):
            job.schedule_removal()

        DISPATCHER.job_queue.run_once(alarm_callback, when=10, name="motion")
        LOGGER.info("Reschedule jobs - stop")

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

    LOGGER.info("Take photo - start")
    CAMERA.start_preview()
    sleep(1)
    CAMERA.capture(os.getcwd() + "/pic.jpg")
    CAMERA.stop_preview()
    LOGGER.info("Take photo - stop")

    context.bot.send_photo(chat_id=update.message.from_user.id, photo=open(os.getcwd() + "/pic.jpg", "rb"))

def die_command(update: Update, context: CallbackContext) -> None:
    # Send to subscribers
    LOGGER.info("Update subscriber - start")
    for userid, username in context.user_data.items():
        LOGGER.info("Send message to %s" % username)
        context.bot.send_message(chat_id=userid, text="Going back to slumber! zZzZ")
    LOGGER.info("Update subscriber - stop")

    os.system("convert -delay 20 -loop 0 image-*.jpg anim.gif")

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

    GPIO.add_event_detect(SENSOR_PIN, GPIO.RISING, callback=motion_callback, bouncetime=500)

    # Set up telegram / persistence
    pickle_data = PicklePersistence(filename="birdhouse.dat")

    updater = Updater(os.environ.get("TOKEN"), persistence=pickle_data, use_context=True)

    # Add dispatcher commands
    DISPATCHER = updater.dispatcher

    DISPATCHER.add_handler(CommandHandler("sub", sub_command))
    DISPATCHER.add_handler(CommandHandler("unsub", unsub_command))
    DISPATCHER.add_handler(CommandHandler("pic", pic_command))
    DISPATCHER.add_handler(CommandHandler("die", die_command))
    DISPATCHER.add_handler(CommandHandler("help", help_command))

    DISPATCHER.bot_data["ignore_callbacks"] = False

    updater.start_polling()

    # Say hello to all known users
    LOGGER.info("Update subscriber - stop")
    for userid, username in DISPATCHER.user_data.items():
        DISPATCHER.bot.send_message(chat_id=userid, text="Ready for duty!")
    LOGGER.info("Update subscriber - stop")
    LOGGER.info("Ready")

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    updater.idle()

    GPIO.cleanup()
