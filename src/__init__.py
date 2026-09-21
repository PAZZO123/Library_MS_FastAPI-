from contextlib import asynccontextmanager

from fastapi import FastAPI,status

from src.auth.routes import auth_router
from src.books.routes import book_router
from src.db.main import init_db
from fastapi.responses import JSONResponse
from src.reviews.routes import review_router
from .middleware import register_middleware
from .errors import (
    create_exception_handler,
    InvalidCredentials,
    InvalidToken,
    BookNOtFound,
    UserAlreadyExists,
    UserNotFound,
    InsufficientPermission,
    AccessTokenRequired,
    RefreshTokenRequired,
    RevokedToken,
    AccountNotVerified
    
)




@asynccontextmanager
async def life_span(app:FastAPI):
    print(f"Server is Starting....")
    await init_db()
    yield
    print(f"Server has been stopped")

version="v1"
app =FastAPI(
    title="Bookly",
    description="A REST API for a book review web service",
    version=version
)

register_middleware(app)
app.add_exception_handler(
    UserAlreadyExists,
  create_exception_handler( status_code=status. HTTP_403_FORBIDDEN,
                           initial_detail={
                               "message":"user with email already exists",
                               "resolution":"some message",
                               "error_code":"user_exists"
                               
                           })
)

app.add_exception_handler(
    BookNOtFound,
  create_exception_handler( status_code=status. HTTP_404_NOT_FOUND,
                           initial_detail={
                               "message":"book not found",
                               "resolution":"some message",
                               "error_code":"book not found"
                               
                           })
)

app.add_exception_handler(
    InvalidCredentials,
  create_exception_handler( status_code=status. HTTP_400_BAD_REQUEST,
                           initial_detail={
                               "message":"Invalid email or password",
                                "resolution":"some message",
                               "error_code":"invalid credentials"
                               
                           })
  
)

app.add_exception_handler(
    InvalidToken,
  create_exception_handler( status_code=status. HTTP_401_UNAUTHORIZED,
                           initial_detail={
                               "message":"token is invalid or expired",
                                "resolution":"some message",
                               "error_code":"invalid token"
                               
                           })
)
app.add_exception_handler(
    RevokedToken,
  create_exception_handler( status_code=status. HTTP_401_UNAUTHORIZED,
                           initial_detail={
                               "message":"Token is invalid or revoked",
                               "resolution":"some message",
                               "error_code":"token revoked"
                               
                           })
)

app.add_exception_handler(
    AccessTokenRequired,
  create_exception_handler( status_code=status. HTTP_403_FORBIDDEN,
                           initial_detail={
                               "message":"Please provide valid acess token",
                                "resolution":"some message",
                               "error_code":"access_token_required"
                               
                           })
)

app.add_exception_handler(
    InsufficientPermission,
  create_exception_handler( status_code=status. HTTP_403_FORBIDDEN,
                           initial_detail={
                               "message":"user is not allowed to perform this operation",
                                 "resolution":"some message",
                               "error_code":"not_allowed"
                               
                           })
)
app.add_exception_handler(
    RefreshTokenRequired,
  create_exception_handler( status_code=status. HTTP_403_FORBIDDEN,
                           initial_detail={
                               "message":"Please provide the valid reresh token",
                               "resolution":"some message",
                               "error_code":"refresh_token_required"
                               
                           })
)

app.add_exception_handler(
    AccountNotVerified,
  create_exception_handler( status_code=status. HTTP_403_FORBIDDEN,
                           initial_detail={
                               "message":"Please verify your account first",
                               "resolution":"check your email and verify account",
                               "error_code":"account_not_verified"
                               
                           })
)
@app.exception_handler(500)
async def  internal_server_error(request, exc):
    return JSONResponse(
        content={
            "message":"OOPs something went wrong",
            "error_code":"server_error"
        },
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
app.include_router(book_router, prefix=f"/api/{version}/books", tags=['books'])
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=['auth'])
app.include_router(review_router, prefix=f"/api/{version}/reviews", tags=['reviews'])