from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from .model import User
from .schemas import UserCreateModel
from .utils import generate_psswd_hash


class UserService:
    async def get_user_by_email(self, email:str, session:AsyncSession):
        statement=select(User).where(User.email == email)
        result= await session.exec(statement)
        book=result.first()
        return book
    
    async def user_exists(self,email:str, session:AsyncSession):
        user=await self.get_user_by_email(email, session)
        if user is None:
            return False
        else:
            return True
        
    async def create_user(self, user_data:User, session:AsyncSession):
        user_data_dict=user_data.model_dump()
        
        new_user=User(
            **user_data_dict
        )
        new_user.password_hash=generate_psswd_hash(user_data_dict['password'])
        new_user.role='user'
        session.add(new_user)
        await session.commit()
        
        return new_user