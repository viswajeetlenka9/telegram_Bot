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
from telegram import *
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters


PORT = int(os.environ.get('PORT', 8443))

def get_download_url_from_api(url):
    API_URL = "https://getvideo.p.rapidapi.com/"
    query_string = {"url": f"{url}"}

    headers = {
        'x-rapidapi-host': "getvideo.p.rapidapi.com",
        'x-rapidapi-key': "b71057ccbdmshbdb08c316cac5c0p17d423jsna96364d48563"
    }

    response = requests.get(API_URL, headers=headers, params=query_string)
    data = response.json()
    return data['streams'][0]['url']


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(text='Welcome to URL downloader!\nPlease provide a valid URL')


def textHandler(update: Update, context: CallbackContext) -> None:
    user_message = str(update.message.text)
    # if update.message.parse_entities(types=MessageEntity.URL):
    #     download_url = get_download_url_from_api(user_message)
    #     update.message.reply_text(text="You sent a valid URL!", quote=True)
    #     update.message.reply_text(text=f"Your download url is : {download_url}")
    update.message.reply_text(user_message)


def main():
    TOKEN = "5195793507:AAF5dfs4l4MXjU2kXOfsU9-DLgb5MBxONIc"
    updater = Updater(TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(MessageHandler(Filters.all & ~Filters.command, textHandler, run_async=True))
    # updater.start_polling()
    # updater.start_webhook(listen='0.0.0.0', port=int(PORT), url_path=TOKEN)
    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN,
                          webhook_url='https://youtubetelegrambot.herokuapp.com/'+TOKEN)
    # updater.bot.setWebhook('https://youtubetelegrambot.herokuapp.com/'+TOKEN)

    updater.idle()


if __name__ == "__main__":
    main()
