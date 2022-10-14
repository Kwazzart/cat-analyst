import json
from telegram import Update
from telegram.ext import Updater, CallbackContext, TypeHandler


def echo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(json.dumps(update.to_dict(), indent=2))


def main() -> None:
    updater = Updater("5554474456:AAH59s3E6GIngfY6KJKIqsUue8ON-JO5qa8")

    updater.dispatcher.add_handler(TypeHandler(Update, echo))

    updater.start_polling()

    print('Started')

    updater.idle()


if __name__ == "__main__":
    main()