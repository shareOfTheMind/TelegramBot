import re

from telegram import Message
from instagram_content_loader import get_instagram_post_media


# Regular expression to extract the shortcode
regex = r"https://www\.instagram\.com/(?:p|reel)/([^/?]+)"



def get_shortcode_from_message(message: Message) -> str | None:
    str_url = message.text

    match = re.search(regex, str_url)
    if match:
        shortcode = match.group(1)
    else:
        return None

    return shortcode


def get_media_from_ig_post(short_code):
    
    return get_instagram_post_media(shortcode=short_code)