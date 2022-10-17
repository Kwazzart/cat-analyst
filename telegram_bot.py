#importing
import logging
import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters

#main variables
TOKEN = '5554474456:AAH59s3E6GIngfY6KJKIqsUue8ON-JO5qa8'
updater = Updater(token = TOKEN)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   level=logging.INFO)

#functions
def start(update, context): 
    context.bot.send_message(chat_id=update.effective_chat.id, 
                             text="иди нах)")
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)


def echo(update, context):
    text = 'ладно все заткнись'
    context.bot.send_message(chat_id=update.effective_chat.id, 
                             text=text)
echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)

def caps(update, context):
    if context.args:
        text_caps = ' '.join(context.args).upper()
        context.bot.send_message(chat_id=update.effective_chat.id, 
                                text=text_caps)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, 
                                text='No command argument')
        context.bot.send_message(chat_id=update.effective_chat.id, 
                                text='send: /caps argument')

#create handler
caps_handler = CommandHandler('caps', caps)
dispatcher.add_handler(caps_handler)

#main func
updater.start_polling()

