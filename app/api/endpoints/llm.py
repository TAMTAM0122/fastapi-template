from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_injector import Injected # 导入Injected
from app.core.common.security import get_current_user
from app.schemas.llm import ChatRequest, ChatResponse, SummarizeRequest, SummarizeResponse
from app.schemas.common.base import BaseResponse
from app.services.websummary import WebSummarizerService # 导入 WebSummarizerService
from app.services.llm import LLMService
from app.core.common.logger import logger

router = APIRouter() # 用于需要认证的接口
public_router = APIRouter() # 用于不需要认证的接口

@router.post(
    "/chat",
    response_model=BaseResponse[ChatResponse],
    summary="与大模型进行对话",
    description="发送消息给Azure OpenAI大模型并获取回复。"
)
async def chat_with_llm(
    request: ChatRequest,
    llm_service: LLMService = Injected(LLMService), # 使用Injected注入LLMService
    current_user: dict = Depends(get_current_user) # 确保用户已认证
):
    """
    与大模型进行对话。
    - **request**: 包含对话消息的请求体。
    - **llm_service**: LLM服务依赖。
    """
    try:
        response_content = await llm_service.chat(request)
        return BaseResponse(data=ChatResponse(response=response_content))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LLM服务错误: {e}"
        )

@public_router.post( # 使用 public_router
    "/summarize_urls_with_query",
    response_model=BaseResponse[SummarizeResponse],
    summary="根据网址和问题总结内容",
    description="在指定网址内搜索问题，提取内容，并使用Azure OpenAI大模型进行总结。"
)
async def summarize_urls_with_query(
    request: SummarizeRequest,
    web_summarizer_service: WebSummarizerService = Injected(WebSummarizerService), # 注入 WebSummarizerService
    # 移除 current_user 依赖，使此接口无需认证
):
    """
    根据网址和问题总结内容。
    - **request**: 包含网址列表和问题的请求体。
    - **web_summarizer_service**: 网页总结服务依赖。
    """
    try:
        summary_content = await web_summarizer_service.process_request(request.urls, request.query)
        return BaseResponse(data=SummarizeResponse(summary=summary_content))
    except HTTPException:
        raise # 重新抛出已处理的HTTPException
    except Exception as e:
        logger.error(f"Web Summarizer Service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"网页总结服务错误: {e}"
        )
