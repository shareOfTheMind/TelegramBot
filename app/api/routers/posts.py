from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.modules.database.manager import get_db  # Use your backend's DB session
from app.modules.database.metadata import Post, User  # Your backend's models
from typing import List

from app.api.models.api_models import PostCreate

router = APIRouter()



@router.post("/posts/", response_model=PostCreate)
async def create_post(post: PostCreate, db: AsyncSession = Depends(get_db)):
    new_post = Post(
        id=post.id,
        poster=post.poster,
        likes=post.likes,
        views=post.views,
        source=post.source,
        share_link=post.share_link,
        file_type=post.file_type,
        submitter_id=post.submitter_id
    )
    db.add(new_post)
    await db.flush()
    await db.commit()
    await db.refresh(new_post)

    return new_post



@router.get("/posts/", response_model=List[PostCreate])
async def get_posts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post))
    posts = result.scalars().all()
    return posts



# Route to get a user and all associated posts
@router.get("/users/{user_id}/posts", response_model=List[PostCreate])
async def get_user_posts(user_id: int, db: AsyncSession = Depends(get_db)):
    # Ensure user_id is a valid integer
    if user_id is None:
        raise HTTPException(status_code=400, detail="User ID cannot be None")

    # Query to fetch the user and eager-load the associated posts
    result = await db.execute(select(User).where(User.id == user_id).options(selectinload(User.posts)))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user.posts