import re

from telegram import Message
from instagram_content_loader import get_instagram_post_media





def get_shortcode_from_message(message: Message) -> str | None:
    # Regular expression to extract the shortcode
    regex = r"https://www\.instagram\.com/(?:p|reel)/([^/?]+)"


    str_url = message.text

    match = re.search(regex, str_url)
    if match:
        shortcode = match.group(1)
    else:
        return None

    return shortcode



def get_media_from_ig_post(short_code: str) -> (tuple[bytes, str, str, bool] | tuple[None, None, None, None]):
    '''
        Calls `get_instagram_post_media()` to extract specific metadata from an instagram post

        Returns a tuple containing
        - The media content (bytes)
        - The post URL (str)
        - The profile URL (str)
        - A boolean indicating whether the post is a video (bool)
    '''
    
    return get_instagram_post_media(shortcode=short_code)



def contains_instagram_link(text: str) -> bool:
    '''
        Function to return whether or not an instagram link exists within the given text
    '''

    # Regular expression to match Instagram /p/ or /reel/ links
    pattern = r'https?://(www\.)?instagram\.com/(p|reel)/[A-Za-z0-9_-]+/?'
    
    # Search for the pattern in the provided text
    match = re.search(pattern, text)
    
    # Return True if a match is found, otherwise False
    return match is not None