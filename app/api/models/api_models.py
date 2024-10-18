from typing import Optional, List
from typing_extensions import Annotated
from pydantic import BaseModel, ConfigDict, StringConstraints




'''
    POST (Create) Request Models
'''
class UserCreate(BaseModel):
    '''
        Data model for user data CREATION structure validation
    '''
    model_config = ConfigDict(from_attributes=True)
    
    id: int
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
    submitter_id: int


    @classmethod
    def __get_validators__(cls):
        yield cls.trim_username

    @classmethod
    def trim_username(cls, v):
        if len(v.get('poster', '')) > 32:
            v['poster'] = v['poster'][:32]
        return v


'''
    GET (Read) Request Models
'''
class UserRead(BaseModel):
    '''
        Data model for user data READ structure validation
    '''
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    posts: Optional[List["PostCreate"]] = []