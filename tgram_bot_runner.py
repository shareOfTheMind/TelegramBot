import os
import datetime
import gc
import random
import traceback

from dotenv import load_dotenv
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from asyncio import QueueEmpty

from tgram_bot_helper import *
from tgram_bot_logger import setup_logger, write_log, remove_old_logs

# setup logging
bot_logger = setup_logger()

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
    write_log(level='info', message=f"Forward_message called with update: {update}")


    message = update.message
    try:
        # check to see if a message exists; and also ignore messages directly sent within the channel
        if message:
            write_log(message=f"A Message Was Received, Processing Message", level='info')
            # if the message is text
            if message.text:
                msg_text = message.text
                write_log(message=f"Processing Text Message: {msg_text}", level='info')

                # Let's check to see if the message text being forwarded contains an instagram link
                if contains_instagram_link(msg_text):
                    write_log(message=f"Instagram Link URL Found Within Message Text", level='info')

                    # firstly, get the shortcode and ensure that it was parsed successfully from a valid instagram post url
                    shortcode = get_shortcode_from_message(message=message)
                    if not shortcode:
                        write_log(message=f"No valid Instagram post URL found within message, unsuccessful in parsing shortcode", level='warning')
                        await message.reply_text("No valid Instagram post URL found in the message.")
                        return
                
                    # next, grab the media, url, profile, and video (bool) from post obj
                    media_obj, url, profile, is_video, like_count, view_count = get_media_from_ig_post(short_code=shortcode)
                    if not media_obj:
                        write_log(message=f"Media Not Parsed Successfully", level='warning')
                        await message.reply_text("Failed to download media from Instagram post.")
                        return
                    
                    write_log(message=f"Media Was Parsed Successfully From Instagram URL", level='info')
                    await message.reply_text("Your media was parsed successfully and is processing!")
                    if is_video:
                        caption_data = f"{url}\n❤️ {like_count:,}\n👀 {view_count:,}"
                        video_input = InputFile(obj=media_obj, filename=f"{profile}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
                        await context.bot.send_video(chat_id=DESTINATION_CHANNEL_ID, video=video_input, caption=caption_data, supports_streaming=True)
                    else:
                        caption_data = f"{url}\n❤️ {like_count:,}"
                        new_media = InputFile(obj=media_obj, filename=f"{profile}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
                        await context.bot.send_photo(chat_id=DESTINATION_CHANNEL_ID, photo=new_media, caption=caption_data)
                    
                    # free memory after sending it to tg channel server
                    # del media_obj
                    media_obj = None
                    gc.collect()

                # if the message does not contain an instagram link
                else:
                    await message.forward(chat_id=DESTINATION_CHANNEL_ID)

            # else if the message was video media
            elif message.video:
                write_log(message="Video Message Recieved", level='info')
                video_media = message.video

                await context.bot.send_video(chat_id=DESTINATION_CHANNEL_ID, video=video_media, caption=f"{update.effective_user or 'Custom User'}'s Video")
            # else if the message was photo media
            elif message.photo:
                write_log(message="Photo Message Recieved", level='info')
                photo_media = message.photo[-1]

                await context.bot.send_photo(chat_id=DESTINATION_CHANNEL_ID, photo=photo_media, caption=f"{update.effective_user or 'Custom User'}'s Photo")

   

            # Forward other post meta-data here message to the destination channel
            await message.reply_text(f"[Submitted]\n{random.choice(submission_phrases)}")
            # await message.reply_text("Your submission has been forwarded to the channel.")

        # If there is no message being forwarded (no Update message); then do nothing
        else:
            write_log(message=f"No Message Was Found In Update", level='warning')
            return
    except Exception as e:
        write_log(message=f"Error Forwarding Message: {e}", level='error')

        # log the traceback for the exception
        tb = traceback.extract_tb(e.__traceback__)

        # examine traceback and list all exceptions potentially caught and display intricate details
        traceback_details = []
        for frame in tb:
            traceback_details.append("".ljust(50,'-'))
            traceback_details.append(f"Offending File: {frame.filename}")
            traceback_details.append(f"Exception on Line: {frame.lineno}")
            traceback_details.append(f"Scope of Exception: {frame.name}")
            traceback_details.append(f"Offending Line of Exception: {frame.line}")
            traceback_details.append(f"".ljust(50,'-') + '\n')

        write_log(message=f"Error traceback\n\n{'\n'.join(traceback_details)}\n\n", level='debug')

        await message.reply_text("Sorry, there was an error forwarding your submission.")


# Function to clear the update queue
async def clear_update_queue(application: Application):
    queue = application.updater.update_queue
    no_items = 0
    while not queue.empty():
        try:
            queue.get_nowait()
            no_items += 1
        except QueueEmpty:
            write_log(message=f"{no_items} Items Removed from Queue.", level='info')
            break


def main():
    write_log(message=f"------------------- Starting BOT...", level='info')
    application = Application.builder().token(TOKEN).build()

    write_log(message=f"Intializing Handlers...", level='info')
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT | filters.VIDEO | filters.PHOTO | filters.Entity('url'), forward_message))

    write_log(message=f"Clearing Message Queue", level='info')
    clear_update_queue(application=application)

    write_log(message=f"Starting Polling", level='info')
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    remove_old_logs()

if __name__ == '__main__':
    main()
