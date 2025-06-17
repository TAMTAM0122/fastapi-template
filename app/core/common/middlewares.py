import time
import traceback
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.core.common.logger import logger
from app.crud.log import LogCRUD
from app.schemas.log import LogCreate
from app.core.database import AsyncSessionLocal # 导入AsyncSessionLocal

class LogMiddleware(BaseHTTPMiddleware):
    """
    自定义日志中间件，用于记录HTTP请求和捕获未处理的异常。
    """
    async def dispatch(self, request: Request, call_next):
        """
        处理传入的HTTP请求，记录请求信息，并捕获异常。
        - **request**: Starlette Request 对象。
        - **call_next**: 下一个中间件或路由处理函数。
        """
        start_time = time.time()
        response = Response("Internal Server Error", status_code=500) # 默认响应，以防发生错误

        try:
            response = await call_next(request)
        except Exception as e:
            # 捕获并记录异常到数据库
            # 在中间件中获取新的异步会话，以确保日志记录的独立性
            async with AsyncSessionLocal() as db:
                try:
                    log_crud = LogCRUD(db)
                    log_entry = LogCreate(
                        level="ERROR",
                        message=f"Unhandled exception: {e}",
                        pathname=request.url.path,
                        lineno=0, # 中间件中难以获取精确行号
                        funcname="dispatch",
                        exc_info=traceback.format_exc(),
                        stack_info=None # 堆栈信息通常包含在exc_info中
                    )
                    await log_crud.create_log(log_entry) # 异步调用创建日志
                    logger.error(f"Unhandled exception during request to {request.url.path}: {e}", exc_info=True)
                except Exception as log_e:
                    logger.error(f"Failed to log exception to database: {log_e}", exc_info=True)
            raise e # 重新抛出异常，以便FastAPI可以继续处理错误
        finally:
            process_time = time.time() - start_time
            logger.info(f"Request: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.4f}s")
        return response
