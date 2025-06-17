import os
import httpx
import asyncio
import logging
from typing import List, Tuple
from urllib.parse import urlparse

from openai import AzureOpenAI,AsyncAzureOpenAI
from app.core.config import settings
from app.core.common.logger import logger

class WebSummarizerService:
    def __init__(self):
        self.http_client = httpx.AsyncClient()
        self.google_api_key = settings.GOOGLE_API_KEY
        self.google_cse_id = settings.GOOGLE_CSE_ID
        self.jinaai_api_key = settings.JINAAI_API_KEY

        self.azure_openai_client = AsyncAzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_version=settings.AZURE_OPENAI_API_VERSION
        )
        self.azure_openai_deployment_name = settings.AZURE_OPENAI_DEPLOYMENT_NAME

    async def search_urls_for_query(self, urls: List[str], query: str) -> List[str]:
        """
        在指定的URL列表中，通过Google Custom Search API搜索用户的问题，并返回相关链接。
        """
        if not urls:
            return []

        # 构建 site: 参数
        site_queries = [f"site:{urlparse(url).netloc}" for url in urls]
        combined_site_query = " OR ".join(site_queries)
        search_query = f"{query} {combined_site_query}"

        google_search_url = "https://serpapi.com/search"
        params = {
            "api_key": self.google_api_key,
            "engine": "google",
            "q": search_query,
            "num": 10, # 可以根据需要调整返回结果的数量
            "filter":1
        }

        try:
            logger.info(f"Calling Google Custom Search API with query: {search_query}")
            response = await self.http_client.get(google_search_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            links = []
            for item in data["organic_results"]:
                links.append(item["link"])
            logger.info(f"Found {len(links)} links from Google Search.")
            return links
        except httpx.HTTPStatusError as e:
            logger.error(f"Google Search API HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Google Search API request error: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred during Google Search: {e}")
            raise

    async def extract_content_from_links(self, links: List[str]) -> List[str]:
        """
        使用JinaAI内容提取服务从给定的链接中提取主要内容。
        """
        extracted_contents = []
        jinaai_base_url = "https://r.jina.ai/" # JinaAI Reader API
        MAX_RETRIES = 3
        RETRY_DELAY_SECONDS = 2 # 重试间隔

        for link in links:
            for attempt in range(MAX_RETRIES):
                try:
                    logger.info(f"Attempt {attempt + 1} to extract content from link: {link} using JinaAI")
                    jina_url = f"{jinaai_base_url}{link}"
                    response = await self.http_client.get(jina_url, headers={"Authorization": f"Bearer {self.jinaai_api_key}"})
                    response.raise_for_status()
                    extracted_contents.append(response.text)
                    logger.info(f"Successfully extracted content from {link} on attempt {attempt + 1}")
                    break # 成功后跳出重试循环
                except httpx.HTTPStatusError as e:
                    logger.warning(f"JinaAI content extraction HTTP error for {link} (Attempt {attempt + 1}/{MAX_RETRIES}): {e.response.status_code} - {e.response.text}")
                    if attempt < MAX_RETRIES - 1:
                        await asyncio.sleep(RETRY_DELAY_SECONDS) # 等待后重试
                    else:
                        logger.error(f"Failed to extract content from {link} after {MAX_RETRIES} attempts due to HTTP error.")
                except httpx.RequestError as e:
                    logger.warning(f"JinaAI content extraction request error for {link} (Attempt {attempt + 1}/{MAX_RETRIES}): {e}")
                    if attempt < MAX_RETRIES - 1:
                        await asyncio.sleep(RETRY_DELAY_SECONDS) # 等待后重试
                    else:
                        logger.error(f"Failed to extract content from {link} after {MAX_RETRIES} attempts due to request error.")
                except Exception as e:
                    logger.warning(f"An unexpected error occurred during JinaAI extraction for {link} (Attempt {attempt + 1}/{MAX_RETRIES}): {e}")
                    if attempt < MAX_RETRIES - 1:
                        await asyncio.sleep(RETRY_DELAY_SECONDS) # 等待后重试
                    else:
                        logger.error(f"Failed to extract content from {link} after {MAX_RETRIES} attempts due to unexpected error.")
        
        logger.info(f"Successfully extracted content from {len(extracted_contents)} out of {len(links)} links.")
        return extracted_contents

    async def summarize_combined_content(self, combined_content: str, query: str) -> str:
        """
        使用Azure OpenAI服务根据合并内容和用户问题进行总结。
        """
        if not combined_content:
            return "没有足够的内容进行总结。"

        prompt = (
            f"以下是关于 '{query}' 的参考文档内容：\n\n"
            f"{combined_content}\n\n"
            f"请根据上述参考文档，详细回答问题：'{query}'。如果文档中没有直接答案，请说明。"
        )

        messages = [
            {"role": "system", "content": "你是一个专业的总结助手，能够根据提供的文档和问题进行准确、简洁的总结。"},
            {"role": "user", "content": prompt}
        ]

        try:
            logger.info(f"Calling Azure OpenAI for summarization with query: {query}")
            response = await self.azure_openai_client.chat.completions.create(
                model=self.azure_openai_deployment_name,
                messages=messages,
                temperature=0.7, # 可以调整
                max_tokens=1000 # 可以调整
            )
            summary = response.choices[0].message.content
            logger.info("Successfully received summary from Azure OpenAI.")
            return summary
        except Exception as e:
            logger.error(f"Azure OpenAI API error: {e}")
            raise

    async def process_request(self, urls: List[str], query: str) -> str:
        """
        协调整个流程：搜索、提取内容并总结。
        """
        logger.info(f"Starting process for URLs: {urls} with query: {query}")
        
        # 1. 在指定URL中搜索问题，获取相关链接
        relevant_links = await self.search_urls_for_query(urls, query)
        if not relevant_links:
            logger.warning("No relevant links found from Google Search.")
            return "未能找到与您问题相关的任何内容。"

        # 2. 从相关链接中提取内容
        extracted_contents = await self.extract_content_from_links(relevant_links)
        
        # 过滤掉空内容
        extracted_contents = [content for content in extracted_contents if content.strip()]
        if not extracted_contents:
            logger.warning("No content could be extracted from the relevant links.")
            return "未能从找到的链接中提取到有效内容。"

        # 3. 合并所有提取到的内容
        combined_content = "\n\n---\n\n".join(extracted_contents)
        
        # 4. 使用LLM总结合并后的内容
        summary = await self.summarize_combined_content(combined_content, query)
        
        logger.info("Process completed successfully.")
        return summary
