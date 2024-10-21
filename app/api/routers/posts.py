from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.modules.database.manager import get_db  # Use your backend's DB session
from app.modules.database.metadata import Post, User  # Your backend's models
from typing import List

from app.api.models.api_models import PostCreate, PostsPaginationResponse

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
        link_code=post.link_code,
        submitter_uid=post.submitter_uid
    )

    try:
        db.add(new_post)
        await db.flush()
        await db.commit()
        await db.refresh(new_post)

        return new_post
    except IntegrityError as ie:
        await db.rollback()  # Roll back the session in case of an error
        if "unique constraint" in str(ie.orig):  # Adjust this condition as necessary for your DB
            raise HTTPException(status_code=400, detail="Post with this ID already exists.")
        else:
            raise HTTPException(status_code=500, detail="An error occurred while creating the post.")


    



@router.get("/posts/", response_model=PostsPaginationResponse)
async def get_posts(page: int = Query(1, ge=1), db: AsyncSession = Depends(get_db)):
    # http://localhost:8000/posts/?page=1
    PAGE_SIZE = 50

    # Calculate offset based on the page and fixed page size
    offset = (page - 1) * PAGE_SIZE

    try:
        # Query the total number of posts to calculate total pages
        total_posts_query = select(func.count(Post.id))  # Modify to match your ORM query
        total_posts_result = await db.execute(total_posts_query)
        total_posts = total_posts_result.scalar_one()  # Get the scalar value (total count)

        # Query the posts for the current page with LIMIT and OFFSET
        posts_query = select(Post).limit(PAGE_SIZE).offset(offset)
        result = await db.execute(posts_query)
        posts = result.scalars().all()

        # Convert SQLAlchemy Post objects to Pydantic models
        pydantic_posts = [PostCreate.model_validate(post) for post in posts]

        # Calculate total pages
        total_pages = (total_posts + PAGE_SIZE - 1) // PAGE_SIZE  # Round up division

        # Generate next page URL if there are more pages
        next_page_url = None
        if page < total_pages:
            next_page_url = f"/posts/?page={page + 1}"

        response_data = {
            "data": pydantic_posts,
            "pagination" : {
                "current_page": page,
                "total_pages": total_pages,
                "next_page": next_page_url
            }
        }

        return response_data

        # result = await db.execute(select(Post))
        # posts = result.scalars().all()
        # return posts
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching ALL posts: {str(ex)}")



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