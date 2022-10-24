from telegram import InlineKeyboardButton
import os


def create_buttons(*args):
    buttons = []
    for text, cd in args:
        buttons.append([InlineKeyboardButton(text, callback_data = cd)])
    return buttons

async def remove_outputs(*urls):
    for url in urls:
        os.remove(url)

async def send_file(update, context, url, filename):
    with open(url, "rb") as file:
        await context.bot.send_document(chat_id = update.effective_chat.id, document=file, filename=filename)

async def send_img(update, context, url, filename):
    with open(url, "rb") as file:
        await context.bot.send_photo(chat_id = update.effective_chat.id, photo=file, filename=filename)

async def send_desc_files(update, context, url): 
   await send_img(update, context, url, "descriptive.png")
        
async def send_corr_files(update, context, url1, url2, url_img):
    await send_file(update, context, url1, "corrmatrix.csv")
    await send_file(update, context, url2, "p_values.csv")
    await send_img(update, context, url_img, "corrmatrix2.png")
        
def get_binary_feature(data):
    bin_arr = []
    for col in data.columns:
        if data[col].nunique() == 2:
            bin_arr.append(col)
    return bin_arr