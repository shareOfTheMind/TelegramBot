import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Replace 'YOUR_BOT_TOKEN' with the token you get from BotFather
TOKEN = '7476924663:AAHWu3WA33-SwiZTS_cZ6tGGfNmq3Yp9hWg'
# Replace 'DESTINATION_CHANNEL_ID' with the ID of @mindvirusfeed channel
DESTINATION_CHANNEL_ID = -1002232776392

async def start(update: Update, context):
    await update.message.reply_text('Welcome! Rohan OWNS YOUR SOUL --> Send me any text, video, or link, and I\'ll forward it to the channel.')

async def forward_message(update: Update, context):
    message = update.message

    try:
        # Forward the message to the destination channel
        await message.forward(chat_id=DESTINATION_CHANNEL_ID)
        await message.reply_text("Your submission has been forwarded to the channel.")
    except Exception as e:
        print(f"Error forwarding message: {e}")
        await message.reply_text("Sorry, there was an error forwarding your submission.")

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT | filters.VIDEO | filters.PHOTO | filters.Entity('url'), forward_message))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
