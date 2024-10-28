from typing import List, Optional
from sqlalchemy import ForeignKey, String, Text, BigInteger, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user"

    uid: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String(32))
    # uid: Mapped[int] = mapped_column(BigInteger)

    posts: Mapped[List["Post"]] = relationship(back_populates="submitter")


    def __repr__(self) -> str:
        return f"<User(id={self.uid}, name='{self.username}')>"

class Post(Base):
    __tablename__ = "post"

    id: Mapped[int] = mapped_column(primary_key=True)
    poster: Mapped[str] = mapped_column(String(32))
    likes: Mapped[int]
    views: Mapped[int]
    source: Mapped[str]
    share_link: Mapped[str]
    file_type: Mapped[str]
    link_code: Mapped[str] = mapped_column(Text)

    submitter_uid = mapped_column(ForeignKey("user.uid"))
    submitter: Mapped[User] = relationship(back_populates="posts")

    # relationship with Comment
    comments: Mapped[List["Comment"]] = relationship(back_populates="post")


    def __repr__(self) -> str:
        return  f"<Post(id={self.id}, poster='{self.poster}', likes={self.likes}, views={self.views}, file_type={self.file_type}, source={self.source}, link_code={self.link_code})>"
    

class Comment(Base):
    __tablename__ = "comment"

    comment_id: Mapped[int] = mapped_column(primary_key=True)  # Primary key
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"))  # Foreign key to Post table
    commenter_username: Mapped[str] = mapped_column(String(32))  # Commenter's username
    comment_text: Mapped[str] = mapped_column(Text)  # Text of the comment
    like_count: Mapped[int] = mapped_column(Integer, default=0)  # Number of likes
    rank: Mapped[int] = mapped_column(Integer, nullable=False) # Rank of the comment

    post: Mapped["Post"] = relationship(back_populates="comments")  # Relationship back to the Post

    def __repr__(self) -> str:
        return f"<Comment(id={self.comment_id}, post_id={self.post_id}, commenter='{self.commenter_username}', likes={self.like_count})>"