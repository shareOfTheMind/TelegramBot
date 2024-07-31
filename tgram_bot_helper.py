import re

from telegram import Message
from instagram_content_loader import get_instagram_post_media


submission_phrases = [
        "Wow, this masterpiece is going to break the internet. We're truly in the presence of genius.",
        "Thank you for blessing us with this content. The world was waiting for exactly this!",
        "What a revolutionary contribution! Clearly, you're the Einstein of social media.",
        "We're all speechless by your groundbreaking submission. How did we survive without it?",
        "Move over, influencers. There's a new visionary in town!",
        "Just when we thought we'd seen it all, you've outdone yourself. Bravo.",
        "Our humble little platform can barely contain the sheer brilliance of this media.",
        "Please, share more! The world needs every ounce of your unparalleled creativity.",
        "How fortunate we are to witness this. Truly, the next big thing in social media.",
        "You've set a new standard. We're all eagerly waiting for the Nobel Prize announcement."
    ]


def get_shortcode_from_message(message: Message) -> str | None:
    '''
        Regular expression to extract the shortcode from an incoming message text
    '''
    regex = r"https://www\.instagram\.com/(?:p|reel|reels)/([^/?]+)"


    str_url = message.text

    match = re.search(regex, str_url)
    if match:
        shortcode = match.group(1)
    else:
        return None

    return shortcode



def get_media_from_ig_post(short_code: str) -> (tuple[bytes, str, str, bool, int, int | None] | tuple[None, None, None, None, None, None]):
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
    pattern = r'https?://(www\.)?instagram\.com/(p|reel|reels)/[A-Za-z0-9_-]+/?'
    
    # Search for the pattern in the provided text
    match = re.search(pattern, text)
    
    # Return True if a match is found, otherwise False
    return match is not None