from typing import List

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import AcessTokenBearer
from src.db.models import Book as BookModal
from src.books.schemas import Book, BookCreateModel, BookUpdateModel, BookDetailsModel
from src.books.service import BookService
from src.db.main import get_session
from src.auth.dependencies import RoleChecker


book_router=APIRouter()
book_service=BookService()
access_token_bearer=AcessTokenBearer()
admin_role_checker=RoleChecker(['admin','user'])
role_checker=RoleChecker(['admin', 'user'])


@book_router.get("/", response_model=List[Book])
async def get_all_books(session:AsyncSession =Depends(get_session), token_details:dict=Depends(access_token_bearer),_:bool=Depends(role_checker)):
    print(token_details)
    books=await book_service.get_all_books(session)
    return books
@book_router.get("/user/{user_uid}", response_model=List[Book])
async def get_user_books_submissions(user_uid:str, session:AsyncSession =Depends(get_session), token_details:dict=Depends(access_token_bearer),_:bool=Depends(role_checker)):
    print(token_details)
    books=await book_service.get_user_books(session, user_uid)
    return books

@book_router.post("/", status_code=status.HTTP_201_CREATED, response_model=Book)
async def create_a_book(book_data:BookCreateModel,session:AsyncSession =Depends(get_session), token_details:dict=Depends(access_token_bearer),_:bool=Depends(admin_role_checker))->dict:
   user_id=token_details.get('user')['user_uid']
   newbook= await book_service.create_books(book_data,user_id, session)
   return newbook

@book_router.get("/{book_uid}", response_model=BookDetailsModel)
async def get_book(book_uid:str,session:AsyncSession =Depends(get_session), token_details:dict=Depends(access_token_bearer),_:bool=Depends(role_checker))->dict:
  book= await book_service.get_books(book_uid,session)
  if book:
      return book
  else:
     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not Found!")

@book_router.patch("/{book_uid}", response_model=Book, status_code=status.HTTP_200_OK)
async def update_book(book_uid:str, updated_book:BookUpdateModel,session:AsyncSession =Depends(get_session), token_details:dict=Depends(access_token_bearer),_:bool=Depends(admin_role_checker))->dict:
   updated_book_data= await book_service.update_books(book_uid,updated_book, session)
   if updated_book_data:
       return updated_book_data
   else:    
     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book with that id not found")
            

@book_router.delete("/{book_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_uid:str, session:AsyncSession =Depends(get_session), token_details:dict=Depends(access_token_bearer),_:bool=Depends(admin_role_checker)):
   book_to_delete=await book_service.delete_books(book_uid,session)
   if book_to_delete:
       return {"message":"Book Deleted Successfully"}
   else:

     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not Found!")
