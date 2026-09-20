import uuid
from datetime import datetime

from pydantic import BaseModel, Field
from typing import List
from src.books.schemas import Book
from src.reviews.schemas import ReviewModel


class UserCreateModel(BaseModel):
    username:str=Field(max_length=8 )
    email:str=Field(max_length=40)
    password:str=Field(min_length=6)
    first_name:str=Field(max_length=25)
    last_name:str=Field(max_length=25)
    
    
class UserModel(BaseModel):
    uid:uuid.UUID
    username:str
    email: str
    first_name:str
    last_name:str
    password_hash:str=Field(exclude=True)
    is_verified:bool=False
    created_at:datetime
    updated_at: datetime
    
class UserBookModel(UserModel):
    books:List[Book]
    reviews:List[ReviewModel]
    
class UserLoginModel(BaseModel):
    email:str=Field(max_length=40)
    password:str=Field(min_length=6)