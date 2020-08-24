from telegram import ChatAction
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from filters import UrlFilter
from scraper import SoupStrainer
from util import buildRow
import config
import re
import pickle
import os.path as path
import logging
import json

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


def predict_url(update, context, text=None):
    if text is None:
        text = update.message.text

    chat_id = str(update.effective_chat.id)
    context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    ss = SoupStrainer()
    ss.init()
    if ss.loadAddress(text):
        (article, prediction, probabilities) = make_prediction(ss.extractText)
        maximum = max(probabilities[0])

        if maximum == probabilities[0][0]:
            prediction = 1

        if maximum == probabilities[0][1]:
            prediction = 2

        if maximum == probabilities[0][2]:
            prediction = 3

        if maximum == probabilities[0][3]:
            prediction = 4

        ratings_text = getPredictionsText(prediction, probabilities[0])
        save(chat_id, text, ratings_text)

        context.bot.send_message(chat_id=chat_id, text=ratings_text, reply_to_message_id=update.message.message_id)
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
    chat_id = str(update.effective_chat.id)

    if num_words < 500:
        context.bot.send_message(chat_id=chat_id, text=str(num_words) + ' words counted. I need text containing at least 500 words',
                                 reply_to_message_id=update.message.message_id)
        return

    ss = SoupStrainer()
    ss.init()
    ss.extractText = ''
    ss.getStemmedWords(words)
    (article, prediction, probabilities) = make_prediction(ss.extractText)

    maximum = max(probabilities[0])

    if maximum == probabilities[0][0]:
        prediction = 1

    if maximum == probabilities[0][1]:
        prediction = 2

    if maximum == probabilities[0][2]:
        prediction = 3

    if maximum == probabilities[0][3]:
        prediction = 4

    text = getPredictionsText(prediction, probabilities[0])

    save(chat_id, update.message.text, text)

    context.bot.send_message(chat_id=chat_id, text=text, reply_to_message_id=update.message.message_id)


def getPredictionsText(prediction, probabilities):
    if prediction == 1:
        return 'This is false.'
    elif prediction == 2:
        return 'Although this contains certain elements of truth. It is mostly false.'
    elif prediction == 3:
        if (probabilities[2] + probabilities[3]) > 0.8:
            return 'This article is true'
        else:
            return 'While mostly true, this contains a few mischarecterizations and untruths'
    else:
        return 'This is true.'


def save(chat_id, data, rating):
    with open(path.join(config.base_dir, 'ratings.json')) as reader:
        ratings = json.load(reader)

    if chat_id not in ratings:
        ratings[chat_id] = []

    rating = { 'data':data, 'rating':rating }

    if rating in ratings[chat_id]:
        return 
    
    ratings[chat_id].append(rating)

    with open(path.join(config.base_dir, 'ratings.json'), 'w') as writer:
        json.dump(ratings, writer)

    return


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

def history(update, context):
    chat_id = str(update.effective_chat.id)

    with open(path.join(config.base_dir, 'ratings.json')) as reader:
        ratings = json.load(reader)

    if chat_id not in ratings:
        return context.bot.send_message(chat_id=chat_id, text="I haven't done any fact checking for you apparently")

    user_ratings = ratings[chat_id]
    
    for i in range(0, len(user_ratings)):
        rating = user_ratings[i]
        context.bot.send_message(chat_id=chat_id, text=rating['data'])
        context.bot.send_message(chat_id=chat_id, text=rating['rating']) 

def clear(update, context):
    chat_id = str(update.effective_chat.id)

    with open(path.join(config.base_dir, 'ratings.json')) as reader:
        ratings = json.load(reader)

    if chat_id not in ratings:
        return context.bot.send_message(chat_id=chat_id, text='Nothing to clear!')

    del ratings[chat_id]

    with open(path.join(config.base_dir, 'ratings.json'), 'w') as writer:
        json.dump(ratings, writer)

    context.bot.send_message(chat_id=chat_id, text='History cleared successfully!')


def unknown(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm sorry. I do not understand that.")


# Creating the command/message handlers
start_handler = CommandHandler('start', start)
history_handler = CommandHandler('history', history)
clear_handler = CommandHandler('clear', clear)
group_handler = MessageHandler(Filters.group, group)
url_handler = MessageHandler(url_filter, predict_url)
text_handler = MessageHandler(Filters.text, predict_text)
unknown_handler = MessageHandler(Filters.all, unknown)

# Adding the handlers to the dispatcher
dispatcher.add_handler(start_handler)
dispatcher.add_handler(history_handler)
dispatcher.add_handler(clear_handler)
dispatcher.add_handler(group_handler)
dispatcher.add_handler(url_handler)
dispatcher.add_handler(text_handler)
dispatcher.add_handler(unknown_handler)

# Starting the bot
updater.start_polling()
updater.idle()
