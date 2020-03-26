from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from filters import UrlFilter
from scraper import SoupStrainer
from util import buildRow
import config
import re
import pickle
import os.path as path
import logging

# Enable logging of errors
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# Relevant variable declarations
updater = Updater(token=config.bot_token, use_context=True)
dispatcher = updater.dispatcher
url_filter = UrlFilter()
svc_model = pickle.load(
    open(path.join(config.base_dir, 'svc_model.sav'), 'rb'))


def start(update, context):
    with open(path.join(config.base_dir, 'start_message.txt')) as reader:
        text = reader.read()

    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def check_url(update, context):
    chat_id = update.effective_chat.id
    ss = SoupStrainer()
    ss.init()
    if ss.loadAddress(update.message.text):
        article = buildRow(ss.extractText)
        article = article.reshape(1, -1)
        svc_prediction = svc_model.predict(article)
        svc_probabilities = svc_model.predict_proba(article)

        print('*** SVC ')
        print('Prediction on this article is: ')
        print(svc_prediction)
        print('Probabilities:')
        print(svc_probabilities)
    else:
        context.bot.send_message(
            chat_id=chat_id, text='There was a problem loading page data.')

    context.bot.send_message(chat_id=chat_id, text='Yeeah')



# Creating the command/message handlers
start_handler = CommandHandler('start', start)
url_handler = MessageHandler(url_filter, check_url)

# Adding the handlers to the dispatcher
dispatcher.add_handler(start_handler)
dispatcher.add_handler(url_handler)


# Starting the bot
updater.start_polling()
updater.idle()
