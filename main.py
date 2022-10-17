#imports
from asyncore import dispatcher
import Constants
import logging

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

#logs activate
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   level=logging.INFO)

#functions
def start(update, context): 
    context.bot.send_message(chat_id=update.effective_chat.id, 
                             text="иди нах)")
    
def echo(update, context):
    text = 'ладно все заткнись'
    context.bot.send_message(chat_id=update.effective_chat.id, 
                             text=text)

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

if __name__ == "__main__":
    
    updater = Updater(Constants.TOKEN)
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('caps', caps))
    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), echo))

    updater.start_polling()

