import re

from telegram import Message
from .instagram_content_loader import get_instagram_post_media
from config.tgram_bot_logger import write_log


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
        "You've set a new standard. We're all eagerly waiting for the Nobel Prize announcement.",
        "Stop everything! This is exactly the content humanity's been waiting for since the dawn of time."
        "You've really outdone yourself this time. Watch out, history books, here comes a new chapter!",
        "Finally! A post that will solve world hunger, bring world peace, and cure Monday blues all at once.",
        "I'm getting chills from the sheer innovation. Surely the Louvre is calling to showcase this next.",
        "Thank you for gracing us with something so original. Groundbreaking doesn't even begin to cover it.",
        "I'm sure NASA will want to study this content for its sheer brilliance.",
        "Please, don't stop! The universe just shifted to make room for your genius.",
        "Wow, someone notify the UN. This post is clearly the solution to every global crisis.",
        "If there was ever a cure for boredom, I'm confident this content is the antidote.",
        "We're all in awe. Surely this content is what's been missing from every history textbook.",
        "Brace yourselves, folks. This is the kind of post that will echo through eternity.",
        "Hold on, I'm contacting the Pulitzer committee. Your contribution deserves all the awards.",
        "Legend has it, people will speak of this post for generations to come.",
        "I think the entire internet just had a collective 'aha' moment after seeing this.",
        "Einstein, who? This level of genius might be the new face of intellectual greatness.",
        "I didn't know the meaning of true art until this moment. Thank you for the enlightenment.",
        "Honestly, I didn't think content could reach this level. The rest of us are just amateurs.",
        "You've done it. You've finally cracked the code for internet fame. The rest of us will try to keep up.",
        "Oh, wow. The cultural impact of this post is going to leave us all reeling for centuries.",
        "Clearly, every genius out there is scrambling to catch up with this next-level contribution."
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



def contains_tiktok_link(text: str) -> bool:
    '''
        Function to return whether the provided string is a tiktok share link
    '''

    # already escaped so we dont need the "r" string specifier
    pattern = "^https:\/\/www\.tiktok\.com\/(?:@[\w.]+\/video\/\d+|t\/[\w]+)\/?$"

    match = re.search(pattern, text)
    return match is not None
