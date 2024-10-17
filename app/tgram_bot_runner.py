import datetime
import gc
import random
import traceback

import boto3

from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

from modules.tgram_bot_helper import *
from config.tgram_bot_logger import setup_logger, write_log, remove_old_logs
from modules import DESTINATION_CHANNEL_ID, TOKEN
from modules.database.metadata import Post, User
from modules.database.manager import db_manager

# setup logging
bot_logger = setup_logger(level=10) # debug level logging

# setup s3 client 
s3 = boto3.client('s3')

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Send me any text, video, TikTok link, or Instagram link, and I'll forward the media and meta-data to @mindvirusfeed. Slides and Stories coming soon!")


async def forward_message(update: Update, context: CallbackContext):
    write_log(level='info', message=f"forward_message called with update: {update}")

    submitter = User(username=update.message.chat.username)

    submission_message = []

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
                    media_obj, url, profile, is_video, like_count, view_count, is_carousel, file_type = get_media_from_ig_post(short_code=shortcode)
                    if not media_obj:
                        write_log(message=f"Media Not Parsed Successfully", level='warning')
                        await message.reply_text("Failed to download media from Instagram post.")
                        return
                    
                    write_log(message=f"Media Was Parsed Successfully From Instagram URL", level='info')
                    submission_message.append("Your media was parsed successfully and is processing!\n")

                    # Create post object to upload to the DB
                    post = Post(poster=profile, likes=like_count, views=view_count, source="instagram", share_link=url, file_type=file_type, submitter=submitter)
                    await push_to_db(post, submitter, media_obj) 

                    if is_video:
                        if not is_carousel:
                            caption_data = f"{url}\n❤️ {like_count:,}\n👀 {view_count:,}"
                        else:
                            caption_data = f"{url}\n❤️ {like_count:,}"
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

                ### TODO: We might want to consolidate the logic between tiktok and insta links
                elif contains_tiktok_link(msg_text):
                    write_log(message=f"TikTok Link URL Found Within Message Text", level='info')

                    media_obj, url, profile, is_video, like_count, view_count, file_type = get_media_from_tiktok_post(msg_text)
                    if not media_obj:
                        write_log(message=f"Media Not Parsed Successfully", level='warning')
                        await message.reply_text("Failed to download media from TikTok post.")
                        return
                    
                    write_log(message=f"Media Was Parsed Successfully From TikTok URL", level='info')
                    submission_message.append("Your media was parsed successfully and is processing!\n")

                    # Create post object to upload to the DB
                    post = Post(poster=profile, likes=like_count, views=view_count, source="tiktok", share_link=url, file_type=file_type, submitter=submitter)
                    await push_to_db(post, submitter, media_obj)                    

                    caption_data = f"{url}\n❤️ {like_count:,}\n👀 {view_count:,}"
                    video_input = InputFile(obj=media_obj, filename=f"{profile}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
                    await context.bot.send_video(chat_id=DESTINATION_CHANNEL_ID, video=video_input, caption=caption_data, supports_streaming=True)
                    
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

                # Create post object to upload to the DB
                post = Post(poster=message.chat.username, likes=0, views=0, source="direct", share_link=video_media.file_id, file_type=None, submitter=submitter)
                await push_to_db(post, submitter, None)

                await context.bot.send_video(chat_id=DESTINATION_CHANNEL_ID, video=video_media, caption=f"{update.effective_user.name or 'Custom User'}'s Video")
            # else if the message was photo media
            elif message.photo:
                write_log(message="Photo Message Recieved", level='info')
                photo_media = message.photo[-1]

                # Create post object to upload to the DB
                post = Post(poster=message.chat.username, likes=0, views=0, source="direct", share_link=photo_media.file_id, file_type=None, submitter=submitter)
                await push_to_db(post, submitter, None)

                await context.bot.send_photo(chat_id=DESTINATION_CHANNEL_ID, photo=photo_media, caption=f"{update.effective_user.name or 'Custom User'}'s Photo")

   
            # Forward other post meta-data here message to the destination channel
            submission_message.append(f"[Submitted]\n{random.choice(submission_phrases)}")

            submission_message.append(f"\nCheckout your content on the --> @mindvirusfeed")

            await message.reply_text('\n'.join(submission_message))

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

        write_log(message=f"Error traceback\n\n{chr(10).join(traceback_details)}\n\n", level='debug')

        await message.reply_text("Sorry, there was an error forwarding your submission.")



async def push_to_db(post: Post, submitter: User, media_obj):
    async with db_manager as session:
        session.add(submitter)
        session.add(post)
        session.flush()
        try:
            # Upload the media_obj to s3
            if media_obj:
                s3.upload_fileobj(media_obj, "mindshare-posts-binaries", post.source+"/"+str(post.id)+"."+post.file_type)
            session.commit()
            write_log(message="Post successfully written to the database", level="debug")
        except:
            session.rollback()
            write_log(message="Error writing post to the database", level="error")




def main():
    write_log(message=f"------------------- Starting BOT...", level='info')
    application = Application.builder().token(TOKEN).build()

    write_log(message=f"Intializing Handlers...", level='info')
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT | filters.VIDEO | filters.PHOTO | filters.Entity('url'), forward_message))

    write_log(message=f"Clearing Message Queue and Starting Polling...", level='info')
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
    remove_old_logs()

if __name__ == '__main__':
    main()
