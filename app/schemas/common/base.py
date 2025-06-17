from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

T = TypeVar("T")

class BaseResponse(GenericModel, Generic[T]):
    code: int = Field(200, description="状态码")
    message: str = Field("Success", description="消息")
    data: Optional[T] = Field(None, description="数据")

    class Config:
        arbitrary_types_allowed = True
