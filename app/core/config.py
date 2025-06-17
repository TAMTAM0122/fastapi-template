import os
from dotenv import load_dotenv
from pydantic import Field # 导入 Field
from pydantic_settings import BaseSettings # 导入 BaseSettings

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Project"
    PROJECT_VERSION: str = "1.0.0"

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    POOL_SIZE: int = int(os.getenv("POOL_SIZE", 10)) # Default pool size

    # Azure OpenAI 配置
    AZURE_OPENAI_API_KEY: str = Field(..., env="AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT: str = Field(..., env="AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    AZURE_OPENAI_DEPLOYMENT_NAME: str = Field(..., env="AZURE_OPENAI_DEPLOYMENT_NAME")

    # Google Custom Search API
    GOOGLE_API_KEY: str = Field(..., env="GOOGLE_API_KEY")
    GOOGLE_CSE_ID: str = Field(..., env="GOOGLE_CSE_ID")

    # JinaAI Content Extraction API
    JINAAI_API_KEY: str = Field(..., env="JINAAI_API_KEY")

settings = Settings()
