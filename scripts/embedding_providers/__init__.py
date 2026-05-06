#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TiDB Memory System - Embedding Providers Package
=================================================

多模型Embedding适配器包

支持多种Embedding模型的统一接口设计，包括：
- BGE-M3 (本地LM Studio服务)
- OpenAI Embeddings (官方API)
- Cohere Embeddings (第三方API)
- HuggingFace Transformers (本地开源模型)

Author: Haiwen Yin (胖头鱼 🐟 / yhw)
Version: 0.2.0
"""

# 从base_provider导入核心类和配置
from .base_provider import BaseEmbeddingProvider, PROVIDER_REGISTRY, PROVIDER_CONFIGS

# 导入所有providers（自动注册到PROVIDER_REGISTRY）
from .bge_m3_provider import BGEM3Provider
from .openai_provider import OpenAIEmbeddingProvider
from .cohere_provider import CohereEmbeddingProvider
from .huggingface_provider import HuggingFaceTransformersProvider

# 导出公共接口
__all__ = [
    'BaseEmbeddingProvider',
    'PROVIDER_REGISTRY', 
    'PROVIDER_CONFIGS',
    'BGEM3Provider',
    'OpenAIEmbeddingProvider',
    'CohereEmbeddingProvider',
    'HuggingFaceTransformersProvider',
]

# 便捷函数：根据配置创建provider实例
def create_embedding_provider(config: dict = None) -> BaseEmbeddingProvider:
    """根据配置字典创建对应的Provider实例
    
    Args:
        config: Provider配置字典，如果为None则使用默认BGE-M3配置
        
    Returns:
        BaseEmbeddingProvider的子类实例
        
    Examples:
        >>> # 使用默认BGE-M3
        >>> provider = create_embedding_provider()
        
        >>> # 指定OpenAI模型
        >>> config = PROVIDER_CONFIGS["openai_ada"]
        >>> config["api_key"] = "sk-your-key"
        >>> provider = create_embedding_provider(config)
    """
    if config is None:
        config = PROVIDER_CONFIGS.get("bge_m3", {}).copy()
    
    # 使用BaseEmbeddingProvider.from_config方法（如果存在）或手动创建
    if hasattr(BaseEmbeddingProvider, 'from_config'):
        return BaseEmbeddingProvider.from_config(config)
    
    # 否则根据provider_type手动创建
    provider_type = config.get("provider_type", "bge_m3")
    
    providers_map = {
        "bge_m3": BGEM3Provider,
        "openai": OpenAIEmbeddingProvider, 
        "cohere": CohereEmbeddingProvider,
        "huggingface": HuggingFaceTransformersProvider,
    }
    
    provider_class = providers_map.get(provider_type)
    if not provider_class:
        raise ValueError(f"不支持的provider类型: {provider_type}")
    
    return provider_class(**config)

# 打印可用配置信息
print("=" * 60)
print("🔧 TiDB Embedding Providers Package Loaded")
print("=" * 60)
print("\n可用的Provider配置:")
for name in PROVIDER_CONFIGS.keys():
    config = PROVIDER_CONFIGS[name]
    dims = config.get('dimensions', 'N/A')
    provider_type = config.get('provider_type', '?')
    print(f"  • {name:20} ({dims}维) - {provider_type}")

print("\n推荐使用方式:")
print("""
# 1. 使用默认BGE-M3（本地服务）
from embedding_providers import create_embedding_provider
provider = create_embedding_provider()

# 2. 指定OpenAI模型  
from embedding_providers import PROVIDER_CONFIGS, create_embedding_provider
config = PROVIDER_CONFIGS["openai_ada"]
config["api_key"] = "sk-your-key"
provider = create_embedding_provider(config)

# 3. 直接使用特定Provider类
from embedding_providers.bge_m3 import BGEM3Provider
provider = BGEM3Provider(endpoint="http://localhost:12345/v1/embeddings")
""")
print("=" * 60)
