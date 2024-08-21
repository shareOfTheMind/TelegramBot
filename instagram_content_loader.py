import threading
import instaloader
import requests
import os
import time

from instaloader import ConnectionException, Instaloader
from generate_session_from_cookie import generate_session_from_cookies
from tgram_bot_logger import write_log

path_to_session = os.getenv('SESSION_PATH')

# Create an Event to coordinate the session generation
session_generation_event = threading.Event()
session_generation_in_progress = False

def get_instagram_post_media(shortcode):
    global session_generation_in_progress

    # Initialize Instaloader
    loader = instaloader.Instaloader()
    # if we're in the right environment, then load the session; else we good
    if path_to_session:
        loader.load_session_from_file(username='tgrambotlord', filename=path_to_session)
        write_log(message="Successfully loaded IG session from file", level='info')
    else:
        write_log(message="No IG session path found in environment.. Continuing to complete request with Instaloader..", level='warning')

    try:
        post_url = f"https://www.instagram.com/p/{shortcode}/"

        # Load post by shortcode
        post = fetch_post_data(loader, shortcode)

        if post.is_video:
            media_url = post.video_url
        else:
            media_url = post.url

        write_log(message="Make GraphQL Request to Instagram Resources with Instaloader.", level='info')
        # download media content
        response = requests.get(media_url, stream=True)
        response.raise_for_status()

        media_content = response.content

        return media_content, post_url, post.profile, post.is_video, post.likes, post.video_view_count

    except Exception as e:
        write_log(message=f"An Exception occured when calling 'get_instagram_post_media()'\n ---> ({type(e)}) {e}", level='error')
        write_log(message=f"An Exception occured when calling 'get_instagram_post_media()'\n ---> Post URL: {post_url}", level='debug')
        return None, None, None, None, None, None

def fetch_post_data(loader: Instaloader, shortcode: str, max_attempts: int = 3):
    global session_generation_event, session_generation_in_progress

    attempts = 0
    reload_session = False

    while attempts < max_attempts:
        try:
            if reload_session:
                # Ensure session generation happens only once
                if not session_generation_in_progress:
                    session_generation_in_progress = True
                    session_generation_event.clear()
                    threading.Thread(target=generate_session_wrapper).start()
                    session_generation_event.wait()
                    session_generation_in_progress = False

                loader.load_session_from_file(username='tgrambotlord', filename=path_to_session)
                write_log(message="New session successfully loaded from file", level='info')

            return instaloader.Post.from_shortcode(loader.context, shortcode)

        except ConnectionException as cex:
            if '401' in str(cex):
                write_log(message="Response Status Code: 401 UNAUTHORIZED. Attempting to regenerate IG Loader Session from cookies on-the-fly..", level='warning')
                generate_session_wrapper()  # In case session needs regeneration
                reload_session = True
                attempts += 1
                time.sleep(5)
            else:
                raise cex

    raise Exception(f"Failed to fetch post data after {max_attempts} attempts.")

def generate_session_wrapper():
    try:
        generate_session_from_cookies()
    finally:
        # Signal that session generation is complete
        session_generation_event.set()
