from typing import Optional, List
from typing_extensions import Annotated
from pydantic import BaseModel, ConfigDict, StringConstraints, computed_field, Field



'''
    POST (Create) Request Models
'''
class UserCreate(BaseModel):
    '''
        Data model for user data CREATION structure validation
    '''
    model_config = ConfigDict(from_attributes=True)
    
    uid: int
    username: Annotated[str, StringConstraints(max_length=32)]


    @classmethod
    def __get_validators__(cls):
        yield cls.trim_username

    @classmethod
    def trim_username(cls, v):
        if len(v.get('username', '')) > 32:
            v['username'] = v['username'][:32]
        return v
    



class PostCreate(BaseModel):
    '''
        Data model for post data CREATION structure validation
    '''
    model_config = ConfigDict(from_attributes=True)

    id: int
    poster: Annotated[str, StringConstraints(max_length=32)]
    likes: int
    views: int
    source: str
    share_link: str
    file_type: str
    link_code: str
    submitter_uid: int


    @classmethod
    def __get_validators__(cls):
        yield cls.trim_username

    @classmethod
    def trim_username(cls, v):
        if len(v.get('poster', '')) > 32:
            v['poster'] = v['poster'][:32]
        return v
    

class PostRead(BaseModel):
    '''
        Data model for post data READ structure validation
    '''
    model_config = ConfigDict(from_attributes=True)

    id: int
    poster: Annotated[str, StringConstraints(max_length=32)]
    likes: int
    views: int
    source: str
    share_link: str
    file_type: str
    link_code: str
    submitter_uid: int

    # media_endpoint: str = Field(default="/posts/media/?media_id={}")
    @computed_field
    def media_endpoint(self) -> str:
        return f"/posts/media/{self.id}/?source={self.source}&type={self.file_type}"

    
'''
    GET (Read) Request Models
'''
class UserRead(BaseModel):
    '''
        Data model for user data READ structure validation
    '''
    model_config = ConfigDict(from_attributes=True)

    uid: int
    username: str
    posts: Optional[List["PostCreate"]] = []



class PaginationMeta(BaseModel):
    current_page: int
    total_pages: int
    next_page: Optional[str]  # URL for the next page, can be None



class PostsPaginationResponse(BaseModel):
    data: List[PostCreate]  # List of posts
    pagination: PaginationMeta  # Pagination metadata



class PostMedia(BaseModel):
    media_id: int
    file_type: str
    link_code: str
    media_content: bytes
