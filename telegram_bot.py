# """
# Simple Bot to download youtube videos.
#
# First, a few handler functions are defined. Then, those functions are passed to the Dispatcher and registered
# at their respective places.
# Then, the bot is started and runs until we press Ctrl + C on the command line.
#
# Usage:
# Basic YoutubeBot example, gives download url for youtube video.
# Press Ctrl + C on the command line or send a signal to the process to stop the bot.
# """
#
# import logging
# from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
# from config import BotFather_config
#
# # Enable logging
# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
#
# logger = logging.getLogger(__name__)
#
#
# # Define a few command handlers. These usually take the two arguements update and context.
# # Error handlers also receive  the raised TelegramError object in error.
# def start(update, context):
#     """Send message when the command /start is issued"""
#     update.message.reply_text("Hi Babu!")
#
#
# def help(update, context):
#     """Send a message when the command /help is issued"""
#     update.message.reply_text('Help!')
#
#
# def echo(update, context):
#     """Echo the user message"""
#     update.message.reply_text(update.message.text)
#
#
# def error(update, context):
#     """Log Errors caused by updates."""
#     logger.warning('Update "%s" caused by error  "%s"', update, context.error)
#
#
# def main():
#     """Start the bot"""
#     # Create the Updater and pass it bot's token.
#     # Make sure to set use_context = True to use the new context based callbacks
#     # Post version 12 this will no longer be necessary
#     updater = Updater(BotFather_config.TOKEN, use_context=True)
#
#     # Get the dispatcher to register handlers
#     dp = updater.dispatcher
#
#     # on different commands - answer in Telegram
#     dp.add_handler(CommandHandler("start", start))
#     dp.add_handler(CommandHandler("help", help))
#
#     # on noncommand i.e message - echo the message on Telegram
#     dp.add_handler(MessageHandler(Filters.text, echo))
#
#     # log all errors
#     dp.add_error_handler(error)
#
#     # Start the bot
#     updater.start_polling()
#
#     # Run the bot until you press Ctrl + C or the process receives SIGINT, SIGTERM or SIGABRT.
#     # This should be used most of the time, since start_polling() is non-blocking and will stop
#     # the bot gracefully.
#     updater.idle()
#
#
# if __name__ == "__main__":
#     main()
import os
import requests
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from telegram import *
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters

load_dotenv('.env')

OPEN_WEATHER_ID = os.environ.get("OPEN_WEATHER_ID")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

PORT = int(os.environ.get('PORT', 8443))
key = Fernet.generate_key()


def encrypt_message(message: bytes, key: bytes):
    return Fernet(key).encrypt(message)


def decrypt_message(token: bytes, key: bytes):
    return Fernet(key).decrypt(token)


open_weather_token = encrypt_message(OPEN_WEATHER_ID.encode(), key)

telegram_token = encrypt_message(TELEGRAM_TOKEN.encode(), key)


def get_geocode_by_zip(zip_code):
    try:
        url = "http://api.openweathermap.org/geo/1.0/zip"
        api_key = decrypt_message(open_weather_token, key).decode()
        params = {"zip": f"{zip_code},IN", "appid": api_key}

        response = requests.get(url=url, params=params)
        return response.json()
    except Exception as ex:
        return "Geo location not present in India"


def get_current_weather_by_geocode(lat, lon):
    url = "https://api.openweathermap.org/data/2.5/weather"
    api_key = decrypt_message(open_weather_token, key).decode()
    params = {"lat": lat, "lon": lon, "appid": api_key}

    response = requests.get(url=url, params=params)
    return response.json()


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(text='Welcome to Weather Update!\nPlease provide a zip code')


def textHandler(update: Update, context: CallbackContext) -> None:
    user_message = str(update.message.text)

    # if update.message.parse_entities(types=MessageEntity.URL):
    #     download_url = get_download_url_from_api(user_message)
    #     update.message.reply_text(text="You sent a valid URL!", quote=True)
    #     update.message.reply_text(text=f"Your download url is : {download_url}")
    if len(user_message) != 6:
        update.message.reply_text(text="Please provide a valid pin code")
    result_geocode = get_geocode_by_zip(user_message)
    if result_geocode:
        res = get_current_weather_by_geocode(result_geocode.get('lat'), result_geocode.get('lon'))
        weather_result_text = 'Weather = {0}\n' \
                              'Tempertaure = {1}\n' \
                              'Feels like = {2}'.format(res.get('weather')[0].get('description'),
                                                        round(float(res.get('main').get('temp')) - 273.15, 2),
                                                        round(float(res.get('main').get('feels_like')) - 273.15, 2))
        update.message.reply_text(weather_result_text)
    else:
        update.message.reply_text(text="Provided pin code could not be found in India")


def main():
    TOKEN = decrypt_message(telegram_token, key).decode()
    updater = Updater(TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(MessageHandler(Filters.all & ~Filters.command, textHandler, run_async=True))
    updater.start_polling()
    # updater.start_webhook(listen='0.0.0.0', port=int(PORT), url_path=TOKEN)
    # updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN,
    #                       webhook_url='https://youtubetelegrambot.herokuapp.com/' + TOKEN)
    # updater.bot.setWebhook('https://youtubetelegrambot.herokuapp.com/'+TOKEN)

    updater.idle()


if __name__ == "__main__":
    main()
