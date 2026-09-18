from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.main import get_session
from src.db.redis import add_jti_to_blocklist

from .dependencies import (AcessTokenBearer, RefreshTokenBearer, RoleChecker,
                           get_current_user)
from .schemas import UserBookModel, UserCreateModel, UserLoginModel, UserModel
from .service import UserService
from .utils import create_access_token, decode_token, verify_password

REFRESH_TOKEN_EXPIRY=2

admin_role_checker=RoleChecker(['admin','user'])
user_service=UserService()

auth_router= APIRouter()
refresh_token_bearer=RefreshTokenBearer()
access_token_bearer=AcessTokenBearer()

@auth_router.post('/signup', status_code=status.HTTP_201_CREATED, response_model=UserModel)
async def create_user_Account(user_data:UserCreateModel, session:AsyncSession= Depends(get_session)):
    email=user_data.email
    user_exists=await user_service.user_exists(email, session)
    if user_exists:
        raise HTTPException( status_code=status.HTTP_403_FORBIDDEN, detail="User with the same email already exists")
    new_user=await user_service.create_user(user_data,session)
    return new_user

@auth_router.post('/login')
async def login_users(login_data:UserLoginModel, session: AsyncSession=Depends(get_session)):
    email=login_data.email
    password=login_data.password
    
    user=await user_service.get_user_by_email(email, session)
    if user is not None:
        password_valid=verify_password(password, user.password_hash)
        if password_valid:
            access_token=create_access_token(
                user_data={
                'email':user.email,
                'user_uid':str(user.uid)
            })
            
            refresh_token=create_access_token(
                user_data={
                'email':user.email,
                'user_uid':str(user.uid),
                "role":user.role
            },
            refresh=True,
            expiry=timedelta(days=REFRESH_TOKEN_EXPIRY)
                                               )
            return JSONResponse(
                content={
                    "message":"Login Sucessful",
                    "access_token":access_token,
                    "refresh_token":refresh_token,
                    "user":{
                        "email":user.email,
                        "user_uid":str(user.uid)
                    }
                }
            )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,detail="Email or Password is Invalid"
    )
    
@auth_router.get('/refresh_token')
async def get_new_access_token(token_details:dict=Depends(refresh_token_bearer)):
    expiry_date=token_details['exp']
    print(expiry_date)
    if datetime.fromtimestamp(expiry_date) > datetime.now():
        new_acces_token=create_access_token(
            user_data=token_details['user']
        )
        return JSONResponse(content={
            "access_token":new_acces_token
        })
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or Expired token")

@auth_router.get('/me', response_model=UserBookModel)
async def get_current_user(user = Depends(get_current_user),_:bool=Depends(admin_role_checker)):
    return user
    
    
@auth_router.get('/logout')
async def revoke_token(token_details:dict=Depends(access_token_bearer)):
    jti=token_details['jti']
    await add_jti_to_blocklist(jti)
    
    return JSONResponse(
        content={
            "message":"Logged out successfuly!"
        },
        status_code=status.HTTP_200_OK
    )