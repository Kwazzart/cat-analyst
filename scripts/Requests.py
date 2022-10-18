from data_functions import *
import Constants
from telegram.ext import * 
from telegram import * 

async def start(update, context): 
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text='Привет, я Кот-Аналитик!\nПришли мне csv файл своих данных, и я проанализирую их за тебя.\nЕсли возникнут вопросы, пиши /help'
    )
         
async def echo(update, context):
    text = update.message.text
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=text
    )
    
async def get_document(update, context):
    
    with open(f'{Constants.DATA_URL}/cat-analyst/id.txt', 'r') as file:
        ID = int(file.read())
        
    await (await context.bot.get_file(update.message.document)).download(f'{Constants.DATA_URL}/cat-analyst/data/inputs/D{ID}.csv')
    
    data = read_data(ID)
    data_vars = get_data_variables(data)
    
    text = f"DATA INFO:\nnumber of samples: {data_vars['n_samples']},\nnumber of features: {data_vars['n_features']}\nnumber of categorical features: {data_vars['n_cat_features']}\nnumber of numeric features: {data_vars['n_num_features']}" + "\nCategorical features: " + data_vars["cat_features"] + "\nNumeric features: " + data_vars["num_features"]
    await context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = text
    )

    buttons = [[InlineKeyboardButton('Нет, не нужна', callback_data = 'No122121218821827178' )],
    [InlineKeyboardButton('Да, нужна ', callback_data = 'Yes122121218821827178' )]]
    await context.bot.send_message(chat_id = update.effective_chat.id, text = 'Нужна ли предобработка данных? (работа с выбросами и пропущенными значениями) \nПредобработка данных рекомендуется для использования статистических методов и методов машинного обучения. \nПредобработка данных не рекомендуется, если Вам нужна только описательная статистика данных.', 
    reply_markup = InlineKeyboardMarkup(buttons))
    
    with open(f'{Constants.DATA_URL}/cat-analyst/id.txt', 'w') as file:
        file.write(str(ID+1))

async def unknown(update, context):
    text = 'Прости, я не знаю такую команду :(.\nНапиши /help, чтобы я смог помочь тебе!'
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text
    )

async def buttons_helper(update, context):
    query = update.callback_query
    q_data = query.data
    await query.answer()
    if 'No122121218821827178' in q_data: 
        await context.bot.send_message(chat_id = update.effective_chat.id, text = 'Понял, не нужно')
    elif 'Yes122121218821827178' in q_data: 
        await context.bot.send_message(chat_id = update.effective_chat.id, text = 'Понял, нужно')