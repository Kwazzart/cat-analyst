import asyncio
import Constants
from read_data import *

async def start(update, context): 
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text='Привет, я Кот-Аналитик!\nПришли мне csv файл своих данных, и я проанализирую их за тебя.\nЕсли возникнут вопросы, пиши /help'
    )
 
async def caps(update, context):
    if context.args:
        text_caps = ' '.join(context.args).upper()
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=text_caps
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text='No command argument\nsend: /caps argument'
        )
         
async def echo(update, context):
    text = update.message.text
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=text
    )
    
async def get_document(update, context):
    
    with open('D:/pet-projects/cat-analyst/id.txt', 'r') as file:
        ID = int(file.read())
        
    await (await context.bot.get_file(update.message.document)).download(f'./cat-analyst/data/inputs/D{ID}.csv')
    
    print(read_data())
    
    with open('D:/pet-projects/cat-analyst/id.txt', 'w') as file:
        file.write(str(ID+1))

async def unknown(update, context):
    text = 'Прости, я не знаю такую команду :(.\nНапиши /help, чтобы я смог помочь тебе!'
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text
    )