#!/usr/bin/python3 

from time import sleep
import os
import copy
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, PicklePersistence
import RPi.GPIO as GPIO
from picamera import PiCamera

# Globals
SENSOR_PIN = 23
CAMERA = None
BOT = None
UDATA = {}

def motion_callback(channel):
    if 0 < len(UDATA):
        print("Taking photo")
        CAMERA.start_preview()
        sleep(1)
        CAMERA.capture(os.getcwd() + "/image.jpg")
        CAMERA.stop_preview()

        for userid, username in UDATA.items():
            print("Send message to %s" % username)
            BOT.send_message(chat_id=userid, text="Chirp! Chirp!")
            BOT.send_photo(chat_id=userid, photo=open(os.getcwd() + "/image.jpg", "rb"))
     
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

# Commands
def start_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Hi %s, thanks for the subscription!" % update.message.from_user.username)

    # Store user
    context.user_data[update.message.from_user.id] = update.message.from_user.username
    UDATA[update.message.from_user.id] = update.message.from_user.username

    print("%s subscribed to updates" % update.message.from_user.username)

def stop_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Bye bye %!" % update.message.from_user.username)

    # Delete user
    del context.user_data[update.message.from_user.id]
    del UDATA[update.message.from_user.id]

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
        "/pic   - Take a picture"
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

    GPIO.add_event_detect(SENSOR_PIN, GPIO.RISING, callback=motion_callback)

    # Set up telegram / persistence
    pickle_data = PicklePersistence(filename="birdhouse.dat")

    updater = Updater(os.environ.get("TOKEN"), persistence=pickle_data, use_context=True)

    # Add dispatcher commands
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("stop", stop_command))
    dispatcher.add_handler(CommandHandler("pic", pic_command))
    dispatcher.add_handler(CommandHandler("help", help_command))

    updater.start_polling()

    # FIXME: STUPID!
    BOT = copy.copy(updater.bot)
    UDATA = copy.copy(dispatcher.user_data)

    # Say all known users hello
    for userid, username in dispatcher.user_data.items():
        BOT.send_message(chat_id=userid, text="Ready for duty!")

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    updater.idle()

    GPIO.cleanup()
