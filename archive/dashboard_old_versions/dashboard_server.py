#!/usr/bin/env python3
"""
VectorBrain Dashboard Server - 指挥舱后端

实时推送 VectorBrain 状态到前端

运行在 18790 端口
"""

import os
import sys
import json
import psutil
import sqlite3
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template_string, send_from_directory
from flask_socketio import SocketIO, emit
import threading
import time

# VectorBrain 目录
VECTORBRAIN_DIR = Path.home() / '.vectorbrain'
LOG_FILE = VECTORBRAIN_DIR / 'agent_core.log'

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

# 创建 Flask 应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'VectorBrain_Dashboard_Secret_Key_2026'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# 全局状态
dashboard_state = {
    'loop_ticks': 0,
    'tasks_pending': 0,
    'tasks_completed': 0,
    'memories_total': 0,
    'experiences_total': 0,
    'system_health': 'healthy',
    'cpu_usage': 0.0,
    'memory_usage': 0.0,
    'last_update': None,
    'recent_logs': [],
    'recent_reflections': [],
    'migration_progress': 100  # 迁移已完成
}

def get_db_count(db_path: Path) -> int:
    """获取数据库记录数"""
    if not db_path.exists():
        return 0
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        total = 0
        for (table_name,) in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                total += count
            except:
                pass
        
        conn.close()
        return total
    except Exception as e:
        return 0

def get_recent_logs(lines: int = 10) -> list:
    """获取最近的日志"""
    if not LOG_FILE.exists():
        return []
    
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            return [line.strip() for line in all_lines[-lines:]]
    except:
        return []

def get_recent_reflections() -> list:
    """获取最近的反思"""
    db_path = DB_PATHS['reflection']
    if not db_path.exists():
        return []
    
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reflections ORDER BY created_at DESC LIMIT 5")
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    except:
        return []

def update_state():
    """更新系统状态"""
    dashboard_state['loop_ticks'] += 1
    dashboard_state['tasks_pending'] = get_db_count(DB_PATHS['tasks'])
    dashboard_state['memories_total'] = (
        get_db_count(DB_PATHS['memory_episodic']) + 
        get_db_count(DB_PATHS['memory_knowledge'])
    )
    dashboard_state['experiences_total'] = get_db_count(DB_PATHS['experience'])
    dashboard_state['cpu_usage'] = psutil.cpu_percent(interval=1)
    dashboard_state['memory_usage'] = psutil.virtual_memory().percent
    dashboard_state['last_update'] = datetime.utcnow().isoformat()
    dashboard_state['recent_logs'] = get_recent_logs(10)
    dashboard_state['recent_reflections'] = get_recent_reflections()
    
    # 系统健康状态
    if dashboard_state['cpu_usage'] > 90 or dashboard_state['memory_usage'] > 90:
        dashboard_state['system_health'] = 'critical'
    elif dashboard_state['cpu_usage'] > 70 or dashboard_state['memory_usage'] > 70:
        dashboard_state['system_health'] = 'warning'
    else:
        dashboard_state['system_health'] = 'healthy'

def background_updater():
    """后台更新线程"""
    while True:
        try:
            update_state()
            socketio.emit('state_update', dashboard_state)
            time.sleep(2)  # 每 2 秒更新一次
        except Exception as e:
            print(f"[Dashboard] 更新错误：{e}")
            time.sleep(5)

# HTML 模板（赛博朋克风格）
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VectorBrain 指挥舱</title>
    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: "Courier New", monospace;
            background: #0a0a0a;
            color: #00ff00;
            overflow-x: hidden;
        }
        
        .header {
            background: linear-gradient(90deg, #0a0a0a 0%, #1a1a1a 50%, #0a0a0a 100%);
            border-bottom: 2px solid #00ff00;
            padding: 20px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            text-shadow: 0 0 10px #00ff00;
            animation: glow 2s ease-in-out infinite alternate;
        }
        
        @keyframes glow {
            from { text-shadow: 0 0 10px #00ff00; }
            to { text-shadow: 0 0 20px #00ff00, 0 0 30px #00ff00; }
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            padding: 20px;
        }
        
        .panel {
            background: #111;
            border: 1px solid #00ff00;
            border-radius: 5px;
            padding: 15px;
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.2);
        }
        
        .panel h2 {
            font-size: 1.2em;
            margin-bottom: 15px;
            border-bottom: 1px solid #00ff00;
            padding-bottom: 5px;
        }
        
        .stat-row {
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 5px 0;
        }
        
        .stat-label {
            color: #888;
        }
        
        .stat-value {
            color: #00ff00;
            font-weight: bold;
        }
        
        .health-indicator {
            display: inline-block;
            width: 15px;
            height: 15px;
            border-radius: 50%;
            animation: pulse 1s infinite;
        }
        
        .health-healthy { background: #00ff00; box-shadow: 0 0 10px #00ff00; }
        .health-warning { background: #ffaa00; box-shadow: 0 0 10px #ffaa00; }
        .health-critical { background: #ff0000; box-shadow: 0 0 10px #ff0000; }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .log-container {
            background: #000;
            border: 1px solid #004400;
            padding: 10px;
            height: 200px;
            overflow-y: auto;
            font-size: 0.8em;
        }
        
        .log-line {
            margin: 2px 0;
            padding: 2px;
            border-left: 2px solid #00ff00;
            padding-left: 5px;
        }
        
        .progress-bar {
            width: 100%;
            height: 30px;
            background: #222;
            border: 1px solid #00ff00;
            border-radius: 5px;
            overflow: hidden;
            margin: 10px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00ff00, #00aa00);
            transition: width 0.5s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #000;
            font-weight: bold;
        }
        
        .worker-status {
            display: flex;
            align-items: center;
            margin: 10px 0;
        }
        
        .worker-name {
            flex: 1;
        }
        
        .reflection-text {
            font-size: 0.85em;
            color: #00cc00;
            line-height: 1.4;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧠 VectorBrain 指挥舱</h1>
        <p>实时监控 · 数据可视化 · 灵魂透视</p>
    </div>
    
    <div class="dashboard">
        <!-- 系统状态 -->
        <div class="panel">
            <h2>📊 系统状态</h2>
            <div class="stat-row">
                <span class="stat-label">系统健康:</span>
                <span>
                    <span class="health-indicator health-healthy" id="health-indicator"></span>
                    <span id="health-text">healthy</span>
                </span>
            </div>
            <div class="stat-row">
                <span class="stat-label">CPU 使用率:</span>
                <span class="stat-value" id="cpu-usage">0%</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">内存使用率:</span>
                <span class="stat-value" id="memory-usage">0%</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Loop Ticks:</span>
                <span class="stat-value" id="loop-ticks">0</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">最后更新:</span>
                <span class="stat-value" id="last-update">-</span>
            </div>
        </div>
        
        <!-- 数据库统计 -->
        <div class="panel">
            <h2>💾 数据库统计</h2>
            <div class="stat-row">
                <span class="stat-label">待处理任务:</span>
                <span class="stat-value" id="tasks-pending">0</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">记忆总数:</span>
                <span class="stat-value" id="memories-total">0</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">经验模式:</span>
                <span class="stat-value" id="experiences-total">0</span>
            </div>
        </div>
        
        <!-- 迁移进度 -->
        <div class="panel">
            <h2>📦 记忆迁移进度</h2>
            <div class="progress-bar">
                <div class="progress-fill" id="migration-progress" style="width: 100%;">100%</div>
            </div>
            <p style="font-size: 0.8em; color: #888; margin-top: 10px;">
                ✅ 已完成从 ~/.openclaw 到 ~/.vectorbrain 的记忆大迁移
            </p>
        </div>
        
        <!-- Worker 状态 -->
        <div class="panel">
            <h2>👷 Worker 状态</h2>
            <div class="worker-status">
                <span class="worker-name">Worker_OpenClaw</span>
                <span class="health-indicator health-healthy"></span>
            </div>
            <div class="worker-status">
                <span class="worker-name">Worker_Feishu</span>
                <span class="health-indicator health-healthy"></span>
            </div>
            <div class="worker-status">
                <span class="worker-name">Agent_Core_Loop</span>
                <span class="health-indicator health-healthy"></span>
            </div>
        </div>
        
        <!-- 实时日志 -->
        <div class="panel" style="grid-column: span 2;">
            <h2>📜 实时日志</h2>
            <div class="log-container" id="log-container">
                <!-- 日志将在这里显示 -->
            </div>
        </div>
        
        <!-- 反思流 -->
        <div class="panel" style="grid-column: span 2;">
            <h2>💭 反思流</h2>
            <div id="reflection-container">
                <!-- 反思将在这里显示 -->
            </div>
        </div>
    </div>
    
    <script>
        // 连接 WebSocket
        const socket = io();
        
        // 更新状态
        socket.on('state_update', function(data) {
            // 系统状态
            document.getElementById('health-text').textContent = data.system_health;
            document.getElementById('health-indicator').className = 
                'health-indicator health-' + data.system_health;
            document.getElementById('cpu-usage').textContent = data.cpu_usage.toFixed(1) + '%';
            document.getElementById('memory-usage').textContent = data.memory_usage.toFixed(1) + '%';
            document.getElementById('loop-ticks').textContent = data.loop_ticks;
            document.getElementById('last-update').textContent = 
                new Date(data.last_update).toLocaleTimeString();
            
            // 数据库统计
            document.getElementById('tasks-pending').textContent = data.tasks_pending;
            document.getElementById('memories-total').textContent = data.memories_total;
            document.getElementById('experiences-total').textContent = data.experiences_total;
            
            // 日志
            const logContainer = document.getElementById('log-container');
            logContainer.innerHTML = '';
            data.recent_logs.forEach(line => {
                const div = document.createElement('div');
                div.className = 'log-line';
                div.textContent = line;
                logContainer.appendChild(div);
            });
            logContainer.scrollTop = logContainer.scrollHeight;
            
            // 反思
            const reflectionContainer = document.getElementById('reflection-container');
            reflectionContainer.innerHTML = '';
            data.recent_reflections.forEach(ref => {
                const div = document.createElement('div');
                div.style.margin = '10px 0';
                div.style.padding = '10px';
                div.style.borderLeft = '2px solid #00ff00';
                div.style.background = '#001100';
                div.innerHTML = '<div class="reflection-text">' + 
                    (ref.analysis || ref.outcome || 'No content') + 
                    '</div><div style="font-size:0.7em;color:#888;margin-top:5px;">' +
                    (ref.created_at || '') + '</div>';
                reflectionContainer.appendChild(div);
            });
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """首页"""
    return render_template_string(HTML_TEMPLATE)

@socketio.on('connect')
def handle_connect():
    """处理客户端连接"""
    print(f"[Dashboard] 客户端已连接")
    emit('state_update', dashboard_state)

def run_dashboard():
    """启动仪表板"""
    # 启动后台更新线程
    update_thread = threading.Thread(target=background_updater, daemon=True)
    update_thread.start()
    
    print("="*60)
    print("🧠 VectorBrain 指挥舱已启动")
    print("="*60)
    print(f"  访问地址：http://localhost:18790")
    print(f"  WebSocket: ws://localhost:18790")
    print("="*60)
    
    # 启动 Flask
    socketio.run(app, host='0.0.0.0', port=18790, debug=False, allow_unsafe_werkzeug=True)

if __name__ == "__main__":
    run_dashboard()
