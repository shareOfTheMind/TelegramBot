import os
import datetime

from dotenv import load_dotenv
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

from tgram_bot_helper import *
# from instagram_content_loader import download_instagram_post_video

# load environment variables
load_dotenv()
api_token = os.getenv('API_KEY')
# chan_id = int(os.getenv('DEV_ID'))
chan_id = int(os.getenv('DEST_CHAN_ID'))

# Replace 'YOUR_BOT_TOKEN' with the token you get from BotFather
TOKEN = api_token
# Replace 'DESTINATION_CHANNEL_ID' with the ID of @mindvirusfeed channel
DESTINATION_CHANNEL_ID = chan_id

# context = None

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('Welcome! Rohan OWNS YOUR SOUL --> Send me any text, video, or link, and I\'ll forward it to the channel.')

async def forward_message(update: Update, context: CallbackContext):
    message = update.message
    try:
        # check to see if a message exists; and also ignore messages directly sent within the channel
        if message:
            
            # NOTE: You're gonna wanna check for IG link within the message text, and if not, just forward the message text
            # firstly, get the shortcode and ensure that it was parsed successfully from a valid instagram post url
            if message.text:
                shortcode = get_shortcode_from_message(message=message)
                if not shortcode:
                    await message.reply_text("No valid Instagram post URL found in the message.")
                    return
            
                # next, grab the media, url, profile, and video (bool) from post obj
                media_obj, url, profile, is_video = get_media_from_ig_post(short_code=shortcode)
                if not media_obj:
                    await message.reply_text("Failed to download media from Instagram post.")
                    return
                
                if is_video:
                    video_input = InputFile(obj=media_obj, filename=f"{profile}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
                    await context.bot.send_video(chat_id=DESTINATION_CHANNEL_ID, video=video_input, caption=url, supports_streaming=True)
                else:
                    new_media = InputFile(obj=media_obj, filename=f"{profile}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
                    await context.bot.send_photo(chat_id=DESTINATION_CHANNEL_ID, photo=new_media, caption=url)
            elif message.video:
                video_media = message.video

                await context.bot.send_video(chat_id=DESTINATION_CHANNEL_ID, video=video_media, caption="Custom User Video")

   

            # Forward other post meta-data here message to the destination channel
            # await message.forward(chat_id=DESTINATION_CHANNEL_ID)
            await message.reply_text("Your submission has been forwarded to the channel.")

        # If there is no message being forwarded (no Update message); then do nothing
        else:
            return
    except Exception as e:
        print(f"Error forwarding message: {e}")
        print(f"Type Error: {type(e)}")
        await message.reply_text("Sorry, there was an error forwarding your submission.")

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT | filters.VIDEO | filters.PHOTO | filters.Entity('url'), forward_message))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
