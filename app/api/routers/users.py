from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.modules.database.manager import get_db  # Use your backend's DB session
from app.modules.database.metadata import User  # Your backend's models
from typing import List

from app.api.models.api_models import UserCreate, UserRead

router = APIRouter()




@router.post("/users/", response_model=UserRead)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    new_user = User(id=user.id, username=user.username)
    
    db.add(new_user)
    await db.flush()
    await db.commit()
    await db.refresh(new_user)
    
    return new_user


@router.get("/users/", response_model=List[UserRead])
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()

    return users


@router.get("/users/{user_id}", response_model=UserRead)
async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_db)):
    # Query to fetch the user by their ID
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    # If the user is not found, raise a 404 error
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
