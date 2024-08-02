from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import requests

TOKEN = '7084287732:AAGte3fXYdH9_PHiMrSDLmNfOxwif5XYIYM'
ADMIN_ID = 7049798779  # Admin's Telegram ID
NGROK_URL = 'https://495f-100-42-182-93.ngrok-free.app'  # Replace with your ngrok URL

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Welcome to the admin bot!')

def approve(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id == ADMIN_ID:
        username = context.args[0]
        response = requests.get(f'{NGROK_URL}/approve_user/{username}')
        update.message.reply_text(response.text)
    else:
        update.message.reply_text('Unauthorized')

def revoke(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id == ADMIN_ID:
        username = context.args[0]
        response = requests.get(f'{NGROK_URL}/revoke_user/{username}')
        update.message.reply_text(response.text)
    else:
        update.message.reply_text('Unauthorized')

def main() -> None:
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("approve", approve))
    dispatcher.add_handler(CommandHandler("revoke", revoke))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
