import uuid
from datetime import date, datetime
from typing import List, Optional

import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Column, Field, Relationship, SQLModel

from src.auth import model


class Book(SQLModel, table=True):
    __tablename__="books"
    uid:uuid.UUID= Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )
    title:str
    author:str
    publisher:str
    published_date:date
    page_count:int
    language:str
    user_uid:Optional[uuid.UUID]=Field(default=None, foreign_key="users.uid")
    created_at:datetime=Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime=Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    user: List["model.User"]=Relationship(back_populates="books")
    
    def __repr__(self):
        return f"<Book {self.title}> "
    
