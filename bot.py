import os
from dotenv import load_dotenv

from datetime import datetime

import logging
from telegram import *
from telegram.ext import *

load_dotenv()
BOT_API_KEY = os.environ.get('BOT_API_KEY')

print('Bot started...')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


logger = logging.getLogger(__name__)

TIME, WEATHER = range(2)


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

    return TIME


def time(update, context):
    now = datetime.now()
    date_time = now.strftime('%d/%m/%y, %H:%M:%S')

    update.message.reply_text(date_time, reply_markup=ReplyKeyboardRemove())


def cancel_time(update, context):
    update.message.reply_text(
        'Thank you! I hope we can talk again some day.'
    )

    return ConversationHandler.END


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
            TIME: [MessageHandler(Filters.regex('^(Time|Weather)$'), time), CommandHandler('cancel', cancel_time)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("help", help_cmd))

    updater.start_polling()

    updater.idle()


main()
