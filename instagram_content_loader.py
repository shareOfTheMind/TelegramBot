import os
import instaloader
import requests

def download_instagram_post(shortcode):
    # Initialize Instaloader
    loader = instaloader.Instaloader()

    try:

        # Load post by shortcode
        post = instaloader.Post.from_shortcode(loader.context, shortcode)

        media_url = post.url
        # Download media
        # loader.download_post(post, target=f"{post.owner_username}_{shortcode}")

        # download media content
        response = requests.get(media_url)
        response.raise_for_status() # ensure we notice bad response

        # store media content in a variable
        media_content = response.content


        return media_content


    except Exception as e:
        print(f"An error occurred: {e}")
        return None







# if __name__ == "__main__":
#     # Example Instagram post URL
#     # post_url = "https://www.instagram.com/p/your_post_shortcode/"
#     # post_url = "https://www.instagram.com/p/CI4QG6gjW3a/"
#     # post_url = "https://www.instagram.com/p/CtMaz6LLHgR/"

#     # codes = ["CI4QG6gjW3a","CtMaz6LLHgR","C90R_ojOy_A"]
#     codes = ["CI4QG6gjW3a"]

#     for short_code in codes:
#         download_instagram_post(f"https://www.instagram.com/p/{short_code}/")
    
    # download_instagram_post(post_url)
    


# import os
# import instaloader

# def download_instagram_post(post_url):
#     # Initialize Instaloader
#     loader = instaloader.Instaloader()

#     try:
#         # Extract post shortcode from URL
#         shortcode = post_url.split('/')[-2]

#         # Load post by shortcode
#         post = instaloader.Post.from_shortcode(loader.context, shortcode)

#         # Download media
#         # loader.download_post(post, target=f"{post.owner_username}_{shortcode}")

#         print("".ljust(100, "#"))
#         print(f"Downloaded media from post: {post_url}")
#         print(f"Shortcode: {shortcode}")
#         print(f"Caption: {post.caption}")

#         for hashtag in post.caption_hashtags:
#             print(f"Hashtag: {hashtag}")

#         for mentioned in post.caption_mentions:
#             print(f"Mentioned user: {mentioned}")

#         print("".ljust(100, "#"))
#         print()

#     except Exception as e:
#         print(f"An error occurred: {e}")

# if __name__ == "__main__":
#     # Example Instagram post URL
#     # post_url = "https://www.instagram.com/p/your_post_shortcode/"
#     # post_url = "https://www.instagram.com/p/CI4QG6gjW3a/"
#     # post_url = "https://www.instagram.com/p/CtMaz6LLHgR/"

#     # codes = ["CI4QG6gjW3a","CtMaz6LLHgR","C90R_ojOy_A"]
#     codes = ["CI4QG6gjW3a"]

#     for short_code in codes:
#         download_instagram_post(f"https://www.instagram.com/p/{short_code}/")
    
#     # download_instagram_post(post_url)
