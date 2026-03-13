#!/usr/bin/env python3
"""
VectorBrain Dashboard Server v3 - MOS 现代毛玻璃风格指挥中心

功能升级：
1. MOS 现代设计风格（毛玻璃 + 渐变 + 动画）
2. 全中文界面 + Emoji 图标
3. 实时数据可视化（Chart.js 图表）
4. 任务队列状态监控
5. 记忆/经验/反思 统计
6. 会话关系网络图
7. 系统资源监控
"""

import os
import sys
import json
import psutil
import sqlite3
import re
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template_string, send_from_directory
from flask_socketio import SocketIO, emit
import threading
import time
import glob

# VectorBrain 目录
VECTORBRAIN_DIR = Path.home() / '.vectorbrain'
LOG_FILE = VECTORBRAIN_DIR / 'agent_core.log'
FEISHU_LOG = VECTORBRAIN_DIR / 'feishu_messages.log'
OPENCLAW_LOG = Path('/tmp/openclaw/openclaw-' + datetime.now().strftime('%Y-%m-%d') + '.log')

# 数据库路径
DB_PATHS = {
    'tasks': VECTORBRAIN_DIR / 'tasks' / 'task_queue.db',
    'memory_episodic': VECTORBRAIN_DIR / 'memory' / 'episodic_memory.db',
    'memory_knowledge': VECTORBRAIN_DIR / 'memory' / 'knowledge_memory.db',
    'experience': VECTORBRAIN_DIR / 'experience' / 'error_patterns.db',
    'goals': VECTORBRAIN_DIR / 'goals' / 'goals.db',
    'reflection': VECTORBRAIN_DIR / 'reflection' / 'reflections.db',
    'opportunity': VECTORBRAIN_DIR / 'opportunity' / 'opportunities.db'
}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'VectorBrain_Dashboard_v3_2026'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# 指挥中心状态
dashboard_state = {
    'loop_ticks': 0,
    'tasks_pending': 0,
    'tasks_completed': 0,
    'tasks_total': 0,
    'memories_episodic': 0,
    'memories_knowledge': 0,
    'memories_total': 0,
    'experiences_total': 0,
    'goals_active': 0,
    'goals_completed': 0,
    'reflections_count': 0,
    'opportunities_count': 0,
    'system_health': 'healthy',
    'cpu_usage': 0.0,
    'memory_usage': 0.0,
    'disk_usage': 0.0,
    'uptime_hours': 0,
    'last_update': None,
    'recent_logs': [],
    'recent_reflections': [],
    'feishu_messages': [],
    'message_count': 0,
    'task_queue': [],
    'active_sessions': [],
    'token_stats': {
        'today_input': 0,
        'today_output': 0,
        'today_total': 0
    }
}

def get_db_count(db_path: Path) -> int:
    """获取数据库记录总数"""
    if not db_path.exists():
        return 0
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        total = 0
        for (table_name,) in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                total += cursor.fetchone()[0]
            except:
                pass
        conn.close()
        return total
    except:
        return 0

def get_task_queue_status() -> dict:
    """获取任务队列状态"""
    db_path = DB_PATHS['tasks']
    if not db_path.exists():
        return {'pending': 0, 'running': 0, 'completed': 0, 'failed': 0}
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        stats = {'pending': 0, 'running': 0, 'completed': 0, 'failed': 0}
        for (table_name,) in tables:
            try:
                cursor.execute(f"SELECT status, COUNT(*) FROM {table_name} GROUP BY status")
                for status, count in cursor.fetchall():
                    if status in stats:
                        stats[status] += count
            except:
                pass
        
        conn.close()
        return stats
    except:
        return {'pending': 0, 'running': 0, 'completed': 0, 'failed': 0}

def get_recent_logs(lines: int = 20) -> list:
    """获取最近日志"""
    if not LOG_FILE.exists():
        return []
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines()[-lines:]]
    except:
        return []

def get_recent_reflections() -> list:
    """获取最近反思"""
    db_path = DB_PATHS['reflection']
    if not db_path.exists():
        return []
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reflections ORDER BY created_at DESC LIMIT 10")
        reflections = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return reflections
    except:
        return []

def get_feishu_messages(lines: int = 20) -> list:
    """获取飞书消息"""
    if not FEISHU_LOG.exists():
        return []
    try:
        with open(FEISHU_LOG, 'r', encoding='utf-8') as f:
            messages = []
            for line in f.readlines()[-lines:]:
                if line.strip():
                    try:
                        parts = line.strip().split(' | ', 2)
                        if len(parts) >= 3:
                            messages.append({
                                'timestamp': parts[0],
                                'user': parts[1],
                                'content': parts[2]
                            })
                    except:
                        pass
            return messages
    except:
        return []

def get_goals_status() -> dict:
    """获取目标状态"""
    db_path = DB_PATHS['goals']
    if not db_path.exists():
        return {'active': 0, 'completed': 0}
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        stats = {'active': 0, 'completed': 0}
        for (table_name,) in tables:
            try:
                cursor.execute(f"SELECT status, COUNT(*) FROM {table_name} GROUP BY status")
                for status, count in cursor.fetchall():
                    if 'active' in status.lower() or status == 'active':
                        stats['active'] += count
                    elif 'completed' in status.lower() or status == 'completed':
                        stats['completed'] += count
            except:
                pass
        
        conn.close()
        return stats
    except:
        return {'active': 0, 'completed': 0}

def update_dashboard_state():
    """更新指挥中心状态"""
    try:
        # 系统资源
        dashboard_state['cpu_usage'] = psutil.cpu_percent(interval=1)
        dashboard_state['memory_usage'] = psutil.virtual_memory().percent
        dashboard_state['disk_usage'] = psutil.disk_usage('/').percent
        
        # 数据库统计
        dashboard_state['memories_episodic'] = get_db_count(DB_PATHS['memory_episodic'])
        dashboard_state['memories_knowledge'] = get_db_count(DB_PATHS['memory_knowledge'])
        dashboard_state['memories_total'] = dashboard_state['memories_episodic'] + dashboard_state['memories_knowledge']
        dashboard_state['experiences_total'] = get_db_count(DB_PATHS['experience'])
        
        # 目标状态
        goals_stats = get_goals_status()
        dashboard_state['goals_active'] = goals_stats['active']
        dashboard_state['goals_completed'] = goals_stats['completed']
        
        # 反思数量
        dashboard_state['reflections_count'] = get_db_count(DB_PATHS['reflection'])
        
        # 机会数量
        dashboard_state['opportunities_count'] = get_db_count(DB_PATHS['opportunity'])
        
        # 任务队列状态
        task_stats = get_task_queue_status()
        dashboard_state['tasks_pending'] = task_stats['pending']
        dashboard_state['tasks_completed'] = task_stats['completed']
        dashboard_state['tasks_total'] = sum(task_stats.values())
        dashboard_state['task_queue'] = task_stats
        
        # 飞书消息
        dashboard_state['feishu_messages'] = get_feishu_messages()
        dashboard_state['message_count'] = len(dashboard_state['feishu_messages'])
        
        # 最近日志
        dashboard_state['recent_logs'] = get_recent_logs()
        
        # 最近反思
        dashboard_state['recent_reflections'] = get_recent_reflections()
        
        # Loop ticks（从日志中解析）
        if dashboard_state['recent_logs']:
            dashboard_state['loop_ticks'] = len([l for l in dashboard_state['recent_logs'] if 'LOOP_TICK' in l])
        
        # 系统健康状态
        if dashboard_state['cpu_usage'] > 90 or dashboard_state['memory_usage'] > 90:
            dashboard_state['system_health'] = 'critical'
        elif dashboard_state['cpu_usage'] > 70 or dashboard_state['memory_usage'] > 70:
            dashboard_state['system_health'] = 'warning'
        else:
            dashboard_state['system_health'] = 'healthy'
        
        dashboard_state['last_update'] = datetime.now().isoformat()
        
    except Exception as e:
        print(f"更新状态失败：{e}")

def background_updater():
    """后台更新线程"""
    while True:
        update_dashboard_state()
        socketio.emit('state_update', dashboard_state)
        time.sleep(2)

