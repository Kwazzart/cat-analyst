from data_functions import *
from utilities import *
import Constants 
from telegram import InlineKeyboardMarkup
import pandas as pd

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
        
    await (await context.bot.get_file(update.message.document)).download(f'{Constants.DATA_URL}/cat-analyst/data/inputs/D{ID}.csv')
    
    data = read_data(ID)
    data_vars = get_data_variables(data, ID)
    
    text = f"ИНФОРМАЦИЯ О ДАТАСЕТЕ:\nКоличество объектов в данных: {data_vars['n_samples']},\nКоличество признаков: {data_vars['n_features']}\nКоличество качественных переменных: {data_vars['n_cat_features']}\nКоличество числовых переменных: {data_vars['n_num_features']}" + "\n\nКачественные переменные: \n" + data_vars["cat_features"] + "\n\Количественные переменные: \n" + data_vars["num_features"] + "\n\nКоличество пропущенных значений: " + str(data_vars["n_nan"])
    await context.bot.send_message(
        chat_id = update.effective_chat.id,
        text = text
    )

    buttons = create_buttons([('Нет, не нужна', 'No122121218821827178'), ('Да, нужна', 'Yes122121218821827178')])

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
        pd.read_csv(f"{Constants.DATA_URL}/cat-analyst/data/inputs/D{ID}.csv", index_col=0).to_csv(f"{Constants.DATA_URL}/cat-analyst/data/prep_data/D{ID}.csv")
            
    elif 'Yes122121218821827178' in q_data: 
        await context.bot.send_message(chat_id = update.effective_chat.id, text = 'Понял, сейчас обработаю!')
        
        ID = str(update.effective_chat.id)
            
        data = pd.read_csv(f"{Constants.DATA_URL}/cat-analyst/data/inputs/D{ID}.csv", index_col=0)
        data, na_drops, many_drops, r_before, r_after = auto_preproccecing(data, ID)
        
        await context.bot.send_message(chat_id = update.effective_chat.id, text = 'Данные обработаны. Теперь анализ пойдёт как по маслу!')
        
        text = f"Удалённые признаки по критерию потерянных значений (>70%):\n{', '.join(na_drops)}\n\nУдалённые признаки по критерию уникальных качественных значений на тысячу объектов (>30/1000):\n{', '.join(many_drops)}\n\nСколько осталось значений после удаления выбросов:\n{r_after} из {r_before}"
        await context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = text
        )
        
        buttons = create_buttons([('Описательная статистика (графики)', 'desc122121218821827178'),
                                  ('Корреляция (связь количественных признаков)', 'corr122121218821827178'),
                                  ('Сравнение двух выборок (t-test/Манна-Уитни)', 'two122121218821827178'),
                                  ('Машинное обучение (классификация/корреляция)', 'ml122121218821827178'),
                                  ('Всё! Скачай обработанные данные!', 'dow122121218821827178')])
        
        await context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = "Данные предобработаны, что будем делать дальше?",
            reply_markup = InlineKeyboardMarkup(buttons))
    
    elif 'corr122121218821827178' in q_data:
        buttons = create_buttons([('Авто', 'corrauto122121218821827178'),
                                  ('Пирсон (параметрический тест)', 'pirson122121218821827178'),
                                  ('Спирмен (непараметрический тест)', 'sperman122121218821827178')])
        await context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = "Корреляция значит. Ага. Готовься получить корреляционную матрицу!",
            reply_markup = InlineKeyboardMarkup(buttons))
        
    elif 'corrauto122121218821827178' in q_data:
        ID = str(update.effective_chat.id)
        data = pd.read_csv(f"{Constants.DATA_URL}/cat-analyst/") 
        
        