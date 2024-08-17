import instaloader
import requests
import os
import time

from generate_session_from_cookie import generate_session_from_cookies
from tgram_bot_logger import write_log
# from dotenv import load_dotenv

# load_dotenv()

path_to_session = os.getenv('SESSION_PATH')

def get_instagram_post_media(shortcode):

    attempts = 0

    # Initialize Instaloader
    loader = instaloader.Instaloader()

    # if we're in the right environment, then load the session; else we good
    if path_to_session:
        loader.load_session_from_file(username='tgrambotlord', filename=path_to_session)
        write_log(message=f"Successfully loaded IG session from file", level='info')
    else:
        write_log(message=f"No IG session path found in environment.. Continuing to complete request with instaloader..", level='warning')


    try:
        post_url = f"https://www.instagram.com/p/{shortcode}/"

        # Load post by shortcode
        post = instaloader.Post.from_shortcode(loader.context, shortcode)

        # if post is a video, return the video url; else return the photo
        if post.is_video:
            media_url = post.video_url
        else:
            media_url = post.url

        while attempts < 3:
            write_log(message=f"Make GraphQL Request to Instagram Resources with Instaloader. Attempt {attempts+1} of 3..", level='info')
            # download media content
            response = requests.get(media_url, stream=True)

            # if IG is blocking our request for some reason, we may need to regenerate an IG loader session on-the-fly from a quick login
            if response.status_code == 401:
                write_log(message=f"Response Status Code: 401 UNAUTHORIZED. Attempting to regenerate IG Loader Session from cookies on-the-fly..", level='warning')
                generate_session_from_cookies()
            else:
                break
            
            attempts += 1
            time.sleep(5)


        response.raise_for_status() # ensure we notice bad response that isn't unauthorized

        # store media content in a variable
        media_content = response.content


        return media_content, post_url, post.profile, post.is_video, post.likes, post.video_view_count

    except Exception as e:
        write_log(message=f"An Exception occured when calling 'get_instagram_post_media()'\n -> {e}", level='error')
        write_log(message=f"An Exception occured when calling 'get_instagram_post_media()'\n -> Post URL: {post_url}", level='debug')
        # print(f"An error occurred: {e}")
        return None, None, None, None, None, None
    


# def download_instagram_post_video(shortcode):
#     # Initialize Instaloader
#     loader = instaloader.Instaloader()

#     try:
#         # Load post by shortcode
#         post = instaloader.Post.from_shortcode(loader.context, shortcode)

#         dir_name = f"{post.owner_username}_{shortcode}"
#         loader.download_post(post=post, target=dir_name)
        
#         media_path = find_mp4_files(directory=dir_name)
#         return media_path

#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return None, None, None, None
    



# def find_mp4_files(directory):
#     # Use glob to find all .mp4 files in the given directory
#     mp4_files = glob.glob(os.path.join(directory, '*.mp4'))
#     if mp4_files:
#         return mp4_files.pop(0)
    
#     return None
