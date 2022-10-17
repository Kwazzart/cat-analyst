async def start(update, context): 
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text='иди нах)'
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
    text = 'ладно все заткнись'
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=text
    )