from app.crud.user import UserCRUD
from app.schemas.user import UserCreate, UserUpdate
from app.core.common.hashing import verify_password
from app.models.user import User

class UserService:
    """
    用户业务逻辑服务层
    负责处理用户相关的业务逻辑，协调CRUD操作和数据验证。
    """
    def __init__(self, user_crud: UserCRUD):
        self.user_crud = user_crud

    async def get_user(self, user_id: int) -> User | None:
        """
        根据用户ID获取用户。
        """
        return await self.user_crud.get_user(user_id)

    async def get_user_by_email(self, email: str) -> User | None:
        """
        根据邮箱获取用户。
        """
        return await self.user_crud.get_user_by_email(email)

    async def get_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """
        获取用户列表。
        """
        return await self.user_crud.get_users(skip, limit)

    async def create_user(self, user: UserCreate) -> User:
        """
        创建新用户。
        """
        return await self.user_crud.create_user(user)

    async def update_user(self, user_id: int, user_update: UserUpdate) -> User | None:
        """
        更新现有用户。
        """
        return await self.user_crud.update_user(user_id, user_update)

    async def delete_user(self, user_id: int) -> User | None:
        """
        删除用户。
        """
        return await self.user_crud.delete_user(user_id)

    async def authenticate_user(self, email: str, password: str) -> User | None:
        """
        验证用户凭据。
        """
        user = await self.user_crud.get_user_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user
