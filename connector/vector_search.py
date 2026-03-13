#!/usr/bin/env python3
"""
VectorBrain 向量检索模块

功能：
接收一句话 → 转成向量 → 跟数据库里的所有向量比对相似度 → 返回最相关的 Top-K

用法：
# 作为模块导入
from vector_search import search_memory
results = search_memory("上次那个备份的事", top_k=3)

# 直接运行测试
python3 ~/.vectorbrain/connector/vector_search.py
"""

import sqlite3
import json
import numpy as np
import subprocess
import faiss
from pathlib import Path
from typing import List, Dict, Optional

# VectorBrain 路径
VECTORBRAIN_ROOT = Path.home() / '.vectorbrain'
KNOWLEDGE_DB = VECTORBRAIN_ROOT / 'memory' / 'knowledge_memory.db'
INDEX_PATH = VECTORBRAIN_ROOT / 'memory' / 'knowledge.index'

# 全局加载 FAISS 索引到内存（常驻内存，毫秒级检索）
memory_index: Optional[faiss.Index] = None
try:
    memory_index = faiss.read_index(str(INDEX_PATH))
    print(f"✅ FAISS 索引已加载：{INDEX_PATH}")
except Exception as e:
    print(f"⚠️ FAISS 索引未找到或加载失败：{e}")
    print("   请先运行：python3 ~/.vectorbrain/connector/faiss_manager.py")

def get_ollama_embedding(text: str) -> np.ndarray:
    """
    调用 Ollama 生成文本向量（使用 bge-m3 多语言模型）
    
    Args:
        text: 输入文本
        
    Returns:
        numpy 向量数组
    """
    try:
        result = subprocess.run(
            ['ollama', 'run', 'bge-m3', text],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            vector = json.loads(result.stdout.strip())
            return np.array(vector)
        else:
            raise Exception(f"ollama run 失败：{result.stderr[:100]}")
            
    except subprocess.TimeoutExpired:
        raise Exception("Ollama 请求超时")

def search_memory(
    query: str, 
    db_path: str = str(KNOWLEDGE_DB), 
    top_k: int = 3,
    min_score: float = 0.0
) -> List[Dict]:
    """
    FAISS 加速向量检索 VectorBrain 记忆
    
    Args:
        query: 查询文本（如"上次那个备份的事"）
        db_path: 数据库路径
        top_k: 返回最相关的 K 条结果
        min_score: 最低相似度阈值（低于此分数的结果不返回）
        
    Returns:
        匹配结果列表，按相似度降序排列
    """
    print(f"⚡ 启动 FAISS 极速检索：'{query}'\n")
    
    if memory_index is None:
        print("❌ FAISS 索引未就绪，请先运行 faiss_manager.py")
        return []
    
    # 1. 生成查询向量
    print("步骤 1: 生成查询向量...")
    query_vector = get_ollama_embedding(query)
    print(f"✅ 查询向量维度：{len(query_vector)}")
    print()
    
    # 2. 转换矩阵并归一化
    q_vec = np.array([query_vector], dtype=np.float32)
    faiss.normalize_L2(q_vec)
    
    # 3. FAISS 底层 C++ 检索 (毫秒级)
    print("步骤 2: FAISS 极速检索...")
    scores, ids = memory_index.search(q_vec, top_k)
    print(f"✅ FAISS 检索完成")
    print()
    
    # 4. 根据命中的 ID 反查 SQLite 提取文本
    print("步骤 3: 从 SQLite 提取文本内容...")
    results = []
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for i in range(top_k):
        record_id = int(ids[0][i])
        score = float(scores[0][i])
        
        if record_id == -1 or score < min_score:
            continue
        
        cursor.execute("SELECT category, key, value FROM knowledge WHERE id = ?", (record_id,))
        row = cursor.fetchone()
        if row:
            results.append({
                "id": record_id,
                "category": row[0],
                "key": row[1],
                "value": row[2][:200] + "..." if len(row[2]) > 200 else row[2],
                "score": score
            })
    
    conn.close()
    print(f"✅ 提取完成")
    print()
    
    # 输出结果
    print("=" * 70)
    print(f"📊 检索完成！返回 Top-{len(results)} 结果")
    print("=" * 70)
    
    for i, res in enumerate(results, 1):
        print()
        print(f"[{i}] 匹配度：{res['score']:.4f} | 标签：{res['category']} / {res['key']}")
        print(f"    内容预览：{res['value'][:100]}...")
    
    print()
    
    return results

def quick_search(query: str, top_k: int = 3) -> List[Dict]:
    """
    快速搜索（简化版，无详细输出）
    
    Args:
        query: 查询文本
        top_k: 返回结果数量
        
    Returns:
        匹配结果列表
    """
    return search_memory(query, top_k=top_k)

# ===== 测试入口 =====
if __name__ == "__main__":
    import sys
    
    # 如果命令行传入参数，只搜索该查询
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"🔍 搜索：'{query}'\n")
        results = search_memory(query, top_k=3)
        
        if results:
            print(f"\n✅ 找到 {len(results)} 条相关记忆")
            for i, res in enumerate(results, 1):
                print(f"\n[{i}] 匹配度：{res['score']:.4f} | {res['category']} / {res['key']}")
                print(f"    {res['value'][:200]}...")
        else:
            print("\n⚠️  未找到相关记忆")
        
        sys.exit(0)
    
    # 否则运行默认测试
    print("=" * 70)
    print("🧪 VectorBrain 向量检索测试")
    print("=" * 70)
    print()
    
    # 测试查询（使用模糊的、口语化的提问）
    test_queries = [
        "上次那个系统备份的经验是什么？",  # 应该匹配 backup_procedure
        "帮我看看股票",  # 应该匹配 Stock 002599
        "健豪平时的习惯有哪些？",  # 应该匹配 学习健豪的习惯记录
        "怎么修改配置文件",  # 应该匹配 openclaw.json 修改规则
        "有机会提醒吗",  # 应该匹配 opportunity_scan_log
    ]
    
    print(f"准备测试 {len(test_queries)} 个查询...")
    print()
    
    for i, query in enumerate(test_queries, 1):
        print()
        print(f"{'='*70}")
        print(f"测试 [{i}/{len(test_queries)}]: '{query}'")
        print(f"{'='*70}")
        print()
        
        try:
            top_results = search_memory(query, top_k=2)
            
            if top_results:
                print(f"✅ 最佳匹配：{top_results[0]['key']} (分数：{top_results[0]['score']:.4f})")
            else:
                print("⚠️  未找到匹配结果")
                
        except Exception as e:
            print(f"❌ 错误：{e}")
        
        print()
    
    print()
    print("=" * 70)
    print("🎉 全部测试完成！")
    print("=" * 70)
    print()
    print("下一步：")
    print("1. 检查匹配结果是否符合预期")
    print("2. 如果效果好，修改 boot.md 的记忆注入逻辑")
    print("3. 将成功经验写入 VectorBrain")
