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
session_generation_lock = threading.Lock()
session_generation_in_progress = False

def get_instagram_post_media(shortcode):
    # Initialize Instaloader
    loader = instaloader.Instaloader()
    # if we're in the right environment, then load the session; else we good
    if path_to_session:
        try:
            loader.load_session_from_file(username='tgrambotlord', filename=path_to_session)
        except FileNotFoundError as exF:
            regenerate_session()
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
    '''
        #### Grabs the post data from the Instagram Post API

        Returns the Post object if successful, otherwise raises an Exception.
        
        Note: Will attempt to relogin if there are any permissions issues with stale session
    '''

    attempts = 0
    reload_session = False

    while attempts < max_attempts:
        try:
            if reload_session:
                loader.load_session_from_file(username='tgrambotlord', filename=path_to_session)
                write_log(message="New session successfully loaded from file", level='info')
            return instaloader.Post.from_shortcode(loader.context, shortcode)
        
        except ConnectionException as cex:
            if '401' in str(cex):
                write_log(message="Response Status Code: 401 UNAUTHORIZED. Attempting to regenerate IG Loader Session from cookies on-the-fly..", level='warning')
                regenerate_session()
                reload_session = True  # Reload session next time around
                attempts += 1
                time.sleep(5)  # Wait before retrying
            else:
                raise cex

    raise Exception(f"Failed to fetch post data after {max_attempts} attempts.")

def regenerate_session():
    global session_generation_in_progress

    with session_generation_lock:
        if not session_generation_in_progress:
            session_generation_in_progress = True
            session_generation_event.clear()
            threading.Thread(target=generate_session_wrapper).start()
            session_generation_event.wait()  # Wait for session generation to complete
            session_generation_in_progress = False

def generate_session_wrapper():
    try:
        generate_session_from_cookies()
    finally:
        session_generation_event.set()
