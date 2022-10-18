from data_functions import *
import Constants
import pandas as pd

async def start(update, context): 
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text='Привет, я Кот-Аналитик!\nПришли мне csv файл своих данных, и я проанализирую их за тебя.\nЕсли возникнут вопросы, пиши /help'
    )
         
async def echo(update, context):
    text = update.message.text.lower()
    data = Constants.DATA
    if text in ['обработка', 'обработать', 'предобработка', 'предобработать']:
        data = auto_preproccecing(data)
        data_vars = get_data_variables(data)
        
        await context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = str(data_vars)
        )
    
async def get_document(update, context):
    
    with open(f'{Constants.DATA_URL}/cat-analyst/id.txt', 'r') as file:
        ID = int(file.read())
        
    await (await context.bot.get_file(update.message.document)).download(f'{Constants.DATA_URL}/cat-analyst/data/inputs/D{ID}.csv')
    
    data = read_data(ID)
    data_vars = get_data_variables(data)
    
    Constants.ID = ID
    Constants.DATA = data
    Constants.DATA_VARS = data_vars
    
    text = f"DATA INFO:\nnumber of samples: {data_vars['n_samples']},\nnumber of features: {data_vars['n_features']}\nnumber of categorical features: {data_vars['n_cat_features']}\nnumber of numeric features: {data_vars['n_num_features']}" + "\n\nCategorical features: \n" + data_vars["cat_features"] + "\n\nNumeric features: \n" + data_vars["num_features"] + "\n\nn nan values: " + str(data_vars["n_nan"])
    await context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = text
    )
    
    with open(f'{Constants.DATA_URL}/cat-analyst/id.txt', 'w') as file:
        file.write(str(ID+1))

async def unknown(update, context):
    text = 'Прости, я не знаю такую команду :(.\nНапиши /help, чтобы я смог помочь тебе!'
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=str(Constants.DATA_VARS)
    )