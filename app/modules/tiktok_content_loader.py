import requests
import os
import json
from bs4 import BeautifulSoup
from config.tgram_bot_logger import write_log
from .generate_cookies import get_session_cookies

retry_count = 0

# Create a session object to persist cookies across requests
session = requests.Session()
session.headers.update(
    {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
        "Upgrade-Insecure-Requests": "1",
    }
)


def get_tiktok_post_media(share_link: str) -> tuple[bytes, str, str, bool, int, int]:
    """
    returns a tuple conforming to the following schema:
        (
            content binary (mp4)
            link
            poster
            is video (always True for tiktok)
            likes
            views
        )
    """
    try:
        media_data = parse_tiktok_data(share_link)
        return (
            media_data["content"],
            share_link,
            media_data["owner"],
            True,
            media_data["likes"],
            media_data["views"],
        )
    except Exception as e:
        write_log(
            message=f"An Exception occurred when calling 'get_tiktok_post_media()'\n ---> ({type(e)}) {e}",
            level="error",
        )
        write_log(
            message=f"An Exception occurred when calling 'get_tiktok_post_media()'\n ---> Post URL: {share_link}",
            level="debug",
        )
        return None, None, None, None, None, None


def parse_tiktok_data(share_link: str):

    # we dont need to login for tiktok. Here we attempt to reuse any saved session data
    # as to not get detected as a bot due to constant cookie refreshing
    cookie_session = json.loads(get_session_cookies(tiktok=True))
    if cookie_session:
        session.cookies.update(cookie_session)

    share_link_response = session.get(share_link)

    # update the session data with any new cookies
    if cookie_session != session.cookies:
        os.environ['TIKTOK_SESSION_COOKIES'] = json.dumps(session.cookies.get_dict())


    if share_link_response.status_code != 200:
        write_log(
            message=f"Response failed with status code {share_link_response.status_code}.",
            level="warning",
        )
        write_log(
            message=f"Error {share_link_response.status_code}: {share_link_response.text}",
            level="debug",
        )
        return None

    # scrape all the data
    try:
        share_link_soup = BeautifulSoup(share_link_response.content, "html.parser")

        universal_data_tag = share_link_soup.find(
            id="__UNIVERSAL_DATA_FOR_REHYDRATION__"
        )
        universal_data = json.loads(universal_data_tag.text)
        post_data = universal_data["__DEFAULT_SCOPE__"]["webapp.video-detail"][
            "itemInfo"
        ]["itemStruct"]

        owner = post_data["author"]["uniqueId"]
        likes = post_data["stats"]["diggCount"]
        views = post_data["stats"]["playCount"]
        content_link = (
            post_data["video"]["bitrateInfo"][0]["PlayAddr"]["UrlList"][0]
            .encode("utf-8")
            .decode("unicode_escape")
        )

        # retrieve the actual content binary
        content_response = session.get(content_link)
        content = content_response.content

        return {"content": content, "owner": owner, "likes": likes, "views": views}
    except KeyError as e:
        write_log(message=f"KeyError accessing JSON data: {e}", level="error")
        return None
    except Exception as ex:
        global retry_count
        write_log(
            message=f"An unexpected error occurred in 'parse_tiktok_data()':\n\t--->{type(ex)}\n\t---> {ex}\n\t---> Request Status Code: {content_response.status_code if content_response else 'Unknown'}",
            level="error",
        )

        if retry_count < 1:
            retry_count += 1
            write_log(
                message=f"Refreshing session. Retry Count {retry_count}",
                level="warning",
            )
            os.environ['TIKTOK_SESSION_COOKIES'] = {}

            return parse_tiktok_data(share_link)  # Retry

        return None

# NOTE: for debugging purposes
# if __name__ == "__main__":
#     parse_tiktok_data("https://www.tiktok.com/t/ZP88euGtW/")
