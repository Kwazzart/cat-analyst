from telegram import InlineKeyboardButton
import os


def create_buttons(arr):
    buttons = []
    for text, cd in arr:
        buttons.append([InlineKeyboardButton(text, callback_data = cd)])
    return buttons

async def remove_corr_outputs(*urls):
    for url in urls:
        os.remove(url)

async def send_file(update, context, url, filename):
    with open(url, "rb") as file:
        await context.bot.send_document(chat_id = update.effective_chat.id, document=file, filename=filename)
        
async def send_corr_files(update, context, url1, url2, url_img):
    await send_file(update, context, url1, "corrmatrix.csv")
    await send_file(update, context, url2, "p_values.csv")
    await send_file(update, context, url_img, "corrmatrix_img.png")
    with open(url_img, "rb") as file:
        await context.bot.send_photo(chat_id = update.effective_chat.id, photo=file, filename="corrmatrix2.png")