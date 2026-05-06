#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TiDB Memory System - HuggingFace Transformers Provider
=======================================================

本地HuggingFace模型适配器（无需API）
支持bge-m3、nomic-embed-text等开源模型

Author: Haiwen Yin (胖头鱼 🐟 / yhw)
Version: 0.2.0
"""

import numpy as np
from .base_provider import BaseEmbeddingProvider, register_provider


@register_provider
class HuggingFaceTransformersProvider(BaseEmbeddingProvider):
    """HuggingFace Transformers本地模型适配器
    
    使用transformers库在本地加载和运行开源嵌入模型。
    优势：无需API密钥、离线可用、可自定义模型。
    
    Supported Models:
        - BAAI/bge-m3 (1024维)
        - nomic-ai/nomic-embed-text-v1 (768维)
        - sentence-transformers/all-MiniLM-L6-v2 (384维)
    
    Usage:
        >>> from embedding_providers.huggingface import HuggingFaceTransformersProvider
        >>> provider = HuggingFaceTransformersProvider(
        ...     model_name="BAAI/bge-m3",
        ...     device="cuda"  # or "cpu"
        ... )
    """
    
    def __init__(self, model_name: str = "BAAI/bge-m3",
                 dimensions: int = 1024,
                 provider_type: str = "huggingface",
                 device: str = None,
                 max_input_length: int = 8192):
        """初始化HuggingFace Provider
        
        Args:
            model_name: HuggingFace模型仓库名称
            dimensions: 向量维度（自动检测或手动指定）
            provider_type: 提供商类型标识
            device: 运行设备 ("cuda", "cpu", or None为自动选择)
            max_input_length: 最大输入长度限制
        """
        super().__init__(
            model_name=model_name,
            dimensions=dimensions,
            provider_type=provider_type,
            device=device if device else ("cuda" if __import__("torch").cuda.is_available() else "cpu"),
            max_input_length=max_input_length
        )
        
        # 延迟加载模型和tokenizer（避免启动时消耗大量内存）
        self._model = None
        self._tokenizer = None
    
    def _load_model(self):
        """懒加载模型和tokenizer"""
        if self._model is None or self._tokenizer is None:
            try:
                from transformers import AutoModel, AutoTokenizer
                
                # 加载模型（从HuggingFace Hub或本地缓存）
                print(f"📥 Loading model: {self.model_name}...")
                self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self._model = AutoModel.from_pretrained(self.model_name)
                
                if self.device and hasattr(self._model, 'to'):
                    self._model.to(self.device)
                
                # 如果dimensions未设置，尝试自动检测
                if self.dimensions == 1024:  # 默认值可能不准确
                    with torch.no_grad():
                        test_input = self._tokenizer("test", return_tensors="pt")
                        outputs = self._model(**test_input)
                        if hasattr(outputs, 'last_hidden_state'):
                            self.dimensions = outputs.last_hidden_state.shape[-1]
                
                print(f"✅ Model loaded: {self.model_name}, dimensions={self.dimensions}")
                
            except ImportError as e:
                raise RuntimeError(f"HuggingFace transformers库未安装: {e}. 请运行 pip install transformers torch")
        
        # 设备切换
        if self.device and hasattr(self._model, 'to'):
            current_device = next(self._model.parameters()).device
            if str(current_device) != self.device:
                self._model.to(self.device)
    
    def get_embedding(self, text: str) -> np.ndarray:
        """使用本地模型获取embedding
        
        Args:
            text: 需要生成embedding的文本
            
        Returns:
            numpy array格式的向量
            
        Raises:
            RuntimeError: 模型加载或推理失败
            ValueError: 输入为空
        """
        if not text or not text.strip():
            raise ValueError("输入文本不能为空")
        
        truncated_text = self.truncate_text(text)
        
        try:
            # 确保模型已加载
            self._load_model()
            
            import torch
            
            # Tokenize and encode
            with torch.no_grad():
                inputs = self._tokenizer(
                    truncated_text, 
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=self.max_input_length
                )
                
                # 移动输入到正确设备
                if hasattr(inputs, 'to'):
                    inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                # 获取模型输出
                outputs = self._model(**inputs)
            
            # 提取embedding（使用[CLS] token或mean pooling）
            last_hidden_state = outputs.last_hidden_state
            
            # Mean pooling over all tokens (excluding padding)
            attention_mask = inputs.get("attention_mask", torch.ones_like(last_hidden_state[:, :, 0]))
            
            # Expand mask to match hidden state dimensions
            if len(attention_mask.shape) == 2:
                attention_mask = attention_mask.unsqueeze(-1).expand_as(last_hidden_state)
            
            mean_embedding = (last_hidden_state * attention_mask).sum(dim=1) / attention_mask.sum(dim=1)
            
            # Convert to numpy
            return mean_embedding.squeeze().cpu().numpy()
            
        except Exception as e:
            raise RuntimeError(f"HuggingFace获取embedding失败: {str(e)}")
    
    def get_model_info(self) -> dict:
        """获取模型信息"""
        return {
            "model_name": self.model_name,
            "dimensions": self.dimensions,
            "provider": "huggingface",
            "max_input_length": self.max_input_length,
            "device": self.device or (next(self._model.parameters()).device if self._model else "unknown"),
            "is_local": True,  # 标记为本地模型
        }
    
    def is_available(self) -> bool:
        """检查HuggingFace模型是否可用"""
        try:
            import torch
            return True
        except ImportError:
            return False


if __name__ == "__main__":
    print("HuggingFace Transformers Provider - 本地模型运行")

