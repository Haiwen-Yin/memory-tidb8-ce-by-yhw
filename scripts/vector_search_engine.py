#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TiDB Memory System - Vector Search Engine
基于TiDB v8.5.6原生VECTOR类型的向量检索引擎

Author: Haiwen Yin (胖头鱼 🐟 / yhw)
Version: 0.2.0
"""

import json
import numpy as np
import requests
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class SimilarityResult:
    """相似度搜索结果"""
    id: int
    memory_id: str
    title: str
    similarity: float
    content_preview: str

    def to_dict(self):
        return {
            "id": self.id,
            "memory_id": self.memory_id,
            "title": self.title,
            "similarity": round(self.similarity, 4),
            "content_preview": self.content_preview[:100] if self.content_preview else ""
        }


@dataclass
class Config:
    """检索引擎配置"""
    host: str = "10.10.10.142"
    port: int = 4000
    user: str = "root"
    password: str = "tidb#123"
    database: str = "memory_system"
    
    # Embedding Provider配置
    embedding_provider_type: str = "bge_m3"  # bge_m3/openai/cohere/huggingface
    embedding_endpoint: str = "http://10.10.10.1:12345/v1/embeddings"
    model_id: str = "text-embedding-bge-m3"
    api_key: str = ""  # OpenAI/Cohere需要
    
    top_k: int = 10
    similarity_threshold: float = 0.7


class VectorSearchEngine:
    """基于TiDB原生VECTOR的向量检索引擎"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.conn = None
        self._provider = None  # Embedding Provider实例（懒加载）
        
    def connect(self):
        """连接到TiDB数据库"""
        try:
            import pymysql
            self.conn = pymysql.connect(
                host=self.config.host,
                port=self.config.port,
                user=self.config.user,
                password=self.config.password,
                database=self.config.database,
                charset='utf8mb4',
                connect_timeout=15
            )
            return True
        except Exception as e:
            print(f"❌ TiDB连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    
    def get_embedding_provider(self):
        """获取或创建Embedding Provider实例（支持多模型切换）
        
        Returns:
            BaseEmbeddingProvider实例
            
        Raises:
            RuntimeError: 当无法初始化对应的Provider时抛出
        """
        if self._provider is None:
            try:
                from embedding_providers import create_embedding_provider, PROVIDER_CONFIGS
                
                # 构建配置字典
                provider_config = {
                    "provider_type": self.config.embedding_provider_type,
                    "endpoint": self.config.embedding_endpoint,
                    "model_id": self.config.model_id,
                    "api_key": self.config.api_key,
                }
                
                # 根据provider类型设置默认配置
                if self.config.embedding_provider_type == "bge_m3":
                    provider_config.update(PROVIDER_CONFIGS["bge_m3"])
                elif self.config.embedding_provider_type in ("openai", "openai-embeddings"):
                    provider_config.update(PROVIDER_CONFIGS["openai_ada"])
                elif self.config.embedding_provider_type in ("cohere", "cohere-embed"):
                    provider_config.update(PROVIDER_CONFIGS["cohere_multilingual_v3"])
                
                # 创建Provider实例
                self._provider = create_embedding_provider(provider_config)
                
            except ImportError as e:
                raise RuntimeError(f"无法导入embedding_providers模块: {e}")
            except Exception as e:
                raise RuntimeError(f"初始化Embedding Provider失败: {e}")
        
        return self._provider
    def get_embedding(self, text: str) -> Optional[np.ndarray]:
        """从BGE-M3服务获取文本的embedding向量"""
        try:
            response = requests.post(
                self.config.embedding_endpoint,
                json={
                    "model": self.config.model_id,
                    "input": text,
                    "encoding_format": "float"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return np.array(data['data'][0]['embedding'], dtype=np.float32)
            else:
                print(f"❌ BGE-M3服务错误: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 获取embedding失败: {e}")
            return None
    
    def cosine_similarity(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        """计算两个向量的余弦相似度"""
        dot = np.dot(vec_a, vec_b)
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return float(dot / (norm_a * norm_b))
    
    def convert_to_tidb_vector(self, embedding: np.ndarray) -> str:
        """将numpy数组转换为TiDB VECTOR存储格式"""
        vector_text = json.dumps(embedding.tolist(), separators=(',', ' '))
        return f"CAST('{vector_text}' AS VECTOR({len(embedding)}))"
    
    def store_memory(self, memory_id: str, title: str, 
                     content: str, embedding: np.ndarray) -> bool:
        """存储记忆和对应的向量到TiDB"""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
                INSERT INTO memories (memory_id, title, content) 
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE updated_at = CURRENT_TIMESTAMP;
            """, (memory_id, title, content))
            
            vector_text = self.convert_to_tidb_vector(embedding)
            cursor.execute(f"""
                INSERT INTO vector_native_test (text_content, embedding) 
                VALUES (%s, {vector_text});
            """, (f"{title}: {content[:50]}"))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ 存储失败: {e}")
            return False
    
    def search_similar(self, query_text: str, top_k: int = None) -> List[SimilarityResult]:
        """搜索与查询文本最相似的记忆"""
        
        if top_k is None:
            top_k = self.config.top_k
        
        # 降低阈值以便测试看到更多结果（生产环境建议0.7-0.8）
        original_threshold = self.config.similarity_threshold
        self.config.similarity_threshold = 0.5
        
        query_embedding = self.get_embedding(query_text)
        if not (query_embedding is not None and len(query_embedding) > 0):
            # 恢复阈值
            self.config.similarity_threshold = original_threshold
            return []
        
        try:
            cursor = self.conn.cursor()
            
            # 由于TiDB CE不支持VECTOR_DISTANCE，在应用层计算相似度
            cursor.execute("SELECT id, memory_id, title, content FROM memories;")
            memories = cursor.fetchall()
            
            results = []
            for memory in memories:
                mem_id, memory_id, title, content = memory
                
                # 通过title精确匹配查找对应的向量记录
                cursor.execute("""
                    SELECT embedding FROM vector_native_test 
                    WHERE text_content LIKE %s;
                """, (f"{title}:%",))
                
                row = cursor.fetchone()
                if row:
                    try:
                        # TiDB返回的是JSON格式的字符串，需要解析为numpy数组
                        vec_str = str(row[0])
                        import ast
                        vec_array = np.array(ast.literal_eval(vec_str))
                        similarity = self.cosine_similarity(query_embedding, vec_array)
                        
                        if similarity >= self.config.similarity_threshold:
                            results.append(SimilarityResult(
                                id=mem_id,
                                memory_id=memory_id,
                                title=title,
                                similarity=similarity,
                                content_preview=content[:100] if content else ""
                            ))
                    except Exception as e:
                        continue
            
            results.sort(key=lambda x: x.similarity, reverse=True)
            return results[:top_k]
            
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            return []
    
    def create_memory_table(self):
        """创建必要的记忆表结构"""
        try:
            cursor = self.conn.cursor()
            
            # 创建基础记忆表（如果不存在）
            create_memories_sql = """
                CREATE TABLE IF NOT EXISTS memories (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    memory_id VARCHAR(36) NOT NULL UNIQUE COMMENT '记忆UUID',
                    title VARCHAR(512) NOT NULL COMMENT '记忆标题',
                    content TEXT COMMENT '记忆内容（精简版）',
                    status ENUM('active', 'archived', 'deprecated') DEFAULT 'active' COMMENT '状态',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_status (status),
                    INDEX idx_created_at (created_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
            """
            cursor.execute(create_memories_sql)
            
            # 创建向量存储表（使用原生VECTOR类型）
            create_vector_sql = """
                CREATE TABLE IF NOT EXISTS vector_native_test (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    text_content TEXT COMMENT '关联文本',
                    embedding VECTOR(1024) COMMENT 'BGE-M3向量（1024维）',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_created (created_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
            """
            cursor.execute(create_vector_sql)
            
            self.conn.commit()
            print("✅ 表结构创建/确认完成")
            
        except Exception as e:
            print(f"❌ 创建表失败: {e}")


if __name__ == "__main__":
    # 快速测试
    engine = VectorSearchEngine()
    
    if engine.connect():
        try:
            query = "分布式数据库"
            embedding = engine.get_embedding(query)
            
            if embedding is not None and len(embedding) > 0:
                print(f"✅ BGE-M3 embedding获取成功，维度:{len(embedding)}")
                
                # 测试相似度计算
                test_vec = np.ones(1024, dtype=np.float32) * 0.5
                sim = engine.cosine_similarity(embedding, test_vec)
                print(f"✅ 余弦相似度计算正常: {sim:.4f}")
                
        finally:
            engine.disconnect()
