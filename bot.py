from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import requests

TOKEN = '7084287732:AAGte3fXYdH9_PHiMrSDLmNfOxwif5XYIYM'
ADMIN_ID = 7049798779  # Admin's Telegram ID
NGROK_URL = 'https://495f-100-42-182-93.ngrok-free.app'  # Replace with your ngrok URL

def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Approve User", callback_data='approve')],
        [InlineKeyboardButton("Revoke User", callback_data='revoke')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Welcome to the admin bot!', reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    if query.from_user.id == ADMIN_ID:
        if query.data == 'approve':
            query.edit_message_text(text="Send the username to approve")
            context.user_data['action'] = 'approve'
        elif query.data == 'revoke':
            query.edit_message_text(text="Send the username to revoke")
            context.user_data['action'] = 'revoke'
    else:
        query.edit_message_text(text="Unauthorized")

def handle_message(update: Update, context: CallbackContext) -> None:
    if 'action' in context.user_data:
        username = update.message.text
        if context.user_data['action'] == 'approve':
            response = requests.get(f'{NGROK_URL}/approve_user/{username}')
            update.message.reply_text(response.text)
        elif context.user_data['action'] == 'revoke':
            response = requests.get(f'{NGROK_URL}/revoke_user/{username}')
            update.message.reply_text(response.text)
        del context.user_data['action']
    else:
        update.message.reply_text("Send /start to initiate.")

def main() -> None:
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
