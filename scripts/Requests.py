from data_functions import *
from utilities import *
import Constants as C 
from telegram import InlineKeyboardMarkup
import pandas as pd
import os
import ast

img_url = f"{C.DATA_URL}/cat-analyst/data/img"
prepdata_url = f"{C.DATA_URL}/cat-analyst/data/prep_data"
input_url = f"{C.DATA_URL}/cat-analyst/data/inputs"
button_text = 122121218821827178

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
    
async def get_document(update, context):
    ''' Получает данные от пользователя и сохраняет на диск сырые данные и основные "переменные" данных '''
    ID = str(update.effective_chat.id)

    await (await context.bot.get_file(update.message.document)).download(f'{input_url}/D{ID}.csv')

    data = read_data(ID)
    data_vars = get_data_variables(data, ID)

    text = f"ИНФОРМАЦИЯ О ДАТАСЕТЕ:\nКоличество объектов в данных: {data_vars['n_samples']},\nКоличество признаков: {data_vars['n_features']}\nКоличество качественных переменных: {data_vars['n_cat_features']}\nКоличество числовых переменных: {data_vars['n_num_features']}" + "\n\nКачественные переменные: \n" + str(data_vars["cat_features"]) + "\n\nВ том числе бинарные признаки: \n" + str(data_vars['bin_features']) + "\n\nКоличественные переменные: \n" + str(data_vars["num_features"]) + "\n\nКоличество пропущенных значений: " + str(data_vars["n_nan"])
    await context.bot.send_message(
    chat_id = update.effective_chat.id,
    text = text
    )

    buttons = create_buttons(('Нет, не нужна', f'No{button_text}'), ('Да, нужна', f'Yes{button_text}'))

    await context.bot.send_message(chat_id = update.effective_chat.id, text = 'Нужна ли предобработка данных? (работа с выбросами и пропущенными значениями) \n\nПредобработка данных рекомендуется для использования статистических методов и алгоритмов машинного обучения. \nПредобработка данных необязательна, если Вам нужна только описательная статистика данных.', 
    reply_markup = InlineKeyboardMarkup(buttons))

async def get_buttons_callbacks(update, context):
    ''' Главная функция, которая получает ответ от кнопок и реагирует на них '''
    query = update.callback_query
    q_data = query.data
    await query.answer()
    if f'No{button_text}' in q_data: 
        await context.bot.send_message(chat_id = update.effective_chat.id, text = 'А ты не из робких!')
        
        ID = update.effective_chat.id
        pd.read_csv(f"{input_url}/D{ID}.csv", index_col=0).to_csv(f"{prepdata_url}/D{ID}.csv")

        buttons = create_buttons(('Описательная статистика (графики)', f'desc{button_text}'))
        await context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = "Окей, что будем делать дальше?",
            reply_markup = InlineKeyboardMarkup(buttons))
            
    elif f'Yes{button_text}' in q_data: 
        await context.bot.send_message(chat_id = update.effective_chat.id, text = 'Понял, сейчас обработаю!')
        
        ID = str(update.effective_chat.id)
            
        data = pd.read_csv(f"{input_url}/D{ID}.csv")
        with open(f"{prepdata_url}/data_vars{ID}.txt", "r") as file:
            data_vars = ast.literal_eval(file.read())
        data, na_drops, many_drops, r_before, r_after, cat_features, num_features, bin_features = auto_preproccecing(data, data_vars, ID)
        get_data_variables(data, ID)
        
        await context.bot.send_message(chat_id = update.effective_chat.id, text = f'Данные обработаны. Теперь анализ пойдёт как по маслу!\n\nВсе качественные признаки: {", ".join(cat_features)}\n\nВ том числе бинарные (2 уникальных значений): {", ".join(bin_features)}\n\nКоличественные признаки: {", ".join(num_features)}')
        
        text = f"Удалённые признаки по критерию потерянных значений (>70%):\n{', '.join(na_drops)}\n\nУдалённые признаки по критерию уникальных качественных значений на тысячу объектов (>30/1000):\n{', '.join(many_drops)}\n\nСколько осталось значений после удаления выбросов:\n{r_after} из {r_before}"
        await context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = text
        )
        
        buttons = create_buttons(('Описательная статистика (графики)', f'desc{button_text}'),
                                  ('Корреляция (связь количественных признаков)', f'corr{button_text}'),
                                  ('Сравнение двух выборок (t-test/Манна-Уитни)', f'two{button_text}'),
                                  ('Машинное обучение (классификация/корреляция)', f'ml{button_text}'),
                                  ('Стоп! Скачай обработанные данные!', f'dow{button_text}'))
        
        await context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = "Данные предобработаны, что будем делать дальше?",
            reply_markup = InlineKeyboardMarkup(buttons))
        
    elif f'dow{button_text}' in q_data:
        await context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = "Хорошо, надеюсь моя обработка поможет тебе получить качественные инсайты!")
        await send_file(update, context, f"{prepdata_url}/D{update.effective_chat.id}.csv", "prep_data.csv")
        await send_file(update, context, f"{prepdata_url}/skew_df{update.effective_chat.id}.csv", "skew_data.csv")
        
    #two-sets block     
    elif f'two{button_text}' in q_data:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Для того, чтобы провести анализ двух выборок нужен как минимум один бинарный (два уникальных значения) качественный признак!")
        ID = update.effective_chat.id
        with open(f"{prepdata_url}/data_vars{ID}.txt", "r") as file:
            data_vars = ast.literal_eval(file.read())
        binary_features = data_vars["bin_features"]
        if binary_features:
            buttons = create_buttons(('Авто', f'twovauto{button_text}'),
                                    ('t-test', f'twovt{button_text}'),
                                    ('Манна-Уитни', f'twovman{button_text}'))
            await context.bot.send_message(
                chat_id = update.effective_chat.id,
                text = "Да, у тебя в данных есть бинарные признаки! Теперь нужно выбрать метод (Авто, если не знаешь)",
                reply_markup = InlineKeyboardMarkup(buttons))
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="У тебя нет бинарных признаков, так что провести анализ двух выборок не выйдет :(")
    
    elif f'twovauto{button_text}' in q_data:
        ID = update.effective_chat.id
        with open(f"{prepdata_url}/data_vars{ID}.txt", "r") as file:
            data_vars = ast.literal_eval(file.read())
        data_vars["two_choice"] = "auto"
        with open(f"{prepdata_url}/data_vars{ID}.txt", "w") as file:
            file.write(str(data_vars))
                
        binary_features = data_vars["bin_features"]
        binary_features = [(bf, f"{bf}{button_text}") for bf in binary_features]
        buttons = create_buttons(*binary_features)
        await context.bot.send_message(
                chat_id = update.effective_chat.id,
                text = "Выбери качественную бинарную фичу для сравнения!",
                reply_markup = InlineKeyboardMarkup(buttons))
    
    elif f'twovt{button_text}' in q_data:
        ID = update.effective_chat.id
        with open(f"{prepdata_url}/data_vars{ID}.txt", "r") as file:
            data_vars = ast.literal_eval(file.read())
        data_vars["two_choice"] = "t"
        with open(f"{prepdata_url}/data_vars{ID}.txt", "w") as file:
            file.write(str(data_vars))
            
        binary_features = data_vars["bin_features"]
        binary_features = [(bf, f"{bf}{button_text}") for bf in binary_features]
        buttons = create_buttons(*binary_features)
        await context.bot.send_message(
                chat_id = update.effective_chat.id,
                text = "Выбери качественную бинарную фичу для сравнения.",
                reply_markup = InlineKeyboardMarkup(buttons))
    
    elif f'twovman{button_text}' in q_data:
        ID = update.effective_chat.id
        with open(f"{prepdata_url}/data_vars{ID}.txt", "r") as file:
            data_vars = ast.literal_eval(file.read())
        data_vars["two_choice"] = "m"
        with open(f"{prepdata_url}/data_vars{ID}.txt", "w") as file:
            file.write(str(data_vars))
            
        binary_features = data_vars["bin_features"]
        binary_features = [(bf, f"{bf}{button_text}") for bf in binary_features]
        buttons = create_buttons(*binary_features)
        await context.bot.send_message(
                chat_id = update.effective_chat.id,
                text = "Выбери качественную бинарную фичу для сравнения!",
                reply_markup = InlineKeyboardMarkup(buttons))
    
    elif f'corr{button_text}' in q_data:
        buttons = create_buttons(('Авто', f'corrauto{button_text}'),
                                  ('Пирсон (параметрический тест)', f'pirson{button_text}'),
                                  ('Спирмен (непараметрический тест)', f'sperman{button_text}'))
        await context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = "Корреляция значит. Ага. Готовься получить корреляционную матрицу!",
            reply_markup = InlineKeyboardMarkup(buttons))
        
    elif f'corrauto{button_text}' in q_data:
        ID = str(update.effective_chat.id)
        data = pd.read_csv(f"{prepdata_url}/D{ID}.csv", index_col=0)
        
        with open(f"{prepdata_url}/data_vars{ID}.txt", "r") as file:
            data_vars = ast.literal_eval(file.read())
        
        get_corr_pearson(data, data_vars, ID)
        await send_corr_files(update, context, f"{prepdata_url}/corr{ID}.csv", f"{prepdata_url}/p_val{ID}.csv", f"{img_url}/snscorr{ID}.png")
        await remove_outputs(f"{prepdata_url}/corr{ID}.csv", f"{prepdata_url}/p_val{ID}.csv", f"{img_url}/snscorr{ID}.png") 
            
    elif f'sperman{button_text}' in q_data:
        ID = update.effective_chat.id
        data = pd.read_csv(f"{prepdata_url}/D{ID}.csv", index_col=0)
        
        with open(f"{prepdata_url}/data_vars{ID}.txt", "r") as file:
            data_vars = ast.literal_eval(file.read())
        
        get_corr_spearman(data, data_vars, ID)
        await send_corr_files(update, context, f"{prepdata_url}/corr{ID}.csv", f"{prepdata_url}/p_val{ID}.csv", f"{img_url}/snscorr{ID}.png")
        await remove_outputs(f"{prepdata_url}/corr{ID}.csv", f"{prepdata_url}/p_val{ID}.csv", f"{img_url}/snscorr{ID}.png")
            
    elif f'pirson{button_text}' in q_data:
        ID = update.effective_chat.id
        data = pd.read_csv(f"{prepdata_url}/D{ID}.csv", index_col=0)
        
        with open(f"{prepdata_url}/data_vars{ID}.txt", "r") as file:
            data_vars = ast.literal_eval(file.read())
        
        get_corr_pearson(data, data_vars, ID)
        await send_corr_files(update, context, f"{prepdata_url}/corr{ID}.csv", f"{prepdata_url}/p_val{ID}.csv", f"{img_url}/snscorr{ID}.png") 
        await remove_outputs(f"{prepdata_url}/corr{ID}.csv", f"{prepdata_url}/p_val{ID}.csv", f"{img_url}/snscorr{ID}.png")
    
    elif f'desc{button_text}' in q_data:
        ID = update.effective_chat.id
        data = pd.read_csv(f"{prepdata_url}/D{ID}.csv", index_col=0)
        descriptive(data, ID)
        for i in range(1, 10, 1):
            if os.path.isfile(f"{img_url}/descriptive{i}_{ID}.png"): 
                await send_img(update, context, f"{img_url}/descriptive{i}_{ID}.png")
                await remove_outputs(f"{img_url}/descriptive{i}_{ID}.png")
                
    elif f'ml{button_text}' in q_data:
        ID = update.effective_chat.id
        buttons = create_buttons(('Регрессия', f'reg{button_text}'),
                                  ('Классификация', f'clf{button_text}'))
        await context.bot.send_message(chat_id=ID, 
                                       text="Выбери тип решаемой задачи:",
                                       reply_markup = InlineKeyboardMarkup(buttons))
        
    elif f'reg{button_text}' in q_data:
        ID = update.effective_chat.id
        buttons = create_buttons(('Параметрические методы регрессии', f'regparam{button_text}'),
                                  ('Непараметрические методы регрессии', f'regnparam{button_text}')) 
        await context.bot.send_message(chat_id=ID, 
                                       text="Каким типом методов будем пользоваться для регрессии:",
                                       reply_markup = InlineKeyboardMarkup(buttons))
    
    elif f'clf{button_text}' in q_data:
        ID = update.effective_chat.id
        buttons = create_buttons(('Параметрические методы классификации', f'clfparam{button_text}'),
                                  ('Непараметрические методы классификации', f'clfnparam{button_text}'))
        await context.bot.send_message(chat_id=ID, 
                                       text="Каким типом методо будем пользоваться для классификации:",
                                       reply_markup = InlineKeyboardMarkup(buttons))
    
    elif f'regparam{button_text}' in q_data:
        ID = update.effective_chat.id
        buttons = create_buttons(('Линейная регрессия', f'lin{button_text}'))
        await context.bot.send_message(chat_id = ID,
                                       text = "Выбери один из параметрических методов регрессии",
                                       reply_markup = InlineKeyboardMarkup(buttons))
        
    elif f'regnparam{button_text}' in q_data:
        ID = update.effective_chat.id
        buttons = create_buttons(('Решающее дерево', f'dtree_r{button_text}'))
        await context.bot.send_message(chat_id = ID,
                                       text = "Выбери один из непараметрических методов регрессии",
                                       reply_markup = InlineKeyboardMarkup(buttons))
        
    elif f'clfparam{button_text}' in q_data:
        ID = update.effective_chat.id
        buttons = create_buttons(('Логистическая регрессия', f'log{button_text}'))
        await context.bot.send_message(chat_id = ID,
                                       text = "Выбери один из параметрических методов классификации",
                                       reply_markup = InlineKeyboardMarkup(buttons))
        
    elif f'clfnparam{button_text}' in q_data:
        ID = update.effective_chat.id
        buttons = create_buttons(('Решающее дерево', f'dtree_c{button_text}'))
        await context.bot.send_message(chat_id = ID,
                                       text = "Выбери один из непараметрических методов классификации",
                                       reply_markup = InlineKeyboardMarkup(buttons))
        
    elif f'lin{button_text}' in q_data:
        ID = update.effective_chat.id
        with open(f"{prepdata_url}/data_vars{ID}.txt", "r") as file:
            data_vars = ast.literal_eval(file.read())
            
        num_features = data_vars["num_features"]
        buttons = create_buttons(*[(nf, f'{nf}{button_text}') for nf in num_features])
        await context.bot.send_message(chat_id = ID,
                                       text = "Выбери признак для которого будет произведена регрессия",
                                       reply_markup = InlineKeyboardMarkup(buttons))
        
        data_vars["ml_mode"] = "linreg"  
        with open(f"{prepdata_url}/data_vars{ID}.txt", "w") as file:
            file.write(str(data_vars))
    
    elif f'log{button_text}' in q_data:
        ID = update.effective_chat.id
        with open(f"{prepdata_url}/data_vars{ID}.txt", "r") as file:
            data_vars = ast.literal_eval(file.read())
            
        cat_features = data_vars["cat_features"]
        buttons = create_buttons(*[(nf, f'{nf}{button_text}') for nf in cat_features])
        await context.bot.send_message(chat_id = ID,
                                       text = "Выбери признак для которого будет произведена регрессия",
                                       reply_markup = InlineKeyboardMarkup(buttons))
        
        data_vars["ml_mode"] = "logreg"  
        with open(f"{prepdata_url}/data_vars{ID}.txt", "w") as file:
            file.write(str(data_vars))
            
    elif f'dtree_r{button_text}' in q_data:
        ID = update.effective_chat.id
        with open(f"{prepdata_url}/data_vars{ID}.txt", "r") as file:
            data_vars = ast.literal_eval(file.read())
            
        num_features = data_vars["num_features"]
        buttons = create_buttons(*[(nf, f'{nf}{button_text}') for nf in num_features])
        await context.bot.send_message(chat_id = ID,
                                       text = "Выбери признак для которого будет произведена регрессия",
                                       reply_markup = InlineKeyboardMarkup(buttons))
        
        data_vars["ml_mode"] = "tree"  
        with open(f"{prepdata_url}/data_vars{ID}.txt", "w") as file:
            file.write(str(data_vars))
            
    else:
        ID = update.effective_chat.id
        with open(f"{prepdata_url}/data_vars{ID}.txt", "r") as file:
            data_vars = ast.literal_eval(file.read())
            
        BF = data_vars["bin_features"]
        NF = data_vars["num_features"]
        CF = data_vars["cat_features"]
        
        for nf in NF:
            if f"{nf}{button_text}" in q_data:
                ml_mode = data_vars["ml_mode"]
                ID = update.effective_chat.id 
                data = pd.read_csv(f"{prepdata_url}/D{ID}.csv", index_col=0)
                
                if ml_mode == "linreg":
                    pass
                    #get_linreg(data, ID, nf)
                if ml_mode == "tree":
                    get_tree_regression(data, ID, nf)
                
                await send_file(update, context, f"{prepdata_url}/reg{ID}.csv", "regression.csv")
                await send_img(update, context, f"{img_url}/reg{ID}.png", "regression.png")
                await remove_outputs(f"{prepdata_url}/twov{ID}.csv", f"{img_url}/twov{ID}.png")     
                
        for cf in CF:
            if f"{cf}{button_text}" in q_data:
                ml_mode = data_vars["ml_mode"]
                ID = update.effective_chat.id 
                data = pd.read_csv(f"{prepdata_url}/D{ID}.csv", index_col=0)
                
                if ml_mode == "logreg":
                    pass
                    #get_linreg(data, ID, nf)
                
                await send_file(update, context, f"{prepdata_url}/reg{ID}.csv", "regression.csv")
                await send_img(update, context, f"{img_url}/reg{ID}.png", "regression.png")
                await remove_outputs(f"{prepdata_url}/twov{ID}.csv", f"{img_url}/twov{ID}.png")   
              
        for bf in BF:
            if f"{bf}{button_text}" in q_data:
                choice = data_vars["two_choice"]
                ID = update.effective_chat.id 
                data = pd.read_csv(f"{prepdata_url}/D{ID}.csv", index_col=0)
                
                if choice == "auto":
                    get_twov(data, ID, bf)
                elif choice == "t":
                    get_ttest(data, ID, bf)
                elif choice == "m":
                    get_manna(data, ID, bf)
                    
                await send_file(update, context, f"{prepdata_url}/twov{ID}.csv", "auto_t-test_data.csv")
                await send_img(update, context, f"{img_url}/twov{ID}.png", "auto_t-test_data.png")
                await remove_outputs(f"{prepdata_url}/twov{ID}.csv", f"{img_url}/twov{ID}.png")
            
               

   
        

    
        
        