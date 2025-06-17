import openai
from app.core.config import settings
from app.schemas.llm import ChatRequest, ChatMessage

class LLMService:
    def __init__(self):
        self.client = openai.AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
        )
        self.deployment_name = settings.AZURE_OPENAI_DEPLOYMENT_NAME

    async def chat(self, request: ChatRequest) -> str:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        try:
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                temperature=0.7,
                max_tokens=800,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None
            )
            return response.choices[0].message.content
        except Exception as e:
            # 可以在这里添加更详细的日志记录
            print(f"Error calling Azure OpenAI API: {e}")
            raise
