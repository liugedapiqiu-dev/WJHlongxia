#!/usr/bin/env python3
"""
VectorBrain Task Manager
中央大脑任务管理模块

所有 AI 实例共享同一个任务队列
"""

import os
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# VectorBrain 根目录
VECTORBRAIN_ROOT = Path.home() / '.vectorbrain'
TASKS_DIR = VECTORBRAIN_ROOT / 'tasks'

class TaskManager:
    """任务管理器 - 所有 AI 实例共享"""
    
    def __init__(self):
        """初始化任务管理器"""
        # 确保目录存在
        TASKS_DIR.mkdir(parents=True, exist_ok=True)
        
        # 数据库路径
        self.db_path = TASKS_DIR / 'task_queue.db'
        
        # 初始化数据库
        self._init_database()
    
    def _init_database(self):
        """初始化任务数据库"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                priority INTEGER DEFAULT 5,
                status TEXT DEFAULT 'pending',
                assigned_worker TEXT,
                created_by TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                completed_at TEXT,
                result TEXT,
                error_message TEXT
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON tasks(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_priority ON tasks(priority)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_worker ON tasks(assigned_worker)')
        
        conn.commit()
        conn.close()
    
    def create_task(self, title: str, description: str = '', 
                    priority: int = 5, created_by: str = '') -> str:
        """
        创建新任务
        
        Args:
            title: 任务标题
            description: 任务描述
            priority: 优先级 (1-10, 1 最高)
            created_by: 创建者 worker ID
            
        Returns:
            task_id
        """
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tasks (task_id, title, description, priority, created_by, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
        ''', (task_id, title, description, priority, created_by))
        conn.commit()
        conn.close()
        
        return task_id
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """获取任务详情"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE task_id = ?', (task_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_pending_tasks(self, limit: int = 10) -> List[Dict]:
        """获取待处理任务"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM tasks 
            WHERE status = 'pending'
            ORDER BY priority ASC, created_at ASC
            LIMIT ?
        ''', (limit,))
        
        tasks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return tasks
    
    def assign_task(self, task_id: str, worker_id: str) -> bool:
        """分配任务给 worker"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE tasks 
            SET status = 'running', 
                assigned_worker = ?,
                updated_at = ?
            WHERE task_id = ? AND status = 'pending'
        ''', (worker_id, datetime.utcnow().isoformat(), task_id))
        
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return updated
    
    def complete_task(self, task_id: str, result: str = '') -> bool:
        """完成任务"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE tasks 
            SET status = 'done',
                completed_at = ?,
                result = ?,
                updated_at = ?
            WHERE task_id = ?
        ''', (datetime.utcnow().isoformat(), result, datetime.utcnow().isoformat(), task_id))
        
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return updated
    
    def fail_task(self, task_id: str, error_message: str) -> bool:
        """标记任务失败"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE tasks 
            SET status = 'failed',
                error_message = ?,
                updated_at = ?
            WHERE task_id = ?
        ''', (error_message, datetime.utcnow().isoformat(), task_id))
        
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return updated
    
    def get_stats(self) -> Dict:
        """获取任务统计信息"""
        stats = {}
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 按状态统计
        cursor.execute('''
            SELECT status, COUNT(*) as count 
            FROM tasks 
            GROUP BY status
        ''')
        stats['by_status'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 总任务数
        cursor.execute('SELECT COUNT(*) FROM tasks')
        stats['total'] = cursor.fetchone()[0]
        
        # 活跃 worker 数
        cursor.execute('SELECT COUNT(DISTINCT assigned_worker) FROM tasks WHERE status = "running"')
        stats['active_workers'] = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return stats
    
    def __repr__(self):
        stats = self.get_stats()
        return f"TaskManager(total={stats['total']}, pending={stats['by_status'].get('pending', 0)}, running={stats['by_status'].get('running', 0)})"


# 单例模式
_task_manager_instance = None

def get_task_manager() -> TaskManager:
    """获取任务管理器单例"""
    global _task_manager_instance
    if _task_manager_instance is None:
        _task_manager_instance = TaskManager()
    return _task_manager_instance


if __name__ == "__main__":
    # 测试
    tm = get_task_manager()
    print(f"Task Manager initialized: {tm}")
    print(f"Stats: {tm.get_stats()}")
    
    # 创建测试任务
    task_id = tm.create_task(
        title="测试任务",
        description="这是第一个测试任务",
        priority=1,
        created_by="system_init"
    )
    print(f"Created test task: {task_id}")
    print(f"Stats after create: {tm.get_stats()}")
