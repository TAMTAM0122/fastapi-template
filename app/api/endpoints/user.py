from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_injector import Injected

from app.schemas.user import UserCreate, UserResponse
from app.schemas.common.base import BaseResponse
from app.services.user import UserService

router = APIRouter()

@router.post(
    "/",
    response_model=BaseResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="创建新用户",
    description="通过提供的用户数据创建一个新用户，如果邮箱已注册则返回错误。"
)
async def create_user(user: UserCreate, user_service: UserService = Injected(UserService)):
    """
    创建新用户。
    - **user**: 用户创建请求体。
    - **user_service**: 用户服务依赖。
    """
    db_user = await user_service.get_user_by_email(email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    created_user = await user_service.create_user(user=user)
    return BaseResponse(data=created_user)

@router.get(
    "/{user_id}",
    response_model=BaseResponse[UserResponse],
    summary="根据ID获取用户",
    description="根据用户ID获取单个用户的信息。"
)
async def read_user(user_id: int, user_service: UserService = Injected(UserService)):
    """
    根据用户ID获取用户。
    - **user_id**: 用户的唯一标识符。
    - **user_service**: 用户服务依赖。
    """
    db_user = await user_service.get_user(user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return BaseResponse(data=db_user)

@router.get(
    "/",
    response_model=BaseResponse[list[UserResponse]],
    summary="获取用户列表",
    description="获取所有用户的列表，支持分页。"
)
async def read_users(skip: int = 0, limit: int = 100, user_service: UserService = Injected(UserService)):
    """
    获取用户列表。
    - **skip**: 跳过的记录数。
    - **limit**: 返回的最大记录数。
    - **user_service**: 用户服务依赖。
    """
    users = await user_service.get_users(skip=skip, limit=limit)
    return BaseResponse(data=users)
