import os
from dotenv import load_dotenv

from datetime import datetime
import math
import requests
import json

import logging
from telegram import *
from telegram.ext import *

load_dotenv()
BOT_API_KEY = os.environ.get('BOT_API_KEY')
WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')

print('Bot started...')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


logger = logging.getLogger(__name__)

# get weather response
city = 'Da Nang'
base_url = 'http://api.openweathermap.org/data/2.5/weather?q=' + \
    city + '&appid=' + WEATHER_API_KEY + '&units=metric&lang=vi'
response = requests.get(base_url).json()

# TIME, WEATHER = range(2)
HANDLE = range(1)


def start_cmd(update, context):
    user = update.effective_user

    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
    )

    reply_keyboard = [['Time', 'Weather']]

    update.message.reply_text(
        "Hi! I'm LTUD's bot. I will hold a conversation with you.\n"
        'Send /cancel to stop asking to me.\n\n'
        'Want to know the time or the weather?',

        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Time or weather?'
        ),
    )

    return HANDLE


def handle_input(update, context):
    now = datetime.now()
    date_time = now.strftime('%d/%m/%y, %H:%M:%S')

    description = response['weather'][0]['description'].capitalize()
    temp = math.ceil(int(response['main']['temp']))
    result = fr'{description}, {temp}°C'

    if (update.message.text).lower() == 'time':
        update.message.reply_text(
            date_time, reply_markup=ReplyKeyboardRemove())
    else:
        update.message.reply_text(result, reply_markup=ReplyKeyboardRemove())


def cancel(update, context):
    user = update.message.from_user

    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def help_cmd(update, context):
    update.message.reply_text(
        'If you need help! You should ask for it on Google!')


def main():
    updater = Updater(BOT_API_KEY)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_cmd)],
        states={
            HANDLE: [MessageHandler(Filters.regex('^(Time|Weather)$'), handle_input), CommandHandler('cancel', cancel)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("help", help_cmd))

    updater.start_polling()

    updater.idle()


main()
