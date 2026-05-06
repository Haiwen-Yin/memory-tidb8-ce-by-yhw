#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TiDB Memory System - Embedding Provider 抽象基类
==================================================

所有Embedding模型的统一接口规范

Author: Haiwen Yin (胖头鱼 🐟 / yhw)
Version: 0.2.0
"""

from abc import ABC, abstractmethod
import numpy as np


class BaseEmbeddingProvider(ABC):
    """Embedding Provider抽象基类
    
    所有支持不同模型的实现都必须继承此类并实现以下方法。
    
    Attributes:
        model_name (str): 模型名称
        dimensions (int): 向量维度
        provider_type (str): 提供商类型 (bge_m3/openai/cohere/huggingface)
        endpoint (str): API端点（本地或远程）
        max_input_length (int): 最大输入文本长度
    """
    
    def __init__(self, model_name: str = "unknown", dimensions: int = 1024,
                 provider_type: str = "local", endpoint: str = "", 
                 api_key: str = "", model_id: str = "", max_input_length: int = 512):
        """初始化Provider
        
        Args:
            model_name: 模型名称（如 'text-embedding-bge-m3'）
            dimensions: 向量维度
            provider_type: 提供商类型标识
            endpoint: API端点URL
            api_key: API密钥（如有需要）
            model_id: 特定模型的ID
            max_input_length: 最大输入长度限制
        """
        self.model_name = model_name
        self.dimensions = dimensions
        self.provider_type = provider_type
        self.endpoint = endpoint
        self.api_key = api_key
        self.model_id = model_id or model_name
        self.max_input_length = max_input_length
    
    @abstractmethod
    def get_embedding(self, text: str) -> np.ndarray:
        """获取文本的embedding向量
        
        Args:
            text: 需要生成embeding的文本（会被截断至max_input_length）
            
        Returns:
            numpy array格式的向量，维度由模型决定
            
        Raises:
            RuntimeError: 当API调用失败时抛出异常
            ValueError: 当输入文本为空或格式错误时抛出
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> dict:
        """获取当前使用的模型信息
        
        Returns:
            {
                "model_name": str,      # 模型名称
                "dimensions": int,      # 向量维度  
                "provider": str,        # 服务提供商
                "max_input_length": int # 最大输入长度限制
            }
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查服务是否可用
        
        Returns:
            True如果服务正常，否则False
        """
        pass
    
    def truncate_text(self, text: str) -> str:
        """根据模型限制截断文本
        
        Args:
            text: 原始文本
            
        Returns:
            截断后的文本（保留末尾以避免丢失关键信息）
        """
        if len(text) > self.max_input_length:
            # 截断时保留最后N个字符以确保语义完整性
            truncated = int(self.max_input_length * 0.7)
            return text[:truncated] + "..."
        return text


# Provider注册表：用于动态创建对应类型的Provider
PROVIDER_REGISTRY = {}

def register_provider(provider_class):
    """装饰器：将provider类注册到全局注册表中"""
    PROVIDER_REGISTRY[provider_class.__name__.lower().replace('provider', '')] = provider_class
    return provider_class


# 预定义常用配置模板
PROVIDER_CONFIGS = {
    "bge_m3": {
        "model_name": "text-embedding-bge-m3",
        "dimensions": 1024,
        "provider_type": "bge_m3",
        "endpoint": "http://10.10.10.1:12345/v1/embeddings",
        "model_id": "text-embedding-bge-m3",
        "max_input_length": 8192,
    },
    "openai_ada": {
        "model_name": "text-embedding-ada-002", 
        "dimensions": 1536,
        "provider_type": "openai",
        "endpoint": "https://api.openai.com/v1/embeddings",
        "max_input_length": 8191,
    },
    "cohere_multilingual_v3": {
        "model_name": "embed-multilingual-v3.0",
        "dimensions": 1024,
        "provider_type": "cohere", 
        "endpoint": "https://api.cohere.ai/v1/embed",
        "max_input_length": 512,
    },
}


if __name__ == "__main__":
    # 测试用例：展示如何切换不同Provider
    
    print("=" * 60)
    print("🔧 Embedding Provider 多模型适配架构")
    print("=" * 60)
    
    # 1. 使用BGE-M3（本地LM Studio）
    bge_config = PROVIDER_CONFIGS["bge_m3"].copy()
    print("\n1️⃣ BGE-M3 (本地LM Studio):")
    for key, value in bge_config.items():
        masked = "***" if "key" in key.lower() else str(value)[:50]
        print(f"   {key}={masked}")
    
    # 2. 使用OpenAI（需要API Key）
    openai_config = PROVIDER_CONFIGS["openai_ada"].copy()
    print("\n2️⃣ OpenAI Embeddings:")
    for key, value in openai_config.items():
        masked = "***" if "key" in key.lower() else str(value)[:50]
        print(f"   {key}={masked}")
    
    # 3. 使用Cohere（需要API Key）
    cohere_config = PROVIDER_CONFIGS["cohere_multilingual_v3"].copy()
    print("\n3️⃣ Cohere Embeddings:")
    for key, value in cohere_config.items():
        masked = "***" if "key" in key.lower() else str(value)[:50]
        print(f"   {key}={masked}")
    
    # 4. 动态创建示例代码
    print("\n📝 使用示例:")
    print("""
# 方式1: 直接导入对应Provider
from embedding_providers.bge_m3 import BGEM3Provider

provider = BGEM3Provider(endpoint="http://localhost:12345/v1/embeddings")

# 方式2: 通过配置字典动态创建（推荐）
from embedding_providers.base_provider import PROVIDER_CONFIGS, BaseEmbeddingProvider

config = PROVIDER_CONFIGS["bge_m3"]  # 或 "openai_ada", "cohere_multilingual_v3"
provider = BaseEmbeddingProvider.from_config(config)
    """)
