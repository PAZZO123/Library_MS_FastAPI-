from datetime import datetime, timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from src.celery_task import send_email
from src.config import config as Config
from src.db.main import get_session
from src.db.redis import add_jti_to_blocklist
from src.errors import (InvalidCredentials, InvalidToken, UserAlreadyExists,
                        UserNotFound)

from .dependencies import (AcessTokenBearer, RefreshTokenBearer, RoleChecker,
                           get_current_user)
from .schemas import (EmailModel, PasswordResetConfirmModel,
                      PasswordResetRequestModel, UserBookModel,
                      UserCreateModel, UserLoginModel)
from .service import UserService
from .utils import (create_access_token, create_url_safe_token,
                    decode_url_safe_token, generate_psswd_hash,
                    verify_password)

REFRESH_TOKEN_EXPIRY=2

admin_role_checker=RoleChecker(['admin','user'])
user_service=UserService()

auth_router= APIRouter()
refresh_token_bearer=RefreshTokenBearer()
access_token_bearer=AcessTokenBearer()

@auth_router.post('/send_mail')
async def send_mail(emails:EmailModel):
    emails=emails.addresses
    html="<h1> Welcome to the Bookly app</h1> "
    subject="Welcome to our app "
    send_email.delay(emails, subject, html)
    return {"message":"Email Sent Sucessfully"}
    

@auth_router.post('/signup', status_code=status.HTTP_201_CREATED)
async def create_user_Account(user_data:UserCreateModel,bg_tasks:BackgroundTasks, session:AsyncSession= Depends(get_session)):
    email=user_data.email
    user_exists=await user_service.user_exists(email, session)
    if user_exists:
        raise UserAlreadyExists()
    new_user=await user_service.create_user(user_data,session)
    token=create_url_safe_token({"email":email})
    link=f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"
    
    html_message=f""" <h1> Verify Your Email</h1>
    <p> Please click this link to verify your email </p>
     <a href="{link}">verify email</a> """
    subject="Verify your email "
    emails=[email]
    send_email.delay(emails, subject, html_message)
    return {
        "message":"Account Created! Check email to verify your account.",
        "user":new_user
    }
    
@auth_router.get('/verify/{token}')
async def verify_user_account(token:str, session:AsyncSession=Depends(get_session)):
    token_data=decode_url_safe_token(token)
    user_email=token_data.get('email')
    if user_email:
        user= await user_service.get_user_by_email(user_email,session)
        if not user:
            raise UserNotFound()
        await user_service.update_user(user, {'is_verified':True},session)
        return JSONResponse(
            content={
                "message":"Account was successfuly verified!"
            },
            status_code=status.HTTP_200_OK
        )
    return JSONResponse(
        content={
            "message":"Error occured during Verification"
        },
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

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
    raise InvalidCredentials()
    
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
    raise InvalidToken()

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
    
@auth_router.post('/password-reset-request')
async def password_reset_request(email_data:PasswordResetRequestModel):
    email=email_data.email
    token=create_url_safe_token({"email":email})
    link=f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"
    
    html_message=f""" <h1> Reset your password</h1>
    <p> Please click this link to reset your password </p>
    <a href="{link}">reset password</a> """
    subject="Reset Your Password "
    emails=[email]
    send_email.delay(emails, subject, html_message)
    return JSONResponse(
        content={
        "message":"Please check your email for password reset link."
        },
        status_code=status.HTTP_200_OK
    )

@auth_router.post('/password-reset-confirm/{token}')
async def reset_account_password(token:str,passwords:PasswordResetConfirmModel, session:AsyncSession=Depends(get_session)):
    if passwords.new_password != passwords.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match!")
    token_data=decode_url_safe_token(token)
    user_email=token_data.get('email')
    if user_email:
        user= await user_service.get_user_by_email(user_email,session)
        if not user:
            raise UserNotFound()
        await user_service.update_user(user, {'password_hash':generate_psswd_hash(passwords.new_password)},session)
        return JSONResponse(
            content={
                "message":"Password has been updated successfuly!"
            },
            status_code=status.HTTP_200_OK
        )
    return JSONResponse(
        content={
            "message":"An Error occured during Password reset!  "
        },
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

