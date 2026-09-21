from typing import Any, Callable
from fastapi.requests import Request
from fastapi.responses import JSONResponse

class BooklyException(Exception):
    " " " This is the base class for all bookly errors"""
    pass
    
    
class InvalidToken(BooklyException):
    """ User has providede invalid or expired token"""
    pass

    
class RevokedToken(BooklyException):
    """ User has providede that has been revoked"""
    pass

class AccessTokenRequired(BooklyException):
    """ User has provided a refresh token when acess token required"""
    pass

class RefreshTokenRequired(BooklyException):
    """ User has provided access token when a refresh token required"""
    pass
class UserAlreadyExists(BooklyException):
    """ User provided email for a user who exists during sign up"""
    pass

class InvalidCredentials(BooklyException):
    """ User provided email or password that aren't vailid during  login """
    pass
class InsufficientPermission(BooklyException):
    """ User does not have the necessary permission to perform this action"""
    pass

class BookNOtFound(BooklyException):
    """ the requested book does not found."""
    pass
class UserNotFound(BooklyException):
    """ User with the specified id doen't exist"""
    pass
class AccountNotVerified(BooklyException):
      """ Account not yet verified"""
      pass

def create_exception_handler(status_code:int,initial_detail:Any)->Callable[[Request, Exception], JSONResponse]:
    async def exception_handler(request: Request, exc:BooklyException):
        return JSONResponse(
            content=initial_detail,
            status_code=status_code
        )
    return exception_handler
    