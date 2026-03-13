#!/usr/bin/env python3
"""
VectorBrain Memory Manager
中央大脑记忆管理模块

所有 AI 实例共享同一个记忆系统
"""

import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# VectorBrain 根目录
VECTORBRAIN_ROOT = Path.home() / '.vectorbrain'
MEMORY_DIR = VECTORBRAIN_ROOT / 'memory'

class MemoryManager:
    """记忆管理器 - 所有 AI 实例共享"""
    
    def __init__(self):
        """初始化记忆管理器"""
        # 确保目录存在
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        
        # 数据库路径
        self.episodic_db = MEMORY_DIR / 'episodic_memory.db'
        self.knowledge_db = MEMORY_DIR / 'knowledge_memory.db'
        
        # 初始化数据库
        self._init_databases()
    
    def _init_databases(self):
        """初始化数据库"""
        # 情景记忆数据库
        conn = sqlite3.connect(str(self.episodic_db))
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                worker_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON episodes(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_worker ON episodes(worker_id)')
        conn.commit()
        conn.close()
        
        # 知识记忆数据库
        conn = sqlite3.connect(str(self.knowledge_db))
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                source_worker TEXT,
                confidence REAL DEFAULT 1.0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_category_key ON knowledge(category, key)')
        conn.commit()
        conn.close()
    
    def load_memory(self, memory_type: str = 'all', limit: int = 100) -> List[Dict]:
        """
        加载记忆
        
        Args:
            memory_type: 'episodic', 'knowledge', 或 'all'
            limit: 返回数量限制
            
        Returns:
            记忆列表
        """
        memories = []
        
        if memory_type in ['episodic', 'all']:
            conn = sqlite3.connect(str(self.episodic_db))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM episodes 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            for row in cursor.fetchall():
                memories.append({
                    'type': 'episodic',
                    'id': row['id'],
                    'timestamp': row['timestamp'],
                    'worker_id': row['worker_id'],
                    'event_type': row['event_type'],
                    'content': row['content'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else None,
                    'created_at': row['created_at']
                })
            
            conn.close()
        
        if memory_type in ['knowledge', 'all']:
            conn = sqlite3.connect(str(self.knowledge_db))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM knowledge 
                ORDER BY updated_at DESC 
                LIMIT ?
            ''', (limit,))
            
            for row in cursor.fetchall():
                memories.append({
                    'type': 'knowledge',
                    'id': row['id'],
                    'category': row['category'],
                    'key': row['key'],
                    'value': row['value'],
                    'source_worker': row['source_worker'],
                    'confidence': row['confidence'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                })
            
            conn.close()
        
        return memories
    
    def save_memory(self, memory_type: str, content: Dict, worker_id: str) -> int:
        """
        保存记忆
        
        Args:
            memory_type: 'episodic' 或 'knowledge'
            content: 记忆内容
            worker_id: 保存记忆的 worker ID
            
        Returns:
            记忆 ID
        """
        if memory_type == 'episodic':
            conn = sqlite3.connect(str(self.episodic_db))
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO episodes (timestamp, worker_id, event_type, content, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                content.get('timestamp', datetime.utcnow().isoformat()),
                worker_id,
                content.get('event_type', 'general'),
                content.get('content', ''),
                json.dumps(content.get('metadata')) if content.get('metadata') else None
            ))
            memory_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return memory_id
        
        elif memory_type == 'knowledge':
            conn = sqlite3.connect(str(self.knowledge_db))
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO knowledge 
                (category, key, value, source_worker, confidence, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                content.get('category', 'general'),
                content.get('key'),
                content.get('value', ''),
                worker_id,
                content.get('confidence', 1.0),
                datetime.utcnow().isoformat()
            ))
            memory_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return memory_id
        
        else:
            raise ValueError(f"Unknown memory type: {memory_type}")
    
    def search_memory(self, query: str, memory_type: str = 'all') -> List[Dict]:
        """
        搜索记忆
        
        Args:
            query: 搜索关键词
            memory_type: 'episodic', 'knowledge', 或 'all'
            
        Returns:
            匹配的记忆列表
        """
        # TODO: 未来集成向量搜索
        # 当前使用简单的 SQL LIKE 搜索
        memories = []
        
        if memory_type in ['episodic', 'all']:
            conn = sqlite3.connect(str(self.episodic_db))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM episodes 
                WHERE content LIKE ? OR event_type LIKE ?
                ORDER BY timestamp DESC
                LIMIT 50
            ''', (f'%{query}%', f'%{query}%'))
            
            for row in cursor.fetchall():
                memories.append({
                    'type': 'episodic',
                    'id': row['id'],
                    'timestamp': row['timestamp'],
                    'worker_id': row['worker_id'],
                    'event_type': row['event_type'],
                    'content': row['content'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else None
                })
            
            conn.close()
        
        if memory_type in ['knowledge', 'all']:
            conn = sqlite3.connect(str(self.knowledge_db))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM knowledge 
                WHERE key LIKE ? OR value LIKE ? OR category LIKE ?
                ORDER BY updated_at DESC
                LIMIT 50
            ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
            
            for row in cursor.fetchall():
                memories.append({
                    'type': 'knowledge',
                    'id': row['id'],
                    'category': row['category'],
                    'key': row['key'],
                    'value': row['value'],
                    'source_worker': row['source_worker'],
                    'confidence': row['confidence']
                })
            
            conn.close()
        
        return memories
    
    def get_stats(self) -> Dict:
        """获取记忆统计信息"""
        stats = {}
        
        # 情景记忆统计
        conn = sqlite3.connect(str(self.episodic_db))
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM episodes')
        stats['episodic_count'] = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(DISTINCT worker_id) FROM episodes')
        stats['episodic_workers'] = cursor.fetchone()[0]
        conn.close()
        
        # 知识记忆统计
        conn = sqlite3.connect(str(self.knowledge_db))
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM knowledge')
        stats['knowledge_count'] = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(DISTINCT category) FROM knowledge')
        stats['knowledge_categories'] = cursor.fetchone()[0]
        conn.close()
        
        return stats
    
    def __repr__(self):
        stats = self.get_stats()
        return f"MemoryManager(episodic={stats['episodic_count']}, knowledge={stats['knowledge_count']})"


# 单例模式
_memory_manager_instance = None

def get_memory_manager() -> MemoryManager:
    """获取记忆管理器单例"""
    global _memory_manager_instance
    if _memory_manager_instance is None:
        _memory_manager_instance = MemoryManager()
    return _memory_manager_instance


if __name__ == "__main__":
    # 测试
    mm = get_memory_manager()
    print(f"Memory Manager initialized: {mm}")
    print(f"Stats: {mm.get_stats()}")
