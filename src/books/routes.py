from typing import List

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from src.books.models import Book as BookModal
from src.books.schemas import Book, BookCreateModel, BookUpdateModel
from src.books.service import BookService
from src.db.main import get_session

book_router=APIRouter()
book_service=BookService()

@book_router.get("/", response_model=List[Book])
async def get_all_books(session:AsyncSession =Depends(get_session)):
    books=await book_service.get_all_books(session)
    return books

@book_router.post("/", status_code=status.HTTP_201_CREATED, response_model=Book)
async def create_a_book(book_data:BookCreateModel,session:AsyncSession =Depends(get_session))->dict:
   newbook= await book_service.create_books(book_data, session)
   return newbook

@book_router.get("/{book_uid}", response_model=Book)
async def get_book(book_uid:str,session:AsyncSession =Depends(get_session))->dict:
  book= await book_service.get_books(book_uid,session)
  if book:
      return book
  else:
     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not Found!")

@book_router.patch("/{book_uid}", response_model=Book, status_code=status.HTTP_200_OK)
async def update_book(book_uid:str, updated_book:BookUpdateModel,session:AsyncSession =Depends(get_session))->dict:
   updated_book_data= await book_service.update_books(book_uid,updated_book, session)
   if updated_book_data:
       return updated_book_data
   else:    
     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book with that id not found")
            

@book_router.delete("/{book_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_uid:str, session:AsyncSession =Depends(get_session)):
   book_to_delete=await book_service.delete_books(book_uid,session)
   if book_to_delete:
       return {"message":"Book Deleted Successfully"}
   else:

     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not Found!")
