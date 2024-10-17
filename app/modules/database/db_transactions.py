'''
    Methods to do database operations
'''

import io

from typing import Optional
from config.tgram_bot_logger import write_log
from modules.database.metadata import Post, User
from modules.database.manager import db_manager
from . import s3



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
async def get_or_create_user(username: str) -> User:
    """
    Retrieve a user by username, or create a new user if not found.

    Args:
        username (str): The username of the user.
        **kwargs: Additional attributes for creating a new user.

    Returns:
        User: The retrieved or newly created User object.
    """
    write_log(message=f'Checking for user with username: {username}...', level='info')
    
    async with db_manager as session:
        # Attempt to retrieve the user
        user: Optional[User] = await session.query(User).filter(User.username == username).first()
        
        if user:
            write_log(message="User found, retrieving user.", level="info")
            return user  # Return the existing user
        
        # If user doesn't exist, create a new one
        write_log(message="User not found, creating new user...", level='info')
        user = User(username=username)
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



async def user_exists(username: str) -> bool:
    """
        Check if a user with the specified name exists in the database.

        Args:
            username (str): The name of the user to check for.

        Returns:
            bool: True if the user exists, False otherwise.
    """
    async with db_manager as session:
        return session.query(User).filter(User.username == username).first() is not None
    


async def get_user_by_username(username: str) -> User:
    """
    Retrieve a user from the database by username.

    Args:
        username (str): The username of the user to retrieve.

    Returns:
        User: The User object if found, None otherwise.
    """
    write_log(message=f'Retrieving user with username: {username}...', level='info')
    
    # Use the global db_manager to manage the session
    async with db_manager as session:
        user = await session.query(User).filter(User.username == username).first()  # Retrieve user by username
        
        if user:
            write_log(message="User successfully retrieved from the database", level="info")
        else:
            write_log(message="User not found", level="warning")
        
        return user  # Return the User object (or None if not found)

        