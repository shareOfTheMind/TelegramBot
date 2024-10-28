from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from api.database.manager import get_db  # Use your backend's DB session
from api.database.metadata import User  # Your backend's models
from typing import List

from api.models.api_models import UserCreate, PostCreate

router = APIRouter()




@router.post("/users/", response_model=UserCreate)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    new_user = User(uid=user.uid, username=user.username)
    
    try:
        db.add(new_user)
        await db.flush()
        await db.commit()
        await db.refresh(new_user)

        return new_user
    except IntegrityError as e:
        await db.rollback()  # Roll back the session in case of an error
        if "unique constraint" in str(e.orig):  # Adjust this condition as necessary for your DB
            raise HTTPException(status_code=400, detail="User with this UID already exists.")
        else:
            raise HTTPException(status_code=500, detail="An error occurred while creating the user.")
    


@router.get("/users/", response_model=List[UserCreate])
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    # NOTE: !! if you want to return the posts with the user -- however, I think that functionality should be placed in a separate route either here or in posts !!
    # the above was the original query, however, the posts are backfilled and lazy loaded by default
    # which is causing issues with the asyncrhonous context that we're operating in, the following options were
    # added to allow the posts to be updated quicker with the query
    # result = await db.execute(select(User).options(selectinload(User.posts)))
    users = result.scalars().all()

    return users


@router.get("/users/{uid}", response_model=UserCreate) # change to UserRead, if you want to return the posts with the user
async def get_user_by_id(uid: int, db: AsyncSession = Depends(get_db)):
    # Query to fetch the user by their ID
    # result = await db.execute(select(User).options(selectinload(User.posts)).where(User.uid == uid)) # query to use if you want to load the posts [] associated with the user
    result = await db.execute(select(User).where(User.uid == uid))
    user = result.scalars().first()

    # If the user is not found, raise a 404 error
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user



# Route to get a user and all associated posts
@router.get("/users/{uid}/posts", response_model=List[PostCreate])
async def get_user_posts(uid: int, db: AsyncSession = Depends(get_db)):
    # Ensure user_id is a valid integer
    if uid is None:
        raise HTTPException(status_code=400, detail="User ID cannot be None")

    # Query to fetch the user and eager-load the associated posts
    result = await db.execute(select(User).where(User.uid == uid).options(selectinload(User.posts)))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user.posts