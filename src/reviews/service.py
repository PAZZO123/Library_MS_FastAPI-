from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.service import UserService
from src.books.service import BookService
from src.db.models import Reviews

from .schemas import ReviewCreateModel
from fastapi.exceptions import HTTPException
from .schemas import ReviewCreateModel
from fastapi import status
import logging

book_service=BookService()
user_service=UserService()


class ReviewService:
     async def add_review_to_book(self,user_email: str, book_uid: str, review_data:ReviewCreateModel,session: AsyncSession):
         try:
             book=await book_service.get_books(
                 book_uid=book_uid,
                 session=session
             )
             user= await user_service.get_user_by_email(email=user_email, session=session)
             if not book:
                 raise HTTPException(
                     status_code=status.HTTP_404_NOT_FOUND, detail='book not found!'
                 )
             if not user:
                 raise HTTPException(
                     status_code=status.HTTP_404_NOT_FOUND, detail='user not found.'
                 )
             new_review=Reviews(
                 **review_data.model_dump()
             )
             new_review.user=user
             new_review.book=book
             session.add(new_review)
             await session.commit()
             return new_review
         except Exception as e:
             logging.exception(e)
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                 detail='Oops Something went wrong')
             