import requests

from config.tgram_bot_logger import write_log
from .generate_cookies import generate_cookies, read_cookies_from_file






def get_instagram_post_media(shortcode: str) -> tuple[bytes, str, str, bool, int, int]:

    try:
        post_url = f"https://www.instagram.com/p/{shortcode}/"

        media_data = parse_instagram_data(post_url=post_url)

        response = requests.get(media_data['cdn_link'])
        response.raise_for_status()

        media_content = response.content

        return media_content, post_url, media_data['owner'], media_data['is_video'], media_data['likes'], media_data['views']

    except Exception as e:
        write_log(message=f"An Exception occured when calling 'get_instagram_post_media()'\n ---> ({type(e)}) {e}", level='error')
        write_log(message=f"An Exception occured when calling 'get_instagram_post_media()'\n ---> Post URL: {post_url}", level='debug')
        return None, None, None, None, None, None



# NOTE: requests session logic should be implemented here in a cunning way to avoid logging in every request
# sessions would ideally be managed by time-interval, user-activity, and request limits to avoid IG api backlash
def parse_instagram_data(post_url: str) -> dict:
    # Modify the URL to fetch the JSON data
    json_url = post_url + '?__a=1&__d=dis'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    
    cookie_session = read_cookies_from_file()

    if not cookie_session:
        generate_cookies()

    # Send a GET request to the Instagram JSON endpoint
    response = requests.get(json_url, headers=headers, cookies=cookie_session)

    # if the error is some type of auth error, generate new cookies and try again
    if response.status_code >= 400:
        cookie_session = generate_cookies()
        response = requests.get(json_url, headers=headers, cookies=cookie_session)

    # Check if the request was successful
    if response.status_code != 200:
        # print(f"Failed to retrieve page: Status code {response.status_code}")
        write_log(message=f"Failed to retrieve page: Status code {response.status_code}", level='warning')
        return None

    # Parse the JSON data
    try:
        '''
          NOTE: or, ...[display_resources][-1]['src']

          for caption: ...[edge_media_to_caption][edges][node][text]

          for is_video: ...[is_video]

          for likes: ...[edge_media_preview_like][count]

          for views: ...[video_view_count]

          for play count: ...[video_play_count]

          special video link: ...[video_url]

          [is_ad] can check if its an ad or not (filter spam content)

          owner of post: ...[owner][username]
            - other props include: [id], [is_verified], [profile_pic_url]
        '''

        data = response.json()

        post_data = data.get('graphql', {}).get('shortcode_media')  # The JSON structure for a PHOTO/VIDEO
        cdn_link = None

        if post_data:
            if post_data['is_video']:
                # Video post
                cdn_link = post_data.get('video_url')
            else:
                # Image post
                cdn_link = post_data.get('display_url')

            is_video = post_data['is_video']
            likes    = post_data['edge_media_preview_like']['count']
            views    = post_data.get('video_view_count', None)
        else:
            post_data = data['items'][0]  # The JSON structure for a REEL
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
            'owner': post_data['owner']['username']  # Get the username of the post owner
            # 'caption': post_data.get('edge_media_to_caption', {}).get('edges', [{}])[0].get('node', {}).get('text', '')
        }

    except KeyError as e:
        write_log(message=f"KeyError accessing JSON data: {e}", level='error')
        return None