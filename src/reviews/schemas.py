from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import uuid


class ReviewModel(BaseModel):
    uid:uuid.UUID
    review_text:str
    rating: int=Field(lt=5)
    user_uid:Optional[uuid.UUID]
    book_uid:Optional[uuid.UUID]
    created_at:datetime
    updated_at: datetime
    
class ReviewCreateModel:
    rating:int=Field(lt=5)
    reviw_text:str