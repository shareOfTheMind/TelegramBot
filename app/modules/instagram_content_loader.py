import requests
from config.tgram_bot_logger import write_log
from .generate_cookies import generate_cookies, read_cookies_from_file

retry_count = 0

# Create a session object to persist cookies across requests
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.9',
    'X-Requested-With': 'XMLHttpRequest',
    'Connection': 'keep-alive',
    'Cache-Control': 'no-cache',
    'Upgrade-Insecure-Requests': '1'
})


def get_instagram_post_media(shortcode: str) -> tuple[bytes, str, str, bool, int, int]:
    try:
        post_url = f"https://www.instagram.com/p/{shortcode}/"
        session.headers.update({'Referer': f'https://www.instagram.com/p/{shortcode}/'})
        media_data = parse_instagram_data(post_url=post_url)

        response = session.get(media_data['cdn_link'])
        response.raise_for_status()

        media_content = response.content

        return media_content, post_url, media_data['owner'], media_data['is_video'], media_data['likes'], media_data['views'], media_data['is_carousel']

    except Exception as e:
        write_log(message=f"An Exception occurred when calling 'get_instagram_post_media()'\n ---> ({type(e)}) {e}", level='error')
        write_log(message=f"An Exception occurred when calling 'get_instagram_post_media()'\n ---> Post URL: {post_url}", level='debug')
        return None, None, None, None, None, None, None


def parse_instagram_data(post_url: str) -> dict:
    json_url = post_url + '?__a=1&__d=dis'

    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    # }

    cookie_session = read_cookies_from_file("../config/instagram_cookies.txt")

    if not cookie_session:
        generate_cookies()

    # Update session with the retrieved cookies
    session.cookies.update(cookie_session)

    # Send a GET request to the Instagram JSON endpoint
    response = session.get(json_url)

    # Check if response failed and retry with new cookies
    if response.status_code >= 400:
        write_log(message=f"Response failed with status code {response.status_code}. Generating new cookies.", level='warning')
        cookie_session = generate_cookies()
        session.cookies.update(cookie_session)
        response = session.get(json_url)

    # Check if the request was successful
    if response.status_code != 200:
        write_log(message=f"Failed to retrieve page: Status code {response.status_code}", level='warning')
        return None

    try:
        data = response.json()

        post_data = data.get('graphql', {}).get('shortcode_media')  
        cdn_link = None

        if post_data:
            if post_data['is_video']:
                cdn_link = post_data.get('video_url')
            else:
                cdn_link = post_data.get('display_url')

            is_video = post_data['is_video']
            likes    = post_data['edge_media_preview_like']['count']
            views    = post_data.get('video_view_count', None)
        else:
            post_data = data['items'][0]
            post_owner = post_data['owner']['username']
            # carasoul check
            is_carousel_item = 'carousel' in post_data.get('product_type')


            if is_carousel_item:
                likes = post_data['like_count']

                all_media = post_data['carousel_media']
                post_data = all_media[0] # take the first item because we don't have a way to select carousel data right now from bot interface

                is_video = post_data['media_type'] != 1

                if is_video:
                    cdn_link = post_data['video_versions'][0]['url']
                else:
                    cdn_link = post_data['image_versions2']['candidates'][0]['url']
            # all other media that is not a carousel item
            else:
                is_video = post_data['media_type'] != 1

                if is_video:
                    cdn_link = post_data['video_versions'][0]['url']
                else:
                    cdn_link = post_data['image_versions2']['candidates'][0]['url']

                likes    = post_data['like_count']


            views    = post_data.get('play_count', 0)

        return {
            'cdn_link': cdn_link,
            'is_video': is_video,
            'likes': likes,
            'views': views,
            'owner': post_owner,
            'is_carousel': is_carousel_item
        }

    except KeyError as e:
        write_log(message=f"KeyError accessing JSON data: {e}", level='error')
        return None
    except Exception as ex:
        global retry_count
        write_log(message=f"An unexpected error occurred in 'parse_instagram_data()':\n\t--->{type(ex)}\n\t---> {ex}\n\t---> Request Status Code: {response.status_code if response else 'Unknown'}", level='error')

        if 'challenge' in response.url and retry_count < 3:
            write_log(message=f"Detected Instagram challenge. Generating new cookies. Retry Count {retry_count+1}", level='warning')
            retry_count += 1
            generate_cookies()
            return parse_instagram_data(post_url=post_url)  # Retry

        return None
