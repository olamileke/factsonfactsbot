from telegram import ChatAction
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from filters import UrlFilter
from scraper import SoupStrainer
from util import buildRow
import config
import re
import os
import pickle
import os.path as path
import logging

# Enable logging of errors
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# Setting the relevant configurations
config.set()

# Relevant variable declarations
token = os.environ.get("BOT_TOKEN")
updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher
url_filter = UrlFilter()
svc_model = pickle.load(
    open(path.join(config.base_dir, 'svc_model.sav'), 'rb'))


def start(update, context):
    with open(path.join(config.base_dir, 'start_message.txt')) as reader:
        text = reader.read()

    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def predict_url(update, context, text=None):
    if text is None:
        text = update.message.text

    chat_id = update.effective_chat.id
    context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    ss = SoupStrainer()
    ss.init()
    if ss.loadAddress(text):
        (article, prediction, probabilities) = make_prediction(ss.extractText)
        print(probabilities)
        print(prediction)
        context.bot.send_message(chat_id=chat_id, text=getPredictionsText(
            prediction, probabilities[0]), reply_to_message_id=update.message.message_id)
    else:
        context.bot.send_message(
            chat_id=chat_id, text='I am sorry. I could not load page data for ' + update.message.text)


def make_prediction(text):
    article = buildRow(text)
    article = article.reshape(1, -1)
    prediction = svc_model.predict(article)
    probabilities = svc_model.predict_proba(article)

    return (article, prediction, probabilities)


def predict_text(update, context, words=None):
    if words is None:
        words = update.message.text.split()
    num_words = len(words)
    chat_id = update.effective_chat.id

    if num_words < 500:
        context.bot.send_message(chat_id=chat_id, text=str(num_words) + ' counted. I need text containing at least 500 words',
                                 reply_to_message_id=update.message.message_id)
        print(num_words)
        return

    ss = SoupStrainer()
    ss.init()
    ss.extractText = ''
    ss.getStemmedWords(words)
    (article, prediction, probabilities) = make_prediction(ss.extractText)
    print(probabilities)
    context.bot.send_message(chat_id=chat_id, text=getPredictionsText(
        prediction, probabilities[0]), reply_to_message_id=update.message.message_id)


def getPredictionsText(prediction, probabilities):
    if prediction == 1:
        return 'This article is false.'
    elif prediction == 2:
        return 'Although this article contains certain elements of truth. It is mostly false.'
    elif prediction == 3:
        return 'While mostly true, this article contains a few mischarecterizations'
    else:
        return 'This article is true.'


def group(update, context):
    url_match = re.compile('.*http.*')
    text = update.message.text

    if text is None:
        return

    if url_match.match(text):
        predict_url(update, context, text)
        return

    words = text.split()
    num_words = len(words)

    if num_words >= 500:
        predict_text(update, context, words)


def unknown(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm sorry. I do not understand that.")


# Creating the command/message handlers
start_handler = CommandHandler('start', start)
group_handler = MessageHandler(Filters.group, group)
url_handler = MessageHandler(url_filter, predict_url)
text_handler = MessageHandler(Filters.text, predict_text)
unknown_handler = MessageHandler(Filters.all, unknown)

# Adding the handlers to the dispatcher
dispatcher.add_handler(start_handler)
dispatcher.add_handler(group_handler)
dispatcher.add_handler(url_handler)
dispatcher.add_handler(text_handler)
dispatcher.add_handler(unknown_handler)


# Starting the bot
updater.start_webhook(listen=os.environ.get("BOT_HOST"), port=os.environ.get("BOT_PORT"), url_path=os.environ.get("WEBHOOK_PATH"))
updater.bot.set_webhook(url="{0}{1}".format(os.environ.get("BOT_URL"), os.environ.get("WEBHOOK_PATH")))

updater.idle()
