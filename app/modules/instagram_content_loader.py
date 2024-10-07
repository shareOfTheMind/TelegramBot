import threading
import requests

from config.tgram_bot_logger import write_log







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




def parse_instagram_data(post_url: str) -> dict:
    # Modify the URL to fetch the JSON data
    json_url = post_url + '?__a=1&__d=dis'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    # Send a GET request to the Instagram JSON endpoint
    response = requests.get(json_url, headers=headers)

    # Check if the request was successful
    if response.status_code != 200:
        # print(f"Failed to retrieve page: Status code {response.status_code}")
        write_log(message=f"Failed to retrieve page: Status code {response.status_code}", level='warning')
        return None

    # Parse the JSON data
    try:
        data = response.json()

        post_data = data['graphql']['shortcode_media']  # The JSON structure may vary, but this usually holds the media data
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
        cdn_link = None

        if post_data['is_video']:
            # Video post
            cdn_link = post_data.get('video_url')
        else:
            # Image post
            cdn_link = post_data.get('display_url')

        return {
            'cdn_link': cdn_link,
            'is_video': post_data['is_video'],
            'likes': post_data['edge_media_preview_like']['count'],
            'views': post_data['video_view_count'],
            'owner': post_data['owner']['username']  # Get the username of the post owner
            # 'caption': post_data.get('edge_media_to_caption', {}).get('edges', [{}])[0].get('node', {}).get('text', '')
        }

    except KeyError as e:
        write_log(f"KeyError accessing JSON data: {e}")
        return None
