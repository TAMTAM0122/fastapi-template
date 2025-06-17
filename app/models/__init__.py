# 从核心数据库模块导入Base，它是所有ORM模型的基础
from app.core.database import Base
# 导入定义的ORM模型
from .user import User
from .log import Log
