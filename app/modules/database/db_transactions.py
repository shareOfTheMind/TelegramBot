'''
    Methods to do database operations
'''

import io

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncResult
from typing import Optional
from config.tgram_bot_logger import write_log
from modules.database.metadata import Post, User
from modules.database.manager import db_manager
from . import s3, BUCKET_NAME



async def push_to_db(post: Post, submitter: User, media_obj: bytes):
    write_log(message='Writing submission to database...', level='info')
    async with db_manager as session:
        session.add(submitter)
        session.add(post)
        await session.flush()

        try:
            # Upload the media_obj to s3
            if media_obj:
                # wrap medi_obj in a BytesIO object
                file_obj = io.BytesIO(media_obj)
                s3.upload_fileobj(file_obj, "mindshare-posts-binaries", post.source+"/"+str(post.id)+"."+post.file_type)
            await session.commit()
            write_log(message="Post successfully written to the database", level="info")
        except Exception as ex:
            await session.rollback()
            write_log(message=f"Error writing post to the database: {str(ex)}", level="error")


# async def get_or_create_user(username: str, **kwargs) -> User:
async def get_or_create_user(username: str, uid: int) -> User:
    """
    Retrieve a user by username, or create a new user if not found.

    Args:
        username (str): The username of the user.
        - NOT IMPLEMENTED **kwargs: Additional attributes for creating a new user.

    Returns:
        User: The retrieved or newly created User object.
    """
    write_log(message=f'Checking for user "{username}" with telegram user id: {uid}...', level='info')
    
    async with db_manager as session:
        # Attempt to retrieve the user
        result: AsyncResult = await session.execute(select(User).filter(User.uid == uid))
        user: Optional[User] = result.scalars().first()
        
        if user:
            write_log(message="User found, retrieving user.", level="info")
            return user  # Return the existing user
        
        # If user doesn't exist, create a new one
        write_log(message="User not found, creating new user...", level='info')
        user = User(username=username, uid=uid)
        # user = User(username=username, **kwargs)  # Assuming kwargs are other User fields
        session.add(user)
        await session.flush()  # Flush to get the ID and other defaults

        try:
            await session.commit()
            write_log(message="New user successfully created in the database", level="info")
            return user  # Return the newly created user
        except Exception as ex:
            await session.rollback()
            write_log(message=f"Error creating user: {str(ex)}", level="error")
            raise  # Optionally re-raise the exception if needed



async def user_exists(uid: int) -> bool:
    """
        Check if a user with the specified name exists in the database.

        Args:
            username (str): The name of the user to check for.

        Returns:
            bool: True if the user exists, False otherwise.
    """
    async with db_manager as session:
        result: AsyncResult = await session.execute(select(User).filter(User.uid == uid))
        user: Optional[User] = result.scalars().first()

        return user is not None  # Return True if user exists, False otherwise
    


async def get_user_by_uid(uid: int) -> User:
    """
    Retrieve a user from the database by unique id.

    Args:
        username (str): The username of the user to retrieve.

    Returns:
        User: The User object if found, None otherwise.
    """
    write_log(message=f'Retrieving user with uid: {uid}...', level='info')
    
    # Use the global db_manager to manage the session
    async with db_manager as session:
        result: AsyncResult = await session.execute(select(User).filter(User.uid == uid))
        user: Optional[User] = result.scalars().first()
        
        if user:
            write_log(message="User successfully retrieved from the database", level="info")
        else:
            write_log(message="User not found", level="warning")
        
        return user  # Return the User object (or None if not found)

        

async def get_user_media(media_id: int, media_type: str, media_source: str) -> Optional[bytes]:
    write_log(message=f"Retrieving user media from bucket", level='info')

    media_filepath_query = f"{media_source}/{str(media_id)}.{media_type}"

    # Use the global s3 client to retrieve the media from s3
    response = s3.get_object(Bucket=BUCKET_NAME, Key=media_filepath_query)

    if media_content:=response['Body']:
        media_content = media_content.read()
        write_log(message=f"Media successfully retrieved from bucket", level="info")
        return media_content
    
    write_log(message=f"Media not found for id: {media_id}", level="warning")
    return None


async def get_user_media_metadata(link_code: str):
    write_log(message=f'Retrieving post metadata {link_code}...', level='info')
    
    # Use the global db_manager to manage the session
    async with db_manager as session:
        result: AsyncResult = await session.execute(select(Post).filter(Post.link_code == link_code))
        post: Optional[Post] = result.scalars().first()
        
        if post:
            write_log(message="Post successfully retrieved from the database", level="info")
        else:
            write_log(message="Post object does not exist.. Request will be made to given url", level="warning")
        
        return post  # Return the User object (or None if not found)