from sqlalchemy.ext.asyncio import AsyncSession
from app.models.log import Log
from app.schemas.log import LogCreate

class LogCRUD:
    """
    日志数据访问层 (CRUD)
    负责与日志相关的数据库操作。
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_log(self, log: LogCreate) -> Log:
        """
        创建新的日志条目。
        """
        db_log = Log(**log.dict())
        self.db.add(db_log)
        await self.db.commit()
        await self.db.refresh(db_log)
        return db_log
