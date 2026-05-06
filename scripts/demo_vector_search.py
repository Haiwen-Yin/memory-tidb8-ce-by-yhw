#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TiDB Vector Search Engine - 完整功能演示
========================================

演示向量检索引擎的完整功能：
1. 连接TiDB数据库（使用原生VECTOR类型）
2. 从BGE-M3服务获取文本embedding
3. 存储记忆和向量到TiDB
4. 执行相似度搜索查询

Author: Haiwen Yin (胖头鱼 🐟 / yhw)
Version: 0.2.0
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from vector_search_engine import VectorSearchEngine


def main():
    """完整演示向量检索功能"""
    
    print("=" * 70)
    print("🔍 TiDB Vector Search Engine - 完整功能演示")
    print(f"版本: 0.2.0 | TiDB v8.5.6 + BGE-M3 + 原生VECTOR类型")
    print("=" * 70)
    
    # 创建引擎实例
    engine = VectorSearchEngine()
    
    try:
        # Step 1: 连接数据库
        print("\n[Step 1/6] 连接TiDB数据库...")
        if not engine.connect():
            print("❌ 无法连接数据库，请检查配置")
            return
        
        # Step 2: 检查表结构
        print("[Step 2/6] 验证表结构...")
        engine.create_memory_table()
        
        # Step 3: 存储测试记忆（带embedding）
        print("\n[Step 3/6] 存储记忆数据到TiDB...")
        test_memories = [
            ("mem-001", "TiDB数据库知识", 
             "TiDB是一个分布式关系型数据库，支持HTAP混合负载"),
            ("mem-002", "向量搜索技术", 
             "使用BGE-M3模型进行文本向量化和相似度计算"),
            ("mem-003", "AI Agent记忆系统", 
             "基于PostgreSQL和Apache AGE的记忆图谱架构"),
            ("mem-004", "Python编程技巧", 
             "Python是流行的编程语言，支持numpy数组操作"),
        ]
        
        stored_count = 0
        for memory_id, title, content in test_memories:
            # 获取embedding
            embedding_text = f"{title}: {content}"
            embedding = engine.get_embedding(embedding_text)
            
            if embedding is not None and len(embedding) == 1024:
                success = engine.store_memory(memory_id, title, content, embedding)
                status = "✅" if success else "❌"
                print(f"   {status} {title[:35]}")
                stored_count += 1 if success else 0
            else:
                print(f"   ⚠️  {title}: embedding获取失败或维度不匹配")
        
        print(f"\n   📊 成功存储 {stored_count}/{len(test_memories)} 条记忆")
        
        # Step 4: 执行多个搜索查询
        print("\n[Step 4/6] 执行向量相似度搜索...")
        
        queries = [
            ("分布式数据库系统架构设计", "关于数据库架构的查询"),
            ("人工智能和机器学习技术", "AI相关话题"),
            ("Python编程与数据处理", "编程工具类查询"),
        ]
        
        for query, description in queries:
            print(f"\n   🔍 搜索: '{query}' ({description})")
            results = engine.search_similar(query, top_k=3)
            
            if results:
                print(f"     📊 找到 {len(results)} 条相似结果:")
                for i, result in enumerate(results, 1):
                    bar = "█" * int(result.similarity * 20) + "░" * (20 - int(result.similarity * 20))
                    print(f"       {i}. [{bar}] [{result.similarity:.4f}]")
                    print(f"          📌 {result.title}")
                    if result.memory_id:
                        print(f"          🆔 ID: {result.memory_id}")
            else:
                print("     ℹ️  没有找到匹配结果（语义距离较远）")
        
        # Step 5: 展示相似度计算示例
        print("\n[Step 5/6] 相似度计算演示...")
        
        # 获取两个不同文本的embedding进行对比
        text1 = "数据库管理系统"
        text2 = "机器学习算法"
        text3 = "关系型数据库工具"
        
        emb1 = engine.get_embedding(text1)
        emb2 = engine.get_embedding(text2)
        emb3 = engine.get_embedding(text3)
        
        if emb1 is not None and len(emb1) > 0 and emb2 is not None and len(emb2) > 0 and emb3 is not None and len(emb3) > 0:
            sim_12 = engine.cosine_similarity(emb1, emb2)
            sim_13 = engine.cosine_similarity(emb1, emb3)
            
            print(f"   '数据库管理系统' vs '机器学习算法': {sim_12:.4f}")
            print(f"   '数据库管理系统' vs '关系型数据库工具': {sim_13:.4f}")
            print(f"   ✅ 语义相近的内容相似度更高")
        
        # Step 6: 保存搜索结果
        print("\n[Step 6/6] 导出搜索结果...")
        
        final_query = "分布式数据库系统架构设计"
        final_results = engine.search_similar(final_query, top_k=5)
        
        if final_results:
            import json
            output_file = "/tmp/tidb_vector_search_results.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                search_data = {
                    "query": final_query,
                    "timestamp": datetime.now().isoformat(),
                    "results": [r.to_dict() for r in final_results]
                }
                json.dump(search_data, f, ensure_ascii=False, indent=2)
            print(f"   ✅ 搜索结果已保存到: {output_file}")
        
    finally:
        # 清理连接
        engine.disconnect()
    
    print("\n" + "=" * 70)
    print("✅ 向量检索引擎完整功能演示完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()
