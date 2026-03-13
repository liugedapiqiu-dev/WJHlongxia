#!/usr/bin/env python3
"""
VectorBrain Goal Manager - 目标管理
管理目标的创建、拆解、跟踪
"""

import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# VectorBrain 根目录
VECTORBRAIN_ROOT = Path.home() / '.vectorbrain'
GOALS_DIR = VECTORBRAIN_ROOT / 'goals'

class GoalManager:
    """目标管理器"""
    
    def __init__(self):
        """初始化目标管理器"""
        # 确保目录存在
        GOALS_DIR.mkdir(parents=True, exist_ok=True)
        
        # 数据库路径
        self.db_path = GOALS_DIR / 'goals.db'
        
        # 初始化数据库
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 目标表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                goal_id TEXT PRIMARY KEY,
                goal_text TEXT NOT NULL,
                priority INTEGER DEFAULT 5,
                status TEXT DEFAULT 'active',
                parent_goal_id TEXT,
                created_by TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                completed_at TEXT,
                result TEXT
            )
        ''')
        
        # 子任务表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subtasks (
                task_id TEXT PRIMARY KEY,
                goal_id TEXT NOT NULL,
                task_text TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                priority INTEGER DEFAULT 5,
                assigned_worker TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                completed_at TEXT,
                result TEXT,
                FOREIGN KEY (goal_id) REFERENCES goals(goal_id)
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_goal_status ON goals(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_subtask_goal ON subtasks(goal_id)')
        
        conn.commit()
        conn.close()
    
    def create_goal(self, goal_text: str, priority: int = 5, 
                    created_by: str = '') -> str:
        """
        创建目标
        
        Args:
            goal_text: 目标描述
            priority: 优先级 (1-10, 1 最高)
            created_by: 创建者 worker ID
            
        Returns:
            goal_id
        """
        goal_id = f"goal_{uuid.uuid4().hex[:8]}"
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO goals (goal_id, goal_text, priority, created_by, status)
            VALUES (?, ?, ?, ?, 'active')
        ''', (goal_id, goal_text, priority, created_by))
        conn.commit()
        conn.close()
        
        return goal_id
    
    def add_subtask(self, goal_id: str, task_text: str, 
                    priority: int = 5, assigned_worker: str = None) -> str:
        """
        添加子任务
        
        Args:
            goal_id: 目标 ID
            task_text: 任务描述
            priority: 优先级
            assigned_worker: 分配给的 worker
            
        Returns:
            task_id
        """
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO subtasks (task_id, goal_id, task_text, priority, assigned_worker)
            VALUES (?, ?, ?, ?, ?)
        ''', (task_id, goal_id, task_text, priority, assigned_worker))
        conn.commit()
        conn.close()
        
        return task_id
    
    def get_goal(self, goal_id: str) -> Optional[Dict]:
        """获取目标详情（包含子任务）"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 获取目标
        cursor.execute('SELECT * FROM goals WHERE goal_id = ?', (goal_id,))
        goal_row = cursor.fetchone()
        
        if not goal_row:
            conn.close()
            return None
        
        goal = dict(goal_row)
        
        # 获取子任务
        cursor.execute('''
            SELECT * FROM subtasks 
            WHERE goal_id = ? 
            ORDER BY priority ASC, created_at ASC
        ''', (goal_id,))
        
        goal['subtasks'] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return goal
    
    def get_active_goals(self) -> List[Dict]:
        """获取所有活跃目标"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM goals 
            WHERE status = 'active' 
            ORDER BY priority ASC, created_at DESC
        ''')
        
        goals = []
        for row in cursor.fetchall():
            goal = dict(row)
            
            # 获取子任务统计
            cursor.execute('''
                SELECT status, COUNT(*) as count 
                FROM subtasks 
                WHERE goal_id = ? 
                GROUP BY status
            ''', (goal['goal_id'],))
            
            goal['subtask_stats'] = {r['status']: r['count'] for r in cursor.fetchall()}
            
            goals.append(goal)
        
        conn.close()
        
        return goals
    
    def complete_goal(self, goal_id: str, result: str = '') -> bool:
        """完成目标"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE goals 
            SET status = 'completed',
                completed_at = ?,
                result = ?,
                updated_at = ?
            WHERE goal_id = ?
        ''', (datetime.utcnow().isoformat(), result, datetime.utcnow().isoformat(), goal_id))
        
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return updated
    
    def get_stats(self) -> Dict:
        """获取目标统计"""
        stats = {}
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 目标统计
        cursor.execute('''
            SELECT status, COUNT(*) as count 
            FROM goals 
            GROUP BY status
        ''')
        stats['goals_by_status'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        cursor.execute('SELECT COUNT(*) FROM goals')
        stats['total_goals'] = cursor.fetchone()[0]
        
        # 子任务统计
        cursor.execute('''
            SELECT status, COUNT(*) as count 
            FROM subtasks 
            GROUP BY status
        ''')
        stats['subtasks_by_status'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        cursor.execute('SELECT COUNT(*) FROM subtasks')
        stats['total_subtasks'] = cursor.fetchone()[0]
        
        conn.close()
        
        return stats
    
    def __repr__(self):
        stats = self.get_stats()
        return f"GoalManager(goals={stats['total_goals']}, subtasks={stats['total_subtasks']})"


# 单例模式
_goal_manager_instance = None

def get_goal_manager() -> GoalManager:
    """获取目标管理器单例"""
    global _goal_manager_instance
    if _goal_manager_instance is None:
        _goal_manager_instance = GoalManager()
    return _goal_manager_instance


if __name__ == "__main__":
    # 测试
    gm = get_goal_manager()
    print(f"Goal Manager initialized: {gm}")
    print(f"Stats: {gm.get_stats()}")
    
    # 创建测试目标
    goal_id = gm.create_goal(
        goal_text="开发一个 ERP 系统",
        priority=1,
        created_by="system_init"
    )
    print(f"\nCreated goal: {goal_id}")
    
    # 添加子任务
    gm.add_subtask(goal_id, "需求分析", priority=1)
    gm.add_subtask(goal_id, "技术选型", priority=2)
    gm.add_subtask(goal_id, "架构设计", priority=2)
    gm.add_subtask(goal_id, "数据库设计", priority=3)
    gm.add_subtask(goal_id, "API 开发", priority=3)
    
    print(f"Stats after create: {gm.get_stats()}")
    
    # 获取目标详情
    goal = gm.get_goal(goal_id)
    print(f"\nGoal: {goal['goal_text']}")
    print("Subtasks:")
    for task in goal['subtasks']:
        print(f"  - {task['task_text']} (priority: {task['priority']})")
