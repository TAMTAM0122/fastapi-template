from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.common.hashing import get_password_hash

class UserCRUD:
    """
    用户数据访问层 (CRUD)
    负责与用户相关的数据库操作。
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user(self, user_id: int) -> User | None:
        """
        根据用户ID获取单个用户。
        """
        result = await self.db.execute(select(User).filter(User.id == user_id))
        return result.scalars().first()

    async def get_user_by_email(self, email: str) -> User | None:
        """
        根据邮箱获取单个用户。
        """
        result = await self.db.execute(select(User).filter(User.email == email))
        return result.scalars().first()

    async def get_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """
        获取用户列表。
        """
        result = await self.db.execute(select(User).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create_user(self, user: UserCreate) -> User:
        """
        创建新用户。
        """
        hashed_password = get_password_hash(user.password)
        db_user = User(email=user.email, hashed_password=hashed_password)
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def update_user(self, user_id: int, user_update: UserUpdate) -> User | None:
        """
        更新现有用户。
        """
        db_user = await self.get_user(user_id)
        if not db_user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            if key == "password":
                db_user.hashed_password = get_password_hash(value)
            else:
                setattr(db_user, key, value)
        
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def delete_user(self, user_id: int) -> User | None:
        """
        删除用户。
        """
        db_user = await self.get_user(user_id)
        if not db_user:
            return None
        await self.db.delete(db_user)
        await self.db.commit()
        return db_user
