import logging
import sys
import asyncio
import threading
import traceback

from app.crud.log import LogCRUD
from app.schemas.log import LogCreate
from app.core.database import AsyncSessionLocal # 导入AsyncSessionLocal

class DatabaseHandler(logging.Handler):
    def emit(self, record):
        # 在单独的线程中运行异步数据库操作
        def _run_async_db_log():
            async def _log_to_db():
                async with AsyncSessionLocal() as db:
                    try:
                        log_crud = LogCRUD(db)
                        log_entry = LogCreate(
                            level=record.levelname,
                            message=self.format(record), # 使用格式化后的消息
                            pathname=record.pathname,
                            lineno=record.lineno,
                            funcname=record.funcName,
                            exc_info=self.format_exception(record.exc_info) if record.exc_info else None,
                            stack_info=record.stack_info
                        )
                        await log_crud.create_log(log_entry)
                    except Exception as e:
                        # 如果日志记录到数据库失败，则打印到控制台
                        print(f"Failed to log to database: {e}", file=sys.stderr)
                        traceback.print_exc(file=sys.stderr)

            # 确保在新的事件循环中运行异步函数
            # 如果当前线程没有事件循环，则创建一个
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            if loop.is_running():
                # 如果事件循环正在运行，则使用run_coroutine_threadsafe
                # 这通常发生在FastAPI的主线程中
                asyncio.run_coroutine_threadsafe(_log_to_db(), loop)
            else:
                # 如果事件循环没有运行，则直接运行
                loop.run_until_complete(_log_to_db())

        # 启动一个新线程来执行数据库日志记录
        thread = threading.Thread(target=_run_async_db_log)
        thread.start()

    def format_exception(self, exc_info):
        if exc_info:
            return ''.join(traceback.format_exception(*exc_info))
        return None

def setup_logging():
    db_handler = DatabaseHandler()
    db_handler.setLevel(logging.WARNING) # 设置数据库处理器只记录ERROR及以上级别的日志

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            db_handler # 添加自定义的数据库处理器
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()
