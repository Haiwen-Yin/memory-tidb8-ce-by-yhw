#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TiDB Memory System - OpenAI Embedding Provider
===============================================

OpenAI官方Embedding API适配器
支持text-embedding-ada-002和text-embedding-3-small等模型

Author: Haiwen Yin (胖头鱼 🐟 / yhw)
Version: 0.2.0
"""

import requests
import numpy as np
from .base_provider import BaseEmbeddingProvider, register_provider


@register_provider
class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """OpenAI Embeddings API适配器
    
    使用OpenAI官方API获取文本嵌入向量。
    支持多种模型：
    - text-embedding-ada-002 (1536维)
    - text-embedding-3-small (1536维, 更经济)
    - text-embedding-3-large (3072维, 更高精度)
    
    Usage:
        >>> from embedding_providers.openai import OpenAIEmbeddingProvider
        >>> provider = OpenAIEmbeddingProvider(
        ...     api_key="sk-your-key-here",
        ...     model_id="text-embedding-3-small"
        ... )
    """
    
    def __init__(self, api_key: str = "", 
                 model_name: str = "text-embedding-ada-002",
                 dimensions: int = 1536,
                 endpoint: str = "https://api.openai.com/v1/embeddings",
                 model_id: str = None,
                 max_input_length: int = 8191):
        """初始化OpenAI Provider
        
        Args:
            api_key: OpenAI API密钥（必需）
            model_name: OpenAI模型名称
            dimensions: 向量维度（取决于模型版本）
            endpoint: OpenAI API端点
            model_id: 具体使用的模型ID，默认使用model_name
            max_input_length: 最大输入长度限制
        """
        if not api_key:
            raise ValueError("OpenAI Provider需要API密钥")
        
        super().__init__(
            model_name=model_name,
            dimensions=dimensions,
            provider_type="openai",
            endpoint=endpoint,
            api_key=api_key,
            model_id=model_id or model_name,
            max_input_length=max_input_length
        )
    
    def get_embedding(self, text: str) -> np.ndarray:
        """从OpenAI API获取embedding
        
        Args:
            text: 需要生成embedding的文本
            
        Returns:
            numpy array格式的向量
            
        Raises:
            RuntimeError: API调用失败或认证错误
            ValueError: 输入为空
        """
        if not text or not text.strip():
            raise ValueError("输入文本不能为空")
        
        truncated_text = self.truncate_text(text)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_id,
            "input": truncated_text,
            "encoding_format": "float" if hasattr(np.array([1.0]), '__array_interface__') else None
        }
        
        try:
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                error_detail = response.json().get("error", {}).get("message", response.text)
                raise RuntimeError(f"OpenAI API错误 ({response.status_code}): {error_detail}")
            
            data = response.json()
            
            if "data" not in data or len(data["data"]) == 0:
                raise RuntimeError("OpenAI响应格式异常")
            
            embedding_list = data["data"][0]["embedding"]
            return np.array(embedding_list, dtype=np.float32)
            
        except requests.exceptions.ConnectionError:
            raise RuntimeError(f"无法连接到OpenAI API: {self.endpoint}")
        except Exception as e:
            if "Invalid API key" in str(e):
                raise RuntimeError("OpenAI API密钥无效")
            raise RuntimeError(f"OpenAI获取embedding失败: {str(e)}")
    
    def get_model_info(self) -> dict:
        """获取模型信息"""
        return {
            "model_name": self.model_name,
            "dimensions": self.dimensions,
            "provider": "openai",
            "max_input_length": self.max_input_length,
            "endpoint": self.endpoint,
            "pricing_note": "按token计费，ada-002约$0.0001/1K tokens"
        }
    
    def is_available(self) -> bool:
        """检查OpenAI服务是否可用"""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            response = requests.head(
                "https://api.openai.com/v1/models",
                headers=headers,
                timeout=5
            )
            return response.status_code in [200, 403]  # 403表示有API但可能权限不足
        except:
            return False


if __name__ == "__main__":
    print("OpenAI Embedding Provider - 需要配置API密钥才能运行")

