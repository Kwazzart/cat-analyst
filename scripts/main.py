#imports
#from asyncore import dispatcher // непонятный импот
import Constants as C
import Requests as R
import logging

async def start(update, context): 
    '''  '''
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text='Привет, я Кот-Аналитик!\nПришли мне csv файл своих данных, и я проанализирую их за тебя! Очень удобно!\n\nТОЛЬКО УЧТИ! Тебе следует убедиться, что качественные признаки в твоих данных (например: пол, цвет, страна и т.п.) имеют текстовые значения, а не числовые!\n\nЕсли возникнут вопросы, пиши /help'
    )
    
async def instraction(update, context):
    await context.bot.send_message(   
        chat_id = update.effective_chat.id,
        text = "Для работы со мной тебе следует отправить файл формата .csv с твоими данными. ОЧЕНЬ ВАЖНО - убедись, что значения качественных признаков введены текстом, а не числом (Пол 1,0 должны быть мужчина, женщина, например). Сделаем нашу совместную работу проще!"
    )
    
async def help(update, context):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="Вот список команд, которые я знаю:\n/start - Приветственная команда с требованием к данным\n/instraction - инструкция по работе со мной\n"
        )
    
async def echo(update, context):
    text = update.message.text.lower()
    if "люблю" in text:
         await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text = "Я тебя люблю :3"
        )   
         
async def unknown(update, context):
    text = 'Прости, я не знаю такую команду :(.\nНапиши /help, чтобы я смог помочь тебе!'
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text
    )

from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler
from telegram import *
from telegram.ext import *

#logs activate
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   level=logging.INFO
                )

if __name__ == "__main__":
    
    application = ApplicationBuilder().token(C.TOKEN).read_timeout(30).write_timeout(30).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help))
    application.add_handler(CommandHandler('instraction', instraction))
    application.add_handler(MessageHandler(filters.Document.ALL, R.get_document))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))
    application.add_handler(CallbackQueryHandler(R.get_buttons_callbacks))
    
    application.run_polling()

