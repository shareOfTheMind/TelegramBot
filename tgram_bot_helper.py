import re

from telegram import Message
from instagram_content_loader import download_instagram_post


# Regular expression to extract the shortcode
regex = r"https://www\.instagram\.com/p/([^/?]+)"



def get_shortcode_from_message(message: Message) -> str | None:
    str_url = message.text

    match = re.search(regex, str_url)
    if match:
        shortcode = match.group(1)
    else:
        return None

    return shortcode


def get_media_from_ig_post(message: Message) -> bytes | None:
    
    shortcode = get_shortcode_from_message(message=message)

    return download_instagram_post(shortcode=shortcode)