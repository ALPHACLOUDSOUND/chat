from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import requests
import asyncio

TOKEN = '7084287732:AAGte3fXYdH9_PHiMrSDLmNfOxwif5XYIYM'
ADMIN_ID = 7049798779  # Admin's Telegram ID
NGROK_URL = 'https://94e4-100-42-182-93.ngrok-free.app'  # Replace with your ngrok URL

async def start(update: Update, context) -> None:
    keyboard = [
        [InlineKeyboardButton("Approve User", callback_data='approve')],
        [InlineKeyboardButton("Revoke User", callback_data='revoke')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Welcome to the admin bot!', reply_markup=reply_markup)

async def button(update: Update, context) -> None:
    query = update.callback_query
    await query.answer()
    if query.from_user.id == ADMIN_ID:
        if query.data == 'approve':
            await query.edit_message_text(text="Send the username to approve")
            context.user_data['action'] = 'approve'
        elif query.data == 'revoke':
            await query.edit_message_text(text="Send the username to revoke")
            context.user_data['action'] = 'revoke'
    else:
        await query.edit_message_text(text="Unauthorized")

async def handle_message(update: Update, context) -> None:
    if 'action' in context.user_data:
        username = update.message.text
        if context.user_data['action'] == 'approve':
            response = requests.get(f'{NGROK_URL}/approve_user/{username}')
            await update.message.reply_text(response.text)
        elif context.user_data['action'] == 'revoke':
            response = requests.get(f'{NGROK_URL}/revoke_user/{username}')
            await update.message.reply_text(response.text)
        del context.user_data['action']
    else:
        await update.message.reply_text("Send /start to initiate.")

async def main() -> None:
    application = Application.builder().token(TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot
    await application.run_polling()

# Check if the script is run as the main module
if __name__ == '__main__':
    try:
        # Check if an event loop is already running
        loop = asyncio.get_event_loop()
        if loop.is_running():
            print("An event loop is already running. Skipping asyncio.run()")
            loop.create_task(main())
        else:
            asyncio.run(main())
    except RuntimeError as e:
        print(f"RuntimeError: {e}")
