#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TiDB Memory System - BGE-M3 Embedding Provider
================================================

BGE-M3多语言嵌入模型的本地LM Studio适配器
支持通过HTTP API调用本地的LM Studio服务

Author: Haiwen Yin (胖头鱼 🐟 / yhw)
Version: 0.2.0
"""

import requests
import numpy as np
from .base_provider import BaseEmbeddingProvider, register_provider


@register_provider
class BGEM3Provider(BaseEmbeddingProvider):
    """BGE-M3模型本地适配器
    
    BGE-M3是一个强大的多语言文本嵌入模型，支持多种语言和长文档。
    通过LM Studio的本地服务提供API访问。
    
    Features:
        - 1024维度向量输出
        - 8192 token上下文窗口
        - 支持中英文等多语言
        - 本地运行无需云端依赖
    
    Usage:
        >>> from embedding_providers.bge_m3 import BGEM3Provider
        >>> provider = BGEM3Provider(
        ...     endpoint="http://localhost:12345/v1/embeddings"
        ... )
        >>> embedding = provider.get_embedding("你好世界")
    """
    
    def __init__(self, model_name: str = "text-embedding-bge-m3", 
                 dimensions: int = 1024,
                 endpoint: str = "http://localhost:12345/v1/embeddings",
                 model_id: str = "text-embedding-bge-m3",
                 max_input_length: int = 8192):
        """初始化BGE-M3 Provider
        
        Args:
            model_name: BGE-M3模型名称
            dimensions: 向量维度（固定为1024）
            endpoint: LM Studio服务地址
            model_id: 具体使用的模型ID
            max_input_length: 最大输入长度限制
        """
        super().__init__(
            model_name=model_name,
            dimensions=dimensions,
            provider_type="bge_m3",
            endpoint=endpoint,
            model_id=model_id,
            max_input_length=max_input_length
        )
    
    def get_embedding(self, text: str) -> np.ndarray:
        """从LM Studio服务获取BGE-M3 embedding
        
        Args:
            text: 需要生成embedding的文本
            
        Returns:
            numpy array格式的1024维度向量
            
        Raises:
            RuntimeError: API调用失败或响应异常
            ValueError: 输入文本为空或格式错误
        """
        if not text or not text.strip():
            raise ValueError("输入文本不能为空")
        
        # 截断过长文本
        truncated_text = self.truncate_text(text)
        
        try:
            response = requests.post(
                self.endpoint,
                json={
                    "model": self.model_id,
                    "input": truncated_text,
                    "encoding_format": "float"
                },
                timeout=30
            )
            
            if response.status_code != 200:
                raise RuntimeError(f"BGE-M3 API错误: HTTP {response.status_code} - {response.text[:100]}")
            
            data = response.json()
            
            # 验证响应格式
            if "data" not in data or len(data["data"]) == 0:
                raise RuntimeError("BGE-M3响应格式异常：缺少'data'字段")
            
            embedding_list = data["data"][0]["embedding"]
            return np.array(embedding_list, dtype=np.float32)
            
        except requests.exceptions.ConnectionError:
            raise RuntimeError(f"无法连接到LM Studio服务: {self.endpoint}")
        except requests.exceptions.Timeout:
            raise RuntimeError("BGE-M3 API请求超时")
        except Exception as e:
            raise RuntimeError(f"BGE-M3获取embedding失败: {str(e)}")
    
    def get_model_info(self) -> dict:
        """获取BGE-M3模型信息"""
        return {
            "model_name": self.model_name,
            "dimensions": self.dimensions,
            "provider": "bge_m3",
            "max_input_length": self.max_input_length,
            "endpoint": self.endpoint,
            "supported_languages": ["zh", "en", "ja", "ko", "de", "fr"],
        }
    
    def is_available(self) -> bool:
        """检查BGE-M3服务是否可用
        
        Returns:
            True如果LM Studio服务正常响应，否则False
        """
        try:
            response = requests.get(
                f"{self.endpoint.rsplit('/', 1)[0]}/health",
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            # 如果健康端点不存在，尝试获取一个简单embedding
            try:
                self.get_embedding("test")
                return True
            except:
                return False


if __name__ == "__main__":
    import time
    
    print("=" * 60)
    print("🧪 BGE-M3 Provider 测试")
    print("=" * 60)
    
    provider = BGEM3Provider(endpoint="http://10.10.10.1:12345/v1/embeddings")
    
    # 检查服务可用性
    available = provider.is_available()
    print(f"\n📊 BGE-M3服务状态: {'✅ 可用' if available else '❌ 不可用'}")
    
    # 获取模型信息
    model_info = provider.get_model_info()
    print("\n🔧 模型信息:")
    for key, value in model_info.items():
        if isinstance(value, list):
            print(f"   {key}: {', '.join(str(v) for v in value)}")
        else:
            print(f"   {key}: {value}")
    
    # 测试embedding生成
    test_texts = [
        "TiDB分布式数据库管理系统",
        "向量相似度搜索算法实现",
        "BGE-M3多语言嵌入模型",
    ]
    
    print("\n📝 Embedding生成测试:")
    for text in test_texts:
        start_time = time.time()
        try:
            embedding = provider.get_embedding(text)
            elapsed = (time.time() - start_time) * 1000
            print(f"   ✅ '{text[:30]}...' - {len(embedding)}维, {elapsed:.2f}ms")
        except Exception as e:
            print(f"   ❌ '{text[:30]}...': {str(e)[:50]}")

