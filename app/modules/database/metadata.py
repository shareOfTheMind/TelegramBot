from typing import List, Optional
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32), unique=True)

    posts: Mapped[List["Post"]] = relationship(back_populates="submitter")


    def __repr__(self) -> str:
        return f"<User(id={self.id}, name='{self.name}')>"

class Post(Base):
    __tablename__ = "post"

    id: Mapped[int] = mapped_column(primary_key=True)
    poster: Mapped[str] = mapped_column(String(32))
    likes: Mapped[int]
    views: Mapped[int]
    share_link: Mapped[str] = mapped_column(unique=True)
    s3_link: Mapped[str] = mapped_column(unique=True)
    is_video: Mapped[bool]

    submitter_id = mapped_column(ForeignKey("user.id"))
    submitter: Mapped[User] = relationship(back_populates="posts")


    def __repr__(self) -> str:
        return  f"<Post(id={self.id}, poster='{self.poster}', likes={self.likes}, views={self.views}, is_video={self.is_video})>"