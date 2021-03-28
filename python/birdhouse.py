#!/usr/bin/python3 

import RPi.GPIO as GPIO
from picamera import PiCamera
from time import sleep
import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Globals
SENSOR_PIN = 23
SUBSCRIPTIONS = {}
CAMERA = None

def motion_callback(channel):
    if 0 < len(SUBSCRIPTIONS):
        print("Taking photo")
        CAMERA.start_preview()
        sleep(1)
        CAMERA.capture(os.getcwd() + "/image.jpg")
        CAMERA.stop_preview()

        for userid, bot in SUBSCRIPTIONS.items():
            print("Send message to %s" % userid)
            bot.send_message(chat_id=userid, text="Chirp! Churp!!")
            bot.send_photo(chat_id=userid, photo=open(os.getcwd() + "/image.jpg", "rb"))
     
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

# Commands
def start_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Hi, thanks for the subscription!")

    SUBSCRIPTIONS[update.message.from_user.id] = context.bot

    print("%s subscribed to updates" % update.message.from_user.username)

def stop_command(update: Update, _: CallbackContext) -> None:
    update.message.reply_text("Bye bye!")

    del SUBSCRIPTIONS[update.message.from_user.id]

    print("%s unsubscribed from updates" % update.message.from_user.username)

def pic_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Say cheese!")

    print("Taking photo")
    CAMERA.start_preview()
    sleep(1)
    CAMERA.capture(os.getcwd() + "/image.jpg")
    CAMERA.stop_preview()

    context.bot.send_photo(chat_id=update.message.from_user.id, photo=open(os.getcwd() + "/image.jpg", "rb"))

def help_command(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(
        "Available commands:"
        "/start - Subcribe to updates"
        "/stop  - Unsubscribe from updates"
        "/pic   - Take a pictube and"
    )

if __name__ == "__main__":
    # Sanity check
    if os.environ.get("TOKEN") is None:
        print("Env var TOKEN is required!")
        exit()

    # Set up cam
    CAMERA = PiCamera()
    CAMERA.rotation = 180

    # Set up GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SENSOR_PIN, GPIO.IN)

    # Set up stuff
    GPIO.add_event_detect(SENSOR_PIN, GPIO.RISING, callback=motion_callback)

    updater = Updater(os.environ.get("TOKEN"))

    dispatcher = updater.dispatcher

    # Add dispatcher commands
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("stop", stop_command))
    dispatcher.add_handler(CommandHandler("pic", pic_command))
    dispatcher.add_handler(CommandHandler("help", help_command))

    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    updater.idle()

    GPIO.cleanup()
