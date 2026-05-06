#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TiDB Memory System - Cohere Embedding Provider
===============================================

Cohere嵌入模型API适配器
支持embed-multilingual-v3.0等多语言模型

Author: Haiwen Yin (胖头鱼 🐟 / yhw)
Version: 0.2.0
"""

import requests
import numpy as np
from .base_provider import BaseEmbeddingProvider, register_provider


@register_provider
class CohereEmbeddingProvider(BaseEmbeddingProvider):
    """Cohere Embeddings API适配器
    
    Cohere提供高质量的多语言嵌入模型，特别擅长：
    - 多语言支持（50+语言）
    - 语义搜索优化
    - 长文本处理
    
    Models:
        - embed-multilingual-v3.0 (1024维)
        - embed-english-v3.0 (1024维)
    
    Usage:
        >>> from embedding_providers.cohere import CohereEmbeddingProvider
        >>> provider = CohereEmbeddingProvider(api_key="your-cohere-key")
    """
    
    def __init__(self, api_key: str = "",
                 model_name: str = "embed-multilingual-v3.0",
                 dimensions: int = 1024,
                 endpoint: str = "https://api.cohere.ai/v1/embed",
                 model_id: str = None,
                 max_input_length: int = 512):
        """初始化Cohere Provider
        
        Args:
            api_key: Cohere API密钥（必需）
            model_name: Cohere模型名称
            dimensions: 向量维度（取决于模型版本）
            endpoint: Cohere API端点
            model_id: 具体使用的模型ID，默认使用model_name
            max_input_length: 最大输入长度限制（Cohere通常较短）
        """
        if not api_key:
            raise ValueError("Cohere Provider需要API密钥")
        
        super().__init__(
            model_name=model_name,
            dimensions=dimensions,
            provider_type="cohere",
            endpoint=endpoint,
            api_key=api_key,
            model_id=model_id or model_name,
            max_input_length=max_input_length
        )
    
    def get_embedding(self, text: str) -> np.ndarray:
        """从Cohere API获取embedding
        
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
            "Content-Type": "application/json",
            "Cohere-Version": "2023-10-15"  # Cohere API版本头
        }
        
        payload = {
            "model": self.model_id,
            "texts": [truncated_text],
            "input_type": "search_document",
            "truncate": "END"  # 截断模式：START/END/NONE
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
                raise RuntimeError(f"Cohere API错误 ({response.status_code}): {error_detail}")
            
            data = response.json()
            
            # Cohere返回格式不同：{"embeddings": [[...]]}
            if "embeddings" not in data or len(data["embeddings"]) == 0:
                raise RuntimeError("Cohere响应格式异常")
            
            embedding_list = data["embeddings"][0]
            return np.array(embedding_list, dtype=np.float32)
            
        except requests.exceptions.ConnectionError:
            raise RuntimeError(f"无法连接到Cohere API: {self.endpoint}")
        except Exception as e:
            if "Unauthorized" in str(e):
                raise RuntimeError("Cohere API密钥无效或已过期")
            raise RuntimeError(f"Cohere获取embedding失败: {str(e)}")
    
    def get_model_info(self) -> dict:
        """获取模型信息"""
        return {
            "model_name": self.model_name,
            "dimensions": self.dimensions,
            "provider": "cohere",
            "max_input_length": self.max_input_length,
            "endpoint": self.endpoint,
            "languages_supported": 50,
            "pricing_note": "按字符计费，约$0.00025/1K tokens"
        }
    
    def is_available(self) -> bool:
        """检查Cohere服务是否可用"""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            response = requests.head(
                "https://api.cohere.ai/v1/models",
                headers=headers,
                timeout=5
            )
            return response.status_code == 200
        except:
            return False


if __name__ == "__main__":
    print("Cohere Embedding Provider - 需要配置API密钥才能运行")

