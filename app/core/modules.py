from injector import Module, provider, singleton
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.user import UserCRUD
from app.crud.log import LogCRUD
from app.services.user import UserService
from app.services.websummary import WebSummarizerService # 导入 WebSummarizerService
from app.services.llm import LLMService

class ApplicationModule(Module):
    """
    FastAPI 应用程序的依赖注入模块。
    定义了如何提供 CRUD 和 Service 类的实例。
    """
    @singleton
    @provider
    def provide_db_session(self) -> AsyncSession:
        """
        提供数据库会话。
        """
        # 这里我们直接返回 get_db 的结果，FastAPIInjector 会处理其作为依赖注入函数。
        # 实际的会话管理（yield）会在 FastAPI 的 Depends 机制中处理。
        # 在这里，我们只是声明如何获取一个 AsyncSession 实例。
        # 注意：FastAPIInjector 会在请求生命周期内管理这个会话。
        return get_db()
    
    @singleton
    @provider
    def provide_user_crud(self, db: AsyncSession) -> UserCRUD:
        """
        提供 UserCRUD 实例。
        """
        return UserCRUD(db)

    @provider
    def provide_user_service(self, user_crud: UserCRUD) -> UserService:
        """
        提供 UserService 实例。
        """
        return UserService(user_crud)

    @singleton
    @provider
    def provide_log_crud(self, db: AsyncSession) -> LogCRUD:
        """
        提供 LogCRUD 实例。
        """
        return LogCRUD(db)

    @provider
    def provide_llm_service(self) -> LLMService: # LLMService 不再依赖 db
        """
        提供 LLMService 实例。
        """
        return LLMService()

    @provider
    def provide_web_summarizer_service(self) -> WebSummarizerService:
        """
        提供 WebSummarizerService 实例。
        """
        return WebSummarizerService()
