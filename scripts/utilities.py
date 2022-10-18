from telegram import InlineKeyboardButton

def create_buttons(arr):
    buttons = []
    for text, cd in arr:
        buttons.append([InlineKeyboardButton(text, callback_data = cd)])
    return buttons