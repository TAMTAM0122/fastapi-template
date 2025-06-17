from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta
from injector import Injector
from fastapi_injector import attach_injector, Injected # 修改导入

from app.api.endpoints import user as user_endpoints
from app.api.endpoints import llm as llm_endpoints
from app.core.config import settings
from app.core.database import engine, Base
from app.core.common.security import create_access_token, get_current_user
from app.core.common.logger import setup_logging
from app.core.common.middlewares import LogMiddleware
from app.schemas.token import Token
from app.schemas.common.base import BaseResponse
from app.services.user import UserService
from app.models.user import User
from app.core.modules import ApplicationModule # 导入ApplicationModule

# 设置日志
setup_logging()

# 初始化FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="一个基于FastAPI的异步项目模板，包含用户认证、日志记录和分层架构。",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 初始化 FastAPIInjector
attach_injector(app=app, injector=Injector([ApplicationModule()])) # 修改初始化方式

@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        # 使用 run_sync 来在异步 contexts 中执行同步的 create_all 操作
        await conn.run_sync(Base.metadata.create_all)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True, # 允许发送凭据（如cookies, HTTP认证）
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有HTTP头
)

# 添加自定义日志中间件
app.add_middleware(LogMiddleware)

# 公共路由 (无需认证)
@app.post(
    "/token",
    response_model=BaseResponse[Token],
    summary="获取访问令牌",
    description="通过用户名和密码获取JWT访问令牌。"
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Injected(UserService) # 使用Injected注入UserService
):
    """
    用户登录并获取JWT令牌。
    - **form_data**: OAuth2密码请求表单数据（用户名和密码）。
    - **user_service**: 用户服务依赖。
    """
    user = await user_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return BaseResponse(data={"access_token": access_token, "token_type": "bearer"})

@app.get(
    "/",
    summary="根路径",
    description="欢迎访问FastAPI项目。"
)
async def root():
    """
    根路径，返回欢迎消息。
    """
    return {"message": "Welcome to FastAPI Project!"}

# 认证路由 (需要Token验证)
# 所有包含在此路由中的接口都需要通过get_current_user进行认证
api_router = APIRouter(dependencies=[Depends(get_current_user)])
api_router.include_router(user_endpoints.router, prefix="/users", tags=["users"])
api_router.include_router(llm_endpoints.router, prefix="/llm", tags=["llm"]) # 添加llm路由 (仅包含需要认证的接口)

# 将认证路由包含到主应用中
app.include_router(api_router)

# 将公共路由包含到主应用中 (无需认证)
app.include_router(llm_endpoints.public_router, prefix="/llm", tags=["llm-public"])
