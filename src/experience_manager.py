#!/usr/bin/env python3
"""
VectorBrain Experience Manager
中央大脑经验管理模块

所有 AI 实例共享同一个经验库
记录错误模式、解决方案、最佳实践
"""

import os
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# VectorBrain 根目录
VECTORBRAIN_ROOT = Path.home() / '.vectorbrain'
EXPERIENCE_DIR = VECTORBRAIN_ROOT / 'experience'

class ExperienceManager:
    """经验管理器 - 所有 AI 实例共享"""
    
    def __init__(self):
        """初始化经验管理器"""
        # 确保目录存在
        EXPERIENCE_DIR.mkdir(parents=True, exist_ok=True)
        
        # 数据库路径
        self.db_path = EXPERIENCE_DIR / 'error_patterns.db'
        
        # 初始化数据库
        self._init_database()
    
    def _init_database(self):
        """初始化经验数据库"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS error_patterns (
                error_id TEXT PRIMARY KEY,
                pattern TEXT NOT NULL,
                solution TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                occurrence_count INTEGER DEFAULT 1,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                category TEXT DEFAULT 'general',
                tags TEXT,
                source_worker TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_used_at TEXT
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pattern ON error_patterns(pattern)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON error_patterns(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_confidence ON error_patterns(confidence)')
        
        conn.commit()
        conn.close()
    
    def record_error(self, pattern: str, solution: str, 
                     category: str = 'general', source_worker: str = '',
                     tags: List[str] = None) -> str:
        """
        记录错误模式
        
        Args:
            pattern: 错误模式描述
            solution: 解决方案
            category: 错误分类
            source_worker: 报告错误的 worker ID
            tags: 标签列表
            
        Returns:
            error_id
        """
        error_id = f"error_{uuid.uuid4().hex[:8]}"
        tags_json = ','.join(tags) if tags else ''
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 检查是否已存在相似模式
        cursor.execute('''
            SELECT error_id, occurrence_count 
            FROM error_patterns 
            WHERE pattern LIKE ?
        ''', (f'%{pattern[:50]}%',))
        
        existing = cursor.fetchone()
        
        if existing:
            # 已存在，增加出现次数
            error_id = existing[0]
            cursor.execute('''
                UPDATE error_patterns 
                SET occurrence_count = occurrence_count + 1,
                    updated_at = ?
                WHERE error_id = ?
            ''', (datetime.utcnow().isoformat(), error_id))
        else:
            # 新错误模式
            cursor.execute('''
                INSERT INTO error_patterns 
                (error_id, pattern, solution, category, source_worker, tags)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (error_id, pattern, solution, category, source_worker, tags_json))
        
        conn.commit()
        conn.close()
        
        return error_id
    
    def record_outcome(self, error_id: str, success: bool) -> bool:
        """
        记录解决方案的结果
        
        Args:
            error_id: 错误 ID
            success: 是否成功解决
            
        Returns:
            是否更新成功
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        if success:
            cursor.execute('''
                UPDATE error_patterns 
                SET success_count = success_count + 1,
                    confidence = MIN(1.0, confidence + 0.1),
                    last_used_at = ?,
                    updated_at = ?
                WHERE error_id = ?
            ''', (datetime.utcnow().isoformat(), datetime.utcnow().isoformat(), error_id))
        else:
            cursor.execute('''
                UPDATE error_patterns 
                SET failure_count = failure_count + 1,
                    confidence = MAX(0.0, confidence - 0.1),
                    last_used_at = ?,
                    updated_at = ?
                WHERE error_id = ?
            ''', (datetime.utcnow().isoformat(), datetime.utcnow().isoformat(), error_id))
        
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return updated
    
    def get_solution(self, pattern: str) -> Optional[Dict]:
        """
        根据错误模式获取解决方案
        
        Args:
            pattern: 错误模式描述
            
        Returns:
            匹配的解决方案
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM error_patterns 
            WHERE pattern LIKE ?
            ORDER BY confidence DESC, success_count DESC
            LIMIT 1
        ''', (f'%{pattern[:50]}%',))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            result = dict(row)
            result['tags'] = result['tags'].split(',') if result['tags'] else []
            return result
        return None
    
    def get_best_practices(self, category: str = None, limit: int = 10) -> List[Dict]:
        """
        获取最佳实践
        
        Args:
            category: 分类过滤
            limit: 返回数量
            
        Returns:
            最佳实践列表
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if category:
            cursor.execute('''
                SELECT * FROM error_patterns 
                WHERE category = ?
                ORDER BY confidence DESC, success_count DESC
                LIMIT ?
            ''', (category, limit))
        else:
            cursor.execute('''
                SELECT * FROM error_patterns 
                ORDER BY confidence DESC, success_count DESC
                LIMIT ?
            ''', (limit,))
        
        practices = []
        for row in cursor.fetchall():
            result = dict(row)
            result['tags'] = result['tags'].split(',') if result['tags'] else []
            practices.append(result)
        
        conn.close()
        
        return practices
    
    def get_stats(self) -> Dict:
        """获取经验统计信息"""
        stats = {}
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 总错误模式数
        cursor.execute('SELECT COUNT(*) FROM error_patterns')
        stats['total_patterns'] = cursor.fetchone()[0]
        
        # 按分类统计
        cursor.execute('''
            SELECT category, COUNT(*) as count 
            FROM error_patterns 
            GROUP BY category
        ''')
        stats['by_category'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 高置信度模式数
        cursor.execute('SELECT COUNT(*) FROM error_patterns WHERE confidence > 0.8')
        stats['high_confidence'] = cursor.fetchone()[0]
        
        # 平均成功率
        cursor.execute('''
            SELECT AVG(CAST(success_count AS FLOAT) / 
                       (success_count + failure_count + 0.001)) 
            FROM error_patterns
        ''')
        stats['avg_success_rate'] = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return stats
    
    def __repr__(self):
        stats = self.get_stats()
        return f"ExperienceManager(patterns={stats['total_patterns']}, high_confidence={stats['high_confidence']})"


# 单例模式
_experience_manager_instance = None

def get_experience_manager() -> ExperienceManager:
    """获取经验管理器单例"""
    global _experience_manager_instance
    if _experience_manager_instance is None:
        _experience_manager_instance = ExperienceManager()
    return _experience_manager_instance


if __name__ == "__main__":
    # 测试
    em = get_experience_manager()
    print(f"Experience Manager initialized: {em}")
    print(f"Stats: {em.get_stats()}")
    
    # 记录测试错误
    error_id = em.record_error(
        pattern="技能打包忘记添加 README.md",
        solution="打包后立即执行 unzip -l 检查内容",
        category="packaging",
        source_worker="system_init",
        tags=["packaging", "skills", "verification"]
    )
    print(f"Recorded error: {error_id}")
    
    # 记录成功结果
    em.record_outcome(error_id, success=True)
    print(f"Recorded successful outcome")
    
    print(f"Stats after record: {em.get_stats()}")
    
    # 查询解决方案
    solution = em.get_solution("打包忘记")
    print(f"Found solution: {solution['solution'] if solution else 'None'}")
