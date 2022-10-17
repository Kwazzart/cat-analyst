#imports
#from asyncore import dispatcher // непонятный импот
import Constants
import Requests as R
import logging

from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler

#logs activate
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   level=logging.INFO
                )

if __name__ == "__main__":
    
    application = ApplicationBuilder().token(Constants.TOKEN).build()
    
    application.add_handler(CommandHandler('start', R.start))
    application.add_handler(CommandHandler('caps', R.caps))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), R.echo))

    application.run_polling()

