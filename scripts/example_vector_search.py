#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TiDB Memory System - Vector Search Engine 使用示例
==================================================

演示如何使用VectorSearchEngine进行向量检索

Author: Haiwen Yin (胖头鱼 🐟 / yhw)
Version: 0.2.0
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from vector_search_engine import VectorSearchEngine, Config


def demo_basic_usage():
    """基础使用示例"""
    
    print("=" * 70)
    print("📚 TiDB Vector Search Engine - 使用示例")
    print("=" * 70)
    
    # 1. 创建引擎实例（使用默认配置）
    engine = VectorSearchEngine()
    
    # 2. 连接到TiDB数据库
    print("\n[1] 连接TiDB...")
    if not engine.connect():
        print("❌ 无法连接数据库，请检查配置")
        return
    
    try:
        # 3. 确保表结构存在
        print("[2] 检查表结构...")
        engine.create_memory_table()
        
        # 4. 存储测试记忆（带embedding）
        print("\n[3] 存储测试记忆...")
        test_memories = [
            ("mem-001", "TiDB数据库知识", 
             "TiDB是一个分布式关系型数据库，支持HTAP混合负载"),
            ("mem-002", "向量搜索技术", 
             "使用BGE-M3模型进行文本向量化和相似度计算"),
            ("mem-003", "AI Agent记忆系统", 
             "基于PostgreSQL和Apache AGE的记忆图谱架构"),
        ]
        
        for memory_id, title, content in test_memories:
            # 获取embedding
            embedding = engine.get_embedding(f"{title}: {content}")
            if embedding is not None:
                success = engine.store_memory(memory_id, title, content, embedding)
                status = "✅" if success else "❌"
                print(f"   {status} {title[:30]}")
        
        # 5. 执行搜索查询
        print("\n[4] 执行相似度搜索...")
        
        queries = [
            "分布式数据库系统架构设计",
            "人工智能和向量技术",
            "PostgreSQL相关工具"
        ]
        
        for query in queries:
            print(f"\n   🔍 查询: '{query}'")
            results = engine.search_similar(query, top_k=3)
            
            if results:
                print(f"     📊 找到 {len(results)} 条相似结果:")
                for i, result in enumerate(results, 1):
                    print(f"       {i}. [{result.similarity:.4f}] {result.title}")
            else:
                print("     ℹ️  没有找到匹配结果")
        
        # 6. 展示配置选项
        print("\n[5] 自定义配置示例:")
        custom_config = Config(
            host="10.10.10.142",
            port=4000,
            user="root",
            password="tidb#123",
            database="memory_system",
            embedding_endpoint="http://10.10.10.1:12345/v1/embeddings",
            model_id="text-embedding-bge-m3",
            top_k=5,
            similarity_threshold=0.6  # 降低阈值以获取更多内容
        )
        
        engine_custom = VectorSearchEngine(config=custom_config)
        print("   ✅ 已创建自定义配置引擎")
        
    finally:
        # 7. 清理连接
        engine.disconnect()
    
    print("\n" + "=" * 70)
    print("✅ 示例演示完成！")
    print("=" * 70)


if __name__ == "__main__":
    demo_basic_usage()
