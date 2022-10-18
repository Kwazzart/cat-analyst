#imports
#from asyncore import dispatcher // непонятный импот
import Constants
import Requests as R
import logging
import asyncio

from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler
from telegram import *
from telegram.ext import *

#logs activate
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   level=logging.INFO
                )

if __name__ == "__main__":
    
    application = ApplicationBuilder().token(Constants.TOKEN).read_timeout(30).write_timeout(30).build()
    
    application.add_handler(CommandHandler('start', R.start))
    application.add_handler(MessageHandler(filters.Document.ALL, R.get_document))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), R.echo))
    application.add_handler(MessageHandler(filters.COMMAND, R.unknown))
    application.add_handler(CallbackQueryHandler(R.buttons_helper))
    application.run_polling()

