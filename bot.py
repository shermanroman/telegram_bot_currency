#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import requests
import json

from telegram import *
from telegram.ext import *

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ContextTypes

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# chat_id
# [0] countryOfUser
# [1] first_currency
# [2] second_currency
users = dict()

startOver = 'Начать сначала'
connectOperator = 'Связаться с оператором'

countrysOfUser_rus = [
    ['Россия'],
    ['Канада'],
    ['Мексика'],
    [connectOperator],
    [startOver]
]

typeOfAction_rus = [
    ['Купить'],
    ['Продать'],
    [connectOperator],
    [startOver]
]

firstCurrency_rus = [
    ['BTC'],
    ['USDT'],
    [connectOperator],
    [startOver]
]

secondCurrency_rus = [
    ['USDT'],
    ['BTC'],
    [connectOperator],
    [startOver]
]

generalButtons_rus = [
    [connectOperator],
    [startOver]
]


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    users[update.effective_chat.id] = dict()

    message = ('Добрый день. Выберите страну в которой хотете получить или сделать перевод:')

    buttons = countrysOfUser_rus

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=message,
                             reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True))


def method_to_get(update, context):
    # [0] countryOfUser
    users[update.effective_chat.id][0] = update.message.text

    message = ('Выберите тип сделки:')

    buttons = typeOfAction_rus

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=message,
                             reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True))


def first_currency(update, context):
    # [1] first_currency
    users[update.effective_chat.id][1] = update.message.text

    message = ('Выберите валюту из которой нужно совершить перевод:')

    buttons = firstCurrency_rus

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=message,
                             reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True))


def second_currency(update, context):
    # [2] second_currency
    users[update.effective_chat.id][2] = update.message.text

    message = ('Выберите валюту в которую нужно совершить перевод:')

    buttons = secondCurrency_rus

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=message,
                             reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True))


def amount(update, context):
    # [2] second_currency
    users[update.effective_chat.id][3] = update.message.text

    message = ('Введите сумму:')

    buttons = generalButtons_rus

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=message,
                             reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True))


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def convert_amount(update, context):

    users[update.effective_chat.id][4] = update.message.text
    first_currency_string = users[update.effective_chat.id][2]
    second_currency_string = users[update.effective_chat.id][3]

    url = "https://api.binance.com/api/v3/ticker/price?symbol=" + first_currency_string + second_currency_string

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    responseJSON = json.loads(response.text)

    update.message.reply_text('Курс обмена для ' + responseJSON['symbol'])
    update.message.reply_text('Цена обмена: ' + responseJSON['price'])
    amountFromClient = update.message.text
    amountToPay = responseJSON['price'] * amountFromClient
    update.message.reply_text('Стоимость к оплате: ' + amountToPay)
    update.message.reply_text('Курс взят из платформы binance.')


def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def messageHandler(update: Update, context: CallbackContext):
    updateText = update.message.text

    if updateText == connectOperator:
        echo(update, context)
        return

    if updateText == startOver:
        start(update, context)
        return

    for countryOfUser in countrysOfUser_rus:
        if countryOfUser[0] == updateText:
            method_to_get(update, context)
            return

    for typeOfAction in typeOfAction_rus:
        if typeOfAction[0] == updateText:
            first_currency(update, context)
            return

    if 2 not in users[update.effective_chat.id]:
        for firstCurrency in firstCurrency_rus:
            if firstCurrency[0] == updateText:
                second_currency(update, context)
                return

    if 2 not in users[update.effective_chat.id]:
        for secondCurrency in secondCurrency_rus:
            if secondCurrency[0] == updateText:
                second_currency(update, context)
                return


    if 3 not in users[update.effective_chat.id]:
        amount(update, context)
        return

    if 4 not in users[update.effective_chat.id]:
        convert_amount(update, context)
        return


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("5580543576:AAGdgsSgi9EMGmGgsnWhnQOl9lSgodtn4Rs", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(MessageHandler(Filters.text, messageHandler))

    # on noncommand i.e message - echo the message on Telegram
    # dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
