from data_functions import *
from utilities import *
import Constants as C 
from telegram import InlineKeyboardMarkup
import pandas as pd
import os

img_url = f"{C.DATA_URL}/cat-analyst/data/img"
prepdata_url = f"{C.DATA_URL}/cat-analyst/data/prep_data"
input_url = f"{C.DATA_URL}/cat-analyst/data/inputs"
button_text = 122121218821827178

BF = None

async def start(update, context): 
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
    
async def get_document(update, context):
    
    ID = str(update.effective_chat.id)
        
    await (await context.bot.get_file(update.message.document)).download(f'{input_url}/D{ID}.csv')
    
    data = read_data(ID)
    data_vars = get_data_variables(data, ID)
    
    text = f"ИНФОРМАЦИЯ О ДАТАСЕТЕ:\nКоличество объектов в данных: {data_vars['n_samples']},\nКоличество признаков: {data_vars['n_features']}\nКоличество качественных переменных: {data_vars['n_cat_features']}\nКоличество числовых переменных: {data_vars['n_num_features']}" + "\n\nКачественные переменные: \n" + data_vars["cat_features"] + "\n\nКоличественные переменные: \n" + data_vars["num_features"] + "\n\nКоличество пропущенных значений: " + str(data_vars["n_nan"])
    await context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = text
    )

    buttons = create_buttons(('Нет, не нужна', 'No122121218821827178'), ('Да, нужна', 'Yes122121218821827178'))

    await context.bot.send_message(chat_id = update.effective_chat.id, text = 'Нужна ли предобработка данных? (работа с выбросами и пропущенными значениями) \n\nПредобработка данных рекомендуется для использования статистических методов и алгоритмов машинного обучения. \nПредобработка данных необязательна, если Вам нужна только описательная статистика данных.', 
    reply_markup = InlineKeyboardMarkup(buttons))
    
async def unknown(update, context):
    text = 'Прости, я не знаю такую команду :(.\nНапиши /help, чтобы я смог помочь тебе!'
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text
    )

async def get_buttons_callbacks(update, context):
    query = update.callback_query
    q_data = query.data
    await query.answer()
    if 'No122121218821827178' in q_data: 
        await context.bot.send_message(chat_id = update.effective_chat.id, text = 'А ты не из робких!')
        
        ID = update.effective_chat.id
        pd.read_csv(f"{input_url}/D{ID}.csv", index_col=0).to_csv(f"{prepdata_url}/D{ID}.csv")

        buttons = create_buttons([('Описательная статистика (графики)', 'desc122121218821827178')])
        await context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = "Окей, что будем делать дальше?",
            reply_markup = InlineKeyboardMarkup(buttons))
            
    elif 'Yes122121218821827178' in q_data: 
        await context.bot.send_message(chat_id = update.effective_chat.id, text = 'Понял, сейчас обработаю!')
        
        ID = str(update.effective_chat.id)
            
        data = pd.read_csv(f"{input_url}/D{ID}.csv", index_col=0)
        data, na_drops, many_drops, r_before, r_after, cat_features, num_features, bin_features = auto_preproccecing(data, ID)
        
        global BF
        BF = pd.read_csv(f"{prepdata_url}/binf{ID}.csv", index_col=0).index.values
        
        await context.bot.send_message(chat_id = update.effective_chat.id, text = f'Данные обработаны. Теперь анализ пойдёт как по маслу!\n\nВсе качественные признаки: {", ".join(cat_features)}\nВ том числе бинарные (2 уникальных значений): {", ".join(bin_features)}\n\nКоличественные признаки: {", ".join(num_features)}')
        
        text = f"Удалённые признаки по критерию потерянных значений (>70%):\n{', '.join(na_drops)}\n\nУдалённые признаки по критерию уникальных качественных значений на тысячу объектов (>30/1000):\n{', '.join(many_drops)}\n\nСколько осталось значений после удаления выбросов:\n{r_after} из {r_before}"
        await context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = text
        )
        
        buttons = create_buttons(('Описательная статистика (графики)', 'desc122121218821827178'),
                                  ('Корреляция (связь количественных признаков)', 'corr122121218821827178'),
                                  ('Сравнение двух выборок (t-test/Манна-Уитни)', 'two122121218821827178'),
                                  ('Машинное обучение (классификация/корреляция)', 'ml122121218821827178'),
                                  ('Стоп! Скачай обработанные данные!', 'dow122121218821827178'))
        
        await context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = "Данные предобработаны, что будем делать дальше?",
            reply_markup = InlineKeyboardMarkup(buttons))
        
    elif 'dow122121218821827178' in q_data:
        await context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = "Хорошо, надеюсь моя обработка поможет тебе получить качественные инсайты!")
        await send_file(update, context, f"{prepdata_url}/D{update.effective_chat.id}.csv", "prep_data.csv")
        await send_file(update, context, f"{prepdata_url}/skew_df{update.effective_chat.id}.csv", "skew_data.csv")
        
    #tho-sets block     
    elif 'two122121218821827178' in q_data:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Для того, чтобы провести анализ двух выборок нужен как минимум один бинарный (два уникальных значения) качественный признак!")
        data = pd.read_csv(f"{prepdata_url}/D{update.effective_chat.id}.csv", index_col=0)
        binary_features = get_binary_feature(data)
        if binary_features:
            buttons = create_buttons(('Авто', 'twovauto122121218821827178'),
                                    ('t-test', 'twovt122121218821827178'),
                                    ('Манна-Уитни', 'twovman122121218821827178'))
            await context.bot.send_message(
                chat_id = update.effective_chat.id,
                text = "Да, у тебя в данных есть бинарные признаки! Теперь нужно выбрать метод (Авто, если не знаешь)",
                reply_markup = InlineKeyboardMarkup(buttons))
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="У тебя нет бинарных признаков, так что провести анализ двух выборок не выйдет :(")
    
    elif 'corr122121218821827178' in q_data:
        buttons = create_buttons(('Авто', 'corrauto122121218821827178'),
                                  ('Пирсон (параметрический тест)', 'pirson122121218821827178'),
                                  ('Спирмен (непараметрический тест)', 'sperman122121218821827178'))
        await context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = "Корреляция значит. Ага. Готовься получить корреляционную матрицу!",
            reply_markup = InlineKeyboardMarkup(buttons))
        
    elif 'corrauto122121218821827178' in q_data:
        ID = str(update.effective_chat.id)
        data = pd.read_csv(f"{prepdata_url}/D{ID}.csv", index_col=0)
        
        get_corr_pearson(data, ID)
        await send_corr_files(update, context, f"{prepdata_url}/corr{ID}.csv", f"{prepdata_url}/p_val{ID}.csv", f"{img_url}/snscorr{ID}.png")
        await remove_corr_outputs(f"{prepdata_url}/corr{ID}.csv", f"{prepdata_url}/p_val{ID}.csv", f"{img_url}/snscorr{ID}.png") 
            
    elif 'sperman122121218821827178' in q_data:
        ID = str(update.effective_chat.id)
        data = pd.read_csv(f"{prepdata_url}/D{ID}.csv", index_col=0)
        
        get_corr_spearman(data, ID)
        await send_corr_files(update, context, f"{prepdata_url}/corr{ID}.csv", f"{prepdata_url}/p_val{ID}.csv", f"{img_url}/snscorr{ID}.png")
        await remove_corr_outputs(f"{prepdata_url}/corr{ID}.csv", f"{prepdata_url}/p_val{ID}.csv", f"{img_url}/snscorr{ID}.png")
            
    elif 'pirson122121218821827178' in q_data:
        ID = str(update.effective_chat.id)
        data = pd.read_csv(f"{prepdata_url}/D{ID}.csv", index_col=0)
        
        get_corr_pearson(data, ID)
        await send_corr_files(update, context, f"{prepdata_url}/corr{ID}.csv", f"{prepdata_url}/p_val{ID}.csv", f"{img_url}/snscorr{ID}.png") 
        await remove_corr_outputs(f"{prepdata_url}/corr{ID}.csv", f"{prepdata_url}/p_val{ID}.csv", f"{img_url}/snscorr{ID}.png")
    
    elif 'desc122121218821827178' in q_data:
        ID = str(update.effective_chat.id)
        data = pd.read_csv(f"{C.DATA_URL}/cat-analyst/data/inputs/D{ID}.csv", index_col=0)
        
    else:    
        for bf in BF:
            if f"{bf}122121218821827178" in q_data:
                ID = update.effective_chat.id 
                data = pd.read_csv(f"{prepdata_url}/D{ID}.csv", index_col=0)
                
                get_twov(data, ID, bf)
                await send_file(update, context, f"{prepdata_url}/twov{ID}.csv", "t-test_data.csv")
                await remove_corr_outputs(f"{prepdata_url}/twov{ID}.csv")

   
        

    
        
        