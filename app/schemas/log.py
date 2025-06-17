from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class LogBase(BaseModel):
    level: str
    message: str
    pathname: str
    lineno: int
    funcname: str
    exc_info: Optional[str] = None
    stack_info: Optional[str] = None

class LogCreate(LogBase):
    pass

class LogResponse(LogBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True
