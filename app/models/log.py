from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    level = Column(String, index=True)
    message = Column(Text)
    pathname = Column(String)
    lineno = Column(Integer)
    funcname = Column(String)
    exc_info = Column(Text, nullable=True)
    stack_info = Column(Text, nullable=True)
