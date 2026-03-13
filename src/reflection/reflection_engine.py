#!/usr/bin/env python3
"""
VectorBrain Reflection Engine - 反思引擎
分析任务结果，提取经验教训
"""

import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# VectorBrain 根目录
VECTORBRAIN_ROOT = Path.home() / '.vectorbrain'
REFLECTION_DIR = VECTORBRAIN_ROOT / 'reflection'

class ReflectionEngine:
    """反思引擎"""
    
    def __init__(self):
        """初始化反思引擎"""
        # 确保目录存在
        REFLECTION_DIR.mkdir(parents=True, exist_ok=True)
        
        # 数据库路径
        self.db_path = REFLECTION_DIR / 'reflections.db'
        
        # 初始化数据库
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 反思记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reflections (
                reflection_id TEXT PRIMARY KEY,
                task_id TEXT,
                goal_id TEXT,
                outcome TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                analysis TEXT,
                lessons_learned TEXT,
                action_items TEXT,
                created_by TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_task ON reflections(task_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_outcome ON reflections(outcome)')
        
        conn.commit()
        conn.close()
    
    def reflect(self, task_id: str = None, goal_id: str = None,
                outcome: str = '', success: bool = True,
                analysis: str = '', created_by: str = '') -> str:
        """
        进行反思
        
        Args:
            task_id: 任务 ID
            goal_id: 目标 ID
            outcome: 结果描述
            success: 是否成功
            analysis: 分析内容
            created_by: 创建者 worker ID
            
        Returns:
            reflection_id
        """
        reflection_id = f"reflection_{uuid.uuid4().hex[:8]}"
        
        # 提取经验教训（简单实现：从分析中提取关键点）
        lessons = self._extract_lessons(analysis, success)
        
        # 生成行动项
        action_items = self._generate_action_items(lessons, success)
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO reflections 
            (reflection_id, task_id, goal_id, outcome, success, analysis, lessons_learned, action_items, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (reflection_id, task_id, goal_id, outcome, success, analysis, lessons, action_items, created_by))
        conn.commit()
        conn.close()
        
        return reflection_id
    
    def _extract_lessons(self, analysis: str, success: bool) -> str:
        """从分析中提取经验教训"""
        lessons = []
        
        if success:
            lessons.append("✅ 成功的做法应该保持")
            if "分析" in analysis or "研究" in analysis:
                lessons.append("✅ 充分的准备是成功的关键")
            if "测试" in analysis:
                lessons.append("✅ 测试验证避免了潜在问题")
        else:
            lessons.append("❌ 需要改进的地方")
            if "失败" in analysis or "错误" in analysis:
                lessons.append("❌ 需要建立错误预防机制")
            if "时间" in analysis:
                lessons.append("❌ 时间管理需要优化")
        
        return '\n'.join(lessons)
    
    def _generate_action_items(self, lessons: str, success: bool) -> str:
        """生成行动项"""
        actions = []
        
        if success:
            actions.append("📝 记录最佳实践")
            actions.append("📝 分享给其他 Workers")
        else:
            actions.append("🔧 制定改进计划")
            actions.append("🔧 建立检查清单")
            actions.append("🔧 加入 ERROR_LOG_V1")
        
        return '\n'.join(actions)
    
    def get_reflections(self, task_id: str = None, 
                        limit: int = 10) -> List[Dict]:
        """获取反思记录"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if task_id:
            cursor.execute('''
                SELECT * FROM reflections 
                WHERE task_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (task_id, limit))
        else:
            cursor.execute('''
                SELECT * FROM reflections 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
        
        reflections = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return reflections
    
    def get_lessons_by_topic(self, topic: str) -> List[Dict]:
        """按主题获取经验教训"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM reflections 
            WHERE lessons_learned LIKE ? OR analysis LIKE ?
            ORDER BY created_at DESC
            LIMIT 20
        ''', (f'%{topic}%', f'%{topic}%'))
        
        lessons = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return lessons
    
    def get_stats(self) -> Dict:
        """获取反思统计"""
        stats = {}
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 总反思数
        cursor.execute('SELECT COUNT(*) FROM reflections')
        stats['total_reflections'] = cursor.fetchone()[0]
        
        # 按成功/失败统计
        cursor.execute('''
            SELECT success, COUNT(*) as count 
            FROM reflections 
            GROUP BY success
        ''')
        stats['by_outcome'] = {
            'success': 0,
            'failure': 0
        }
        for row in cursor.fetchall():
            key = 'success' if row[0] else 'failure'
            stats['by_outcome'][key] = row[1]
        
        # 成功率
        total = stats['by_outcome']['success'] + stats['by_outcome']['failure']
        stats['success_rate'] = f"{stats['by_outcome']['success']/total*100:.1f}%" if total > 0 else "N/A"
        
        conn.close()
        
        return stats
    
    def __repr__(self):
        stats = self.get_stats()
        return f"ReflectionEngine(reflections={stats['total_reflections']}, success_rate={stats['success_rate']})"


# 单例模式
_reflection_engine_instance = None

def get_reflection_engine() -> ReflectionEngine:
    """获取反思引擎单例"""
    global _reflection_engine_instance
    if _reflection_engine_instance is None:
        _reflection_engine_instance = ReflectionEngine()
    return _reflection_engine_instance


if __name__ == "__main__":
    # 测试
    re = get_reflection_engine()
    print(f"Reflection Engine initialized: {re}")
    print(f"Stats: {re.get_stats()}")
    
    # 测试反思
    print("\n测试 1: 成功的任务")
    ref_id = re.reflect(
        task_id="task_001",
        outcome="任务成功完成，抓取了 100 条数据",
        success=True,
        analysis="充分的 API 研究和测试验证确保了任务成功",
        created_by="worker_test_001"
    )
    print(f"Created reflection: {ref_id}")
    
    print("\n测试 2: 失败的任务")
    ref_id = re.reflect(
        task_id="task_002",
        outcome="任务失败，IP 被封",
        success=False,
        analysis="没有考虑反爬机制，请求频率过高导致 IP 被封",
        created_by="worker_test_001"
    )
    print(f"Created reflection: {ref_id}")
    
    print(f"\nStats after reflect: {re.get_stats()}")
    
    # 获取反思记录
    reflections = re.get_reflections()
    print(f"\nLatest reflections:")
    for ref in reflections:
        print(f"  - {ref['outcome'][:30]}... (success: {ref['success']})")
