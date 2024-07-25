import re

from telegram import Message



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


def get_media_from_ig_post(message: Message):
    
    shortcode = get_shortcode_from_message(message=message)