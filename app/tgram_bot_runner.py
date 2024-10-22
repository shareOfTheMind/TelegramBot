import datetime
import gc
import random
import traceback

from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

from modules.tgram_bot_helper import *
from config.tgram_bot_logger import setup_logger, write_log, remove_old_logs
from modules import DESTINATION_CHANNEL_ID, TOKEN
from modules.database.metadata import Post
from modules.database.db_transactions import push_to_db, get_or_create_user, get_user_media_metadata, get_user_media

# setup logging
bot_logger = setup_logger(level=10) # debug level logging

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Send me any text, video, TikTok link, or Instagram link, and I'll forward the media and meta-data to @mindvirusfeed. Slides and Stories coming soon!")


async def forward_message(update: Update, context: CallbackContext):
    write_log(level='info', message=f"forward_message called with update: {update}")

    submitter = await get_or_create_user(username=update.message.chat.username, uid=update.message.from_user.id)

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
                    
                    # Now check if this piece of media exists within our databases before attempting to make a request for it
                    write_log(message='Looking for post object within our databases', level='info')
                    if existing_post:=await get_user_media_metadata(link_code=shortcode):
                        url = existing_post.share_link
                        profile = existing_post.poster
                        is_video = True if existing_post.file_type == 'mp4' else False # NOTE: this will need to change, probably needs to be in the ORM--need a simple bool to tell us video or not
                        like_count = existing_post.likes
                        view_count = existing_post.views
                        is_carousel = False
                        file_type = existing_post.file_type

                        media_obj = get_user_media(media_id=existing_post.id, media_type=existing_post.file_type, media_source=existing_post.source)
                    else:
                        # next, grab the media, url, profile, and video (bool) from post obj
                        media_obj, url, profile, is_video, like_count, view_count, is_carousel, file_type = get_media_from_ig_post(short_code=shortcode)

                    if not media_obj:
                        write_log(message=f"Media Not Parsed Successfully", level='warning')
                        await message.reply_text("Failed to download media from Instagram post.")
                        return
                    
                    write_log(message=f"Media Was Parsed Successfully From Instagram URL", level='info')
                    submission_message.append("Your media was parsed successfully and is processing!\n")

                    if not existing_post:
                        # Create post object to upload to the DB
                        post = Post(poster=profile, likes=like_count, views=view_count, source="instagram", share_link=url, file_type=file_type, submitter=submitter, link_code=shortcode)
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

                    tik_tok_link_code = get_tiktok_link_code(msg_text)
                    # Now check if this piece of media exists within our databases before attempting to make a request for it
                    write_log(message='Looking for post object within our databases', level='info')
                    if existing_post:=await get_user_media_metadata(link_code=shortcode):
                        url = existing_post.share_link
                        profile = existing_post.poster
                        is_video = True # NOTE: this will need to change, probably needs to be in the ORM--need a simple bool to tell us video or not
                        like_count = existing_post.likes
                        view_count = existing_post.views
                        file_type = existing_post.file_type
                        
                        media_obj = get_user_media(media_id=existing_post.id, media_type=existing_post.file_type, media_source=existing_post.source)
                    else:
                        media_obj, url, profile, is_video, like_count, view_count, file_type = get_media_from_tiktok_post(msg_text)
                    if not media_obj:
                        write_log(message=f"Media Not Parsed Successfully", level='warning')
                        await message.reply_text("Failed to download media from TikTok post.")
                        return
                    
                    write_log(message=f"Media Was Parsed Successfully From TikTok URL", level='info')
                    submission_message.append("Your media was parsed successfully and is processing!\n")

                    if not existing_post:
                        # Create post object to upload to the DB
                        post = Post(poster=profile, likes=like_count, views=view_count, source="tiktok", share_link=url, file_type=file_type, submitter=submitter, link_code=tik_tok_link_code)
                        await push_to_db(post, submitter, media_obj)                    

                    caption_data = f"{url}\n❤️ {like_count:,}\n👀 {view_count:,}"
                    video_input = InputFile(obj=media_obj, filename=f"{profile}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
                    await context.bot.send_video(chat_id=DESTINATION_CHANNEL_ID, video=video_input, caption=caption_data, supports_streaming=True)
                    
                    # free memory after sending it to tg channel server
                    # del media_obj
                    media_obj = None
                    gc.collect()

                # if the message does not contain an instagram/tiktok link
                else:
                    await message.forward(chat_id=DESTINATION_CHANNEL_ID)

            # else if the message was video media
            elif message.video:
                write_log(message="Video Message Recieved", level='info')
                video_media = message.video

                # Create post object to upload to the DB
                post = Post(poster=message.chat.username, likes=0, views=0, source="direct", share_link=video_media.file_id, file_type=video_media.mime_type, submitter=submitter, link_code='-1')
                await push_to_db(post, submitter, None)

                await context.bot.send_video(chat_id=DESTINATION_CHANNEL_ID, video=video_media, caption=f"{update.effective_user.name or 'Custom User'}'s Video")
            # else if the message was photo media
            elif message.photo:
                write_log(message="Photo Message Recieved", level='info')
                photo_media = message.photo[-1]

                # Create post object to upload to the DB
                post = Post(poster=message.chat.username, likes=0, views=0, source="direct", share_link=photo_media.file_id, file_type='jpeg', submitter=submitter, link_code='-1')
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
