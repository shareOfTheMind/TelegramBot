from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from app.modules.database.__init__ import s3, BUCKET_NAME
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.modules.database.manager import get_db  # Use your backend's DB session
from app.modules.database.metadata import Post  # Your backend's models
from app.api.models.api_models import PostCreate, PostsPaginationResponse, PostRead, PostMedia
from typing import Dict, Union

router = APIRouter()



@router.post("/posts/", response_model=PostCreate, status_code=status.HTTP_201_CREATED)
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
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching posts: {str(ex)}")



'''
    S3 Route
'''

@router.get("/posts/media/")
async def get_media(media_data: PostRead):
    try:
        if not media_data.id:
            raise HTTPException(status_code=400, detail="No media ID provided")
        media_id = media_data.id

        media_file_name = '.'.join([str(media_id), media_data.file_type])
        media_object_query_path = '/'.join([media_data.source, media_file_name])
        # Try to get the object from S3
        response = s3.get_object(Bucket=BUCKET_NAME, Key=media_object_query_path)
        
        # Read the object's content
        media_content = response['Body'].read()

        return Response(content=media_content, media_type=f"application/{media_data.file_type}")
        # stream_response = StreamingResponse(media_content, media_type=f"application/{media_data.file_type}")

        # stream_response.headers['X-Media-ID'] = str(media_id)
        # stream_response.headers['X-Media-Type'] = media_data.file_type
        # stream_response.headers['X-Link-Code'] = media_data.link_code or ''

        # return stream_response
    
    except s3.exceptions.NoSuchKey:
        raise HTTPException(status_code=404, detail=f"Object [{media_file_name}] not found in the S3 bucket")
    except (NoCredentialsError, PartialCredentialsError):
        raise HTTPException(status_code=500, detail="AWS credentials not found or incomplete")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/posts/{ucode}", response_model=PostRead)
async def get_user_posts(ucode: str, db: AsyncSession = Depends(get_db), get_media: bool = Query(default=False)):
# async def get_user_posts(ucode: str, db: AsyncSession = Depends(get_db)):
    # Ensure ucode was provided
    if not ucode:
        raise HTTPException(status_code=400, detail="No link code provided")

    # Query to fetch the user and eager-load the associated posts
    result = await db.execute(select(Post).where(Post.link_code == ucode))
    post   = result.scalars().first()

    if not post:
        raise HTTPException(status_code=404, detail=f"Post with link code [{ucode}] not found")

    if get_media:
        post = PostRead.model_validate(post, from_attributes=True)

    return post




