import os
from dotenv import load_dotenv

from datetime import datetime
import math
import requests

import logging
from telegram import *
from telegram.ext import *

load_dotenv()
BOT_API_KEY = os.environ.get('BOT_API_KEY')
WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')
COVID_API_KEY = os.environ.get('COVID_API_KEY')

print('Bot started...')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


logger = logging.getLogger(__name__)

HANDLE = range(1)


def start_cmd(update, context):
    user = update.effective_user

    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
    )

    reply_keyboard = [['Time', 'Weather', 'Covid']]

    update.message.reply_text(
        "Hi! I'm LTUD's bot. I will hold a conversation with you.\n"
        "Use /set <seconds> to set a timer or type /unset to stop.\n"
        'Send /help to get help from me or send /cancel to stop asking to me.\n\n'
        'Want to know the time, the weather or the covid?',

        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Time or weather?'
        ),
    )

    return HANDLE


def time():
    now = datetime.today()

    date_time = now.strftime('%d/%m/%y, %H:%M:%S')

    return date_time + '  🍔'


def weather():
    city = 'Da Nang'
    base_url = 'http://api.openweathermap.org/data/2.5/weather?q=' + \
        city + '&appid=' + WEATHER_API_KEY + '&units=metric&lang=vi'
    response = requests.get(base_url).json()

    description = response['weather'][0]['description'].capitalize()
    temp = math.ceil(int(response['main']['temp']))

    result = fr'{description}, {temp}°C  ⛅'

    return result


def covid():
    base_url = COVID_API_KEY
    response = requests.get(base_url).json()

    def seperate(num):
        i = 1
        result = ''

        for letter in reversed(str(num)):
            result += letter

            if i % 3 == 0:
                result += '.'
            i += 1

        if result[-1] == '.':
            result = result[:-1]

        return ''.join(reversed(result))

    infected = seperate(response['infected'])
    treated = seperate(response['treated'])
    recovered = seperate(response['recovered'])
    deceased = seperate(response['deceased'])

    result = fr'Số ca nhiễm: {infected}' + '\n'
    result += fr'Đang điều trị: {treated}' + '\n'
    result += fr'Số ca hồi phục: {recovered}' + '\n'
    result += fr'Giảm {deceased} so với các ngày trước  😢'

    return result


def timer(context):
    job = context.job
    context.bot.send_message(job.context, text=time())


def setTimer(update, context):
    chat_id = update.message.chat_id
    text = 'Timer successfully set!'
    error = 'Please type: /set <seconds>'

    try:
        due = int(context.args[0])

        context.job_queue.run_repeating(timer, interval=due, context=chat_id)
        update.message.reply_text(text)

    except ValueError:
        update.message.reply_text(error)


def unsetTimer(update, context):
    text = 'Timer successfully cancelled!'

    context.job_queue.stop()
    update.message.reply_text(text)


def handleInput(update, context):
    msg = (update.message.text).lower()

    if msg == 'time':
        update.message.reply_text(
            time(), reply_markup=ReplyKeyboardRemove())
    elif msg == 'weather':
        waiter = 'Hold on ...  🐢'

        # wait to fetch data
        update.message.reply_text(waiter, reply_markup=ReplyKeyboardRemove())

        update.message.reply_text(
            weather(), reply_markup=ReplyKeyboardRemove())
    elif msg == 'covid':
        waiter = 'Wai a minute ...  😷'
        remind = 'Wear a mask to protect yourself and those around you!'

        # wait to fetch data
        update.message.reply_text(waiter, reply_markup=ReplyKeyboardRemove())
        update.message.reply_text(covid(), reply_markup=ReplyKeyboardRemove())
        update.message.reply_text(remind, reply_markup=ReplyKeyboardRemove())


def echo(update, context):
    update.message.reply_text(update.message.text)


def help_cmd(update, context):
    update.message.reply_text(
        'If you need help! You should ask for it on Google!')


def cancel_cmd(update, context):
    user = update.message.from_user

    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main():
    updater = Updater(BOT_API_KEY)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_cmd)],
        states={
            HANDLE: [MessageHandler(Filters.regex('^(Time|Weather|Covid|time|weather|covid)$'), handleInput), CommandHandler('cancel', cancel_cmd)],
        },
        fallbacks=[CommandHandler('cancel', cancel_cmd)],
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("set", setTimer))
    dp.add_handler(CommandHandler("unset", unsetTimer))
    dp.add_handler(CommandHandler("help", help_cmd))
    dp.add_handler(MessageHandler(Filters.text, echo))

    updater.start_polling()

    updater.idle()


main()
