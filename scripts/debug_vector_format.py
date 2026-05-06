#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试脚本：查看TiDB VECTOR类型实际存储格式
"""

import pymysql
import numpy as np

host = "10.10.10.142"
port = 4000
user = "root"
password = "tidb#123"

conn = pymysql.connect(
    host=host, port=port, user=user, password=password,
    charset='utf8mb4', connect_timeout=15,
)
cursor = conn.cursor()

print("=" * 70)
print("🔍 TiDB VECTOR类型存储格式调试")
print("=" * 70)

# Step 1: 查询vector_native_test表数据
cursor.execute("USE memory_system;")
cursor.execute("SELECT id, text_content, embedding FROM vector_native_test LIMIT 5;")
rows = cursor.fetchall()

print(f"\n📋 查询到 {len(rows)} 条记录:")
for i, row in enumerate(rows):
    print(f"\n   [记录{i+1}]")
    print(f"     ID: {row[0]}")
    print(f"     文本: {str(row[1])[:50] if row[1] else 'None'}")
    
    # 检查embedding数据类型和长度
    embedding = row[2]
    if embedding is not None:
        print(f"     嵌入类型: {type(embedding)}")
        print(f"     嵌入长度: {len(str(embedding))} 字符")
        
        # 尝试转换为字符串查看内容
        emb_str = str(embedding)
        print(f"     嵌入前100字符: {emb_str[:100]}...")
        
        # 尝试解析为数字数组
        try:
            import ast
            parsed = ast.literal_eval(emb_str)
            if isinstance(parsed, list):
                arr = np.array(parsed)
                print(f"     ✅ 成功解析为numpy数组，形状:{arr.shape}")
            else:
                print(f"     ❌ 解析为{type(parsed)}而非list")
        except Exception as e:
            print(f"     ❌ ast.literal_eval失败: {e}")
            
            # 尝试其他方式
            try:
                # 可能是二进制数据
                if isinstance(embedding, bytes):
                    print(f"     ℹ️  是bytes类型，长度:{len(embedding)}")
                    # 尝试解码为float数组
                    import struct
                    num_floats = len(embedding) // 4
                    floats = struct.unpack(f'{num_floats}f', embedding[:num_floats*4])
                    print(f"     ✅ 可解析为{len(floats)}个浮点数")
            except Exception as e2:
                print(f"     ❌ bytes解码也失败: {e2}")
    else:
        print("     嵌入: None（未存储）")

# Step 2: 检查memories表
print("\n\n📋 memories表数据:")
cursor.execute("SELECT id, memory_id, title FROM memories LIMIT 5;")
mem_rows = cursor.fetchall()
for row in mem_rows:
    print(f"   ID:{row[0]}, MemoryID:{row[1]}, Title:{str(row[2])[:30]}")

conn.close()
