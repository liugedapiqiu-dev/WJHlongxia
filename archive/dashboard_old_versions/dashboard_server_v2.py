#!/usr/bin/env python3
"""
VectorBrain Dashboard Server v2 - 指挥舱后端（双监控模式）

同时监控：
1. 对话流 - 所有飞书消息
2. 任务流 - 正式任务
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
OPENCLAW_LOG = Path('/tmp/openclaw/openclaw-2026-03-07.log')

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
app.config['SECRET_KEY'] = 'VectorBrain_Dashboard_Secret_Key_2026'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

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
    'migration_progress': 100,
    'feishu_messages': [],  # 飞书消息
    'message_count': 0,
    'task_count': 0
}

def get_db_count(db_path: Path) -> int:
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

def get_recent_logs(lines: int = 10) -> list:
    if not LOG_FILE.exists():
        return []
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines()[-lines:]]
    except:
        return []

def get_recent_reflections() -> list:
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

def get_feishu_messages(lines: int = 10) -> list:
    """获取最近的飞书消息"""
    messages = []
    
    # 从 OpenClaw 日志中提取飞书消息
    if OPENCLAW_LOG.exists():
        try:
            with open(OPENCLAW_LOG, 'r', encoding='utf-8') as f:
                log_lines = f.readlines()
                for line in log_lines[-100:]:  # 最后 100 行
                    if 'feishu[default]: Feishu[default] DM from' in line:
                        # 提取消息内容
                        match = re.search(r'Feishu\[default\] DM from \w+: (.+?)"', line)
                        if match:
                            msg = match.group(1)
                            # 提取时间
                            time_match = re.search(r'"time":"(.+?)"', line)
                            time_str = time_match.group(1) if time_match else datetime.now().isoformat()
                            messages.append({
                                'content': msg,
                                'timestamp': time_str,
                                'type': 'message'
                            })
        except:
            pass
    
    # 从 feishu_messages.log 读取
    if FEISHU_LOG.exists():
        try:
            with open(FEISHU_LOG, 'r', encoding='utf-8') as f:
                for line in f.readlines()[-lines:]:
                    if line.startswith('#'):
                        continue
                    messages.append({
                        'content': line.strip(),
                        'timestamp': datetime.now().isoformat(),
                        'type': 'log'
                    })
        except:
            pass
    
    return messages[-lines:]

def update_state():
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
    dashboard_state['feishu_messages'] = get_feishu_messages(10)
    dashboard_state['message_count'] = len(dashboard_state['feishu_messages'])
    
    # 系统健康状态
    if dashboard_state['cpu_usage'] > 90 or dashboard_state['memory_usage'] > 90:
        dashboard_state['system_health'] = 'critical'
    elif dashboard_state['cpu_usage'] > 70 or dashboard_state['memory_usage'] > 70:
        dashboard_state['system_health'] = 'warning'
    else:
        dashboard_state['system_health'] = 'healthy'

def background_updater():
    while True:
        try:
            update_state()
            socketio.emit('state_update', dashboard_state)
            time.sleep(2)
        except Exception as e:
            print(f"[Dashboard] 更新错误：{e}")
            time.sleep(5)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 VectorBrain 指挥中心 v3 - MOS 风格</title>
    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        :root {
            --bg-primary: #0a0e1a; --bg-secondary: #111625; --bg-card: rgba(23,28,40,0.6);
            --border-color: rgba(80,90,120,0.3); --text-primary: #e8ecf1; --text-secondary: #9aa5b5;
            --accent-blue: #4a9eff; --accent-green: #2ecc71; --accent-purple: #9b59b6; --accent-cyan: #00d4ff;
            --glass-bg: rgba(23,28,40,0.5); --glass-border: rgba(100,115,150,0.2);
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, 'SF Pro Display', 'Noto Sans SC', sans-serif;
            background: var(--bg-primary); color: var(--text-primary);
            background-image: radial-gradient(ellipse at top, rgba(74,158,255,0.08), transparent 50%),
                              radial-gradient(ellipse at bottom, rgba(155,89,182,0.06), transparent 50%);
        }
        .header { background: linear-gradient(90deg, #0a0a0a 0%, #1a1a1a 50%, #0a0a0a 100%); border-bottom: 2px solid #00ff00; padding: 20px; text-align: center; }
        .header h1 { font-size: 2em; text-shadow: 0 0 10px #00ff00; animation: glow 2s ease-in-out infinite alternate; }
        @keyframes glow { from { text-shadow: 0 0 10px #00ff00; } to { text-shadow: 0 0 20px #00ff00, 0 0 30px #00ff00; } }
        .dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; padding: 20px; }
        .panel { background: #111; border: 1px solid #00ff00; border-radius: 5px; padding: 15px; box-shadow: 0 0 10px rgba(0, 255, 0, 0.2); }
        .panel h2 { font-size: 1.2em; margin-bottom: 15px; border-bottom: 1px solid #00ff00; padding-bottom: 5px; }
        .panel.full-width { grid-column: span 2; }
        .stat-row { display: flex; justify-content: space-between; margin: 10px 0; padding: 5px 0; }
        .stat-label { color: #888; }
        .stat-value { color: #00ff00; font-weight: bold; }
        .health-indicator { display: inline-block; width: 15px; height: 15px; border-radius: 50%; animation: pulse 1s infinite; }
        .health-healthy { background: #00ff00; box-shadow: 0 0 10px #00ff00; }
        .health-warning { background: #ffaa00; box-shadow: 0 0 10px #ffaa00; }
        .health-critical { background: #ff0000; box-shadow: 0 0 10px #ff0000; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
        .log-container, .message-container { background: #000; border: 1px solid #004400; padding: 10px; height: 250px; overflow-y: auto; font-size: 0.8em; }
        .log-line, .message-line { margin: 2px 0; padding: 5px; border-left: 2px solid #00ff00; padding-left: 5px; background: #001100; }
        .message-line { border-left-color: #00aaff; background: #001122; }
        .progress-bar { width: 100%; height: 30px; background: #222; border: 1px solid #00ff00; border-radius: 5px; overflow: hidden; margin: 10px 0; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #00ff00, #00aa00); transition: width 0.5s; display: flex; align-items: center; justify-content: center; color: #000; font-weight: bold; }
        .counter-box { display: inline-block; padding: 10px 20px; margin: 5px; background: #002200; border: 1px solid #00ff00; border-radius: 5px; }
        .counter-label { font-size: 0.8em; color: #888; }
        .counter-value { font-size: 1.5em; color: #00ff00; font-weight: bold; }
        .timestamp { font-size: 0.7em; color: #666; float: right; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧠 VectorBrain 指挥舱 v2</h1>
        <p>双监控模式 · 对话流 + 任务流 · 实时状态</p>
    </div>
    
    <div class="dashboard">
        <!-- 系统状态 -->
        <div class="panel">
            <h2>📊 系统状态</h2>
            <div class="stat-row">
                <span class="stat-label">系统健康:</span>
                <span><span class="health-indicator health-healthy" id="health-indicator"></span><span id="health-text">healthy</span></span>
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
        </div>
        
        <!-- 计数器 -->
        <div class="panel">
            <h2>🔢 实时计数</h2>
            <div style="text-align: center;">
                <div class="counter-box">
                    <div class="counter-label">对话消息</div>
                    <div class="counter-value" id="message-count">0</div>
                </div>
                <div class="counter-box">
                    <div class="counter-label">正式任务</div>
                    <div class="counter-value" id="task-count">0</div>
                </div>
            </div>
            <div class="stat-row" style="margin-top: 15px;">
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
        
        <!-- 对话流 -->
        <div class="panel full-width">
            <h2>💬 对话流 (所有飞书消息)</h2>
            <div class="message-container" id="message-container">
                <div style="color: #666; text-align: center; padding: 20px;">等待消息...</div>
            </div>
        </div>
        
        <!-- 任务流 -->
        <div class="panel full-width">
            <h2>📋 任务流 (Agent Core Loop)</h2>
            <div class="log-container" id="log-container">
                <div style="color: #666; text-align: center; padding: 20px;">等待任务...</div>
            </div>
        </div>
        
        <!-- 反思流 -->
        <div class="panel full-width">
            <h2>💭 反思流</h2>
            <div id="reflection-container">
                <div style="color: #666; text-align: center; padding: 20px;">暂无反思</div>
            </div>
        </div>
    </div>
    
    <script>
        const socket = io();
        socket.on('state_update', function(data) {
            document.getElementById('health-text').textContent = data.system_health;
            document.getElementById('health-indicator').className = 'health-indicator health-' + data.system_health;
            document.getElementById('cpu-usage').textContent = data.cpu_usage.toFixed(1) + '%';
            document.getElementById('memory-usage').textContent = data.memory_usage.toFixed(1) + '%';
            document.getElementById('loop-ticks').textContent = data.loop_ticks;
            document.getElementById('tasks-pending').textContent = data.tasks_pending;
            document.getElementById('memories-total').textContent = data.memories_total;
            document.getElementById('experiences-total').textContent = data.experiences_total;
            document.getElementById('message-count').textContent = data.message_count;
            document.getElementById('task-count').textContent = data.tasks_pending;
            
            // 对话流
            const msgContainer = document.getElementById('message-container');
            if (data.feishu_messages && data.feishu_messages.length > 0) {
                msgContainer.innerHTML = '';
                data.feishu_messages.forEach(msg => {
                    const div = document.createElement('div');
                    div.className = 'message-line';
                    const time = new Date(msg.timestamp).toLocaleTimeString();
                    div.innerHTML = `<span class="timestamp">${time}</span>${msg.content}`;
                    msgContainer.appendChild(div);
                });
                msgContainer.scrollTop = msgContainer.scrollHeight;
            }
            
            // 任务流
            const logContainer = document.getElementById('log-container');
            if (data.recent_logs && data.recent_logs.length > 0) {
                logContainer.innerHTML = '';
                data.recent_logs.forEach(line => {
                    const div = document.createElement('div');
                    div.className = 'log-line';
                    div.textContent = line;
                    logContainer.appendChild(div);
                });
                logContainer.scrollTop = logContainer.scrollHeight;
            }
            
            // 反思流
            const refContainer = document.getElementById('reflection-container');
            if (data.recent_reflections && data.recent_reflections.length > 0) {
                refContainer.innerHTML = '';
                data.recent_reflections.forEach(ref => {
                    const div = document.createElement('div');
                    div.style.margin = '10px 0';
                    div.style.padding = '10px';
                    div.style.borderLeft = '2px solid #00ff00';
                    div.style.background = '#001100';
                    div.innerHTML = '<div class="reflection-text">' + (ref.analysis || ref.outcome || 'No content') + '</div><div style="font-size:0.7em;color:#888;margin-top:5px;">' + (ref.created_at || '') + '</div>';
                    refContainer.appendChild(div);
                });
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@socketio.on('connect')
def handle_connect():
    print(f"[Dashboard v2] 客户端已连接")
    emit('state_update', dashboard_state)

def run_dashboard():
    update_thread = threading.Thread(target=background_updater, daemon=True)
    update_thread.start()
    
    print("="*60)
    print("🧠 VectorBrain 指挥舱 v2 - 双监控模式")
    print("="*60)
    print(f"  访问地址：http://localhost:18790")
    print(f"  监控：对话流 + 任务流")
    print("="*60)
    
    socketio.run(app, host='0.0.0.0', port=18790, debug=False, allow_unsafe_werkzeug=True)

if __name__ == "__main__":
    run_dashboard()
