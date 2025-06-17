from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings

# 数据库连接URL，从配置中获取
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# 创建异步数据库引擎
# connect_args={"check_same_thread": False} 仅适用于 SQLite，对于 PostgreSQL 等其他数据库应移除
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=settings.POOL_SIZE,  # 连接池大小
    max_overflow=20,  # 超过连接池大小后允许的最大溢出连接数
    echo=False # 设置为True可以打印SQL语句，方便调试
)

# 创建异步会话本地工厂
# expire_on_commit=False 允许在提交后访问会话中的对象
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 声明性基类，用于定义ORM模型
Base = declarative_base()

# 异步获取数据库会话的依赖注入函数
async def get_db():
    """
    提供一个异步数据库会话给FastAPI的依赖注入系统。
    会话在请求处理完成后会自动关闭。
    """
    async with AsyncSessionLocal() as session:
        yield session
