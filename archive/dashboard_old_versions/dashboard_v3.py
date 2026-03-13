#!/usr/bin/env python3
"""
🧠 VectorBrain Dashboard Server v3 - MOS 现代毛玻璃风格指挥中心

升级特性:
- MOS 现代设计风格 (毛玻璃 + 渐变 + 流畅动画)
- 全中文界面 + Emoji 图标
- 实时数据可视化 (Chart.js 图表)
- 任务队列状态实时监控
- 记忆库/经验/反思统计
- 系统资源监控
"""

import os, sys, json, psutil, sqlite3
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit
import threading, time

VECTORBRAIN_DIR = Path.home() / '.vectorbrain'
LOG_FILE = VECTORBRAIN_DIR / 'agent_core.log'
FEISHU_LOG = VECTORBRAIN_DIR / 'feishu_messages.log'

DB_PATHS = {
    'tasks': VECTORBRAIN_DIR / 'tasks' / 'task_queue.db',
    'memory_episodic': VECTORBRAIN_DIR / 'memory' / 'episodic_memory.db',
    'memory_knowledge': VECTORBRAIN_DIR / 'memory' / 'knowledge_memory.db',
    'experience': VECTORBRAIN_DIR / 'experience' / 'error_patterns.db',
    'goals': VECTORBRAIN_DIR / 'goals' / 'goals.db',
    'reflection': VECTORBRAIN_DIR / 'reflection' / 'reflections.db'
}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'VectorBrain_v3_2026'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

state = {
    'loop_ticks': 0, 'tasks_pending': 0, 'tasks_completed': 0, 'tasks_total': 0,
    'memories_total': 0, 'experiences_total': 0, 'goals_active': 0, 'reflections_count': 0,
    'system_health': 'healthy', 'cpu_usage': 0.0, 'memory_usage': 0.0,
    'last_update': None, 'recent_logs': [], 'recent_reflections': [],
    'feishu_messages': [], 'task_queue': {'pending': 0, 'running': 0, 'completed': 0, 'failed': 0}
}

def get_db_count(db_path):
    if not db_path.exists(): return 0
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        total = sum(cursor.execute(f"SELECT COUNT(*) FROM {t[0]}").fetchone()[0] for t in cursor.fetchall() if t[0])
        conn.close()
        return total
    except: return 0

def get_task_stats():
    db_path = DB_PATHS['tasks']
    if not db_path.exists(): return {'pending': 0, 'running': 0, 'completed': 0, 'failed': 0}
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        stats = {'pending': 0, 'running': 0, 'completed': 0, 'failed': 0}
        for (table,) in cursor.fetchall():
            try:
                for status, count in cursor.execute(f"SELECT status, COUNT(*) FROM {table} GROUP BY status").fetchall():
                    if status in stats: stats[status] += count
            except: pass
        conn.close()
        return stats
    except: return {'pending': 0, 'running': 0, 'completed': 0, 'failed': 0}

def get_recent_logs(n=20):
    if not LOG_FILE.exists(): return []
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f: return [l.strip() for l in f.readlines()[-n:]]
    except: return []

def get_reflections():
    db_path = DB_PATHS['reflection']
    if not db_path.exists(): return []
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM reflections ORDER BY created_at DESC LIMIT 10")
        refs = [dict(r) for r in cur.fetchall()]
        conn.close()
        return refs
    except: return []

def get_feishu_msgs(n=20):
    if not FEISHU_LOG.exists(): return []
    try:
        msgs = []
        with open(FEISHU_LOG, 'r', encoding='utf-8') as f:
            for line in f.readlines()[-n:]:
                if line.strip():
                    parts = line.strip().split(' | ', 2)
                    if len(parts) >= 3: msgs.append({'timestamp': parts[0], 'user': parts[1], 'content': parts[2]})
        return msgs
    except: return []

def update_state():
    try:
        state['cpu_usage'] = psutil.cpu_percent(interval=1)
        state['memory_usage'] = psutil.virtual_memory().percent
        state['memories_total'] = get_db_count(DB_PATHS['memory_episodic']) + get_db_count(DB_PATHS['memory_knowledge'])
        state['experiences_total'] = get_db_count(DB_PATHS['experience'])
        state['reflections_count'] = get_db_count(DB_PATHS['reflection'])
        
        task_stats = get_task_stats()
        state['tasks_pending'] = task_stats['pending']
        state['tasks_completed'] = task_stats['completed']
        state['tasks_total'] = sum(task_stats.values())
        state['task_queue'] = task_stats
        
        state['feishu_messages'] = get_feishu_msgs()
        state['recent_logs'] = get_recent_logs()
        state['recent_reflections'] = get_reflections()
        state['loop_ticks'] = len([l for l in state['recent_logs'] if 'LOOP' in l.upper()])
        
        if state['cpu_usage'] > 90 or state['memory_usage'] > 90: state['system_health'] = 'critical'
        elif state['cpu_usage'] > 70 or state['memory_usage'] > 70: state['system_health'] = 'warning'
        else: state['system_health'] = 'healthy'
        
        state['last_update'] = datetime.now().isoformat()
    except Exception as e: print(f"更新错误：{e}")

def background_update():
    while True:
        update_state()
        socketio.emit('state_update', state)
        time.sleep(2)

HTML = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>🧠 VectorBrain 指挥中心</title>
    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        :root{--bg:#0a0e1a;--card:rgba(23,28,40,0.6);--text:#e8ecf1;--muted:#9aa5b5;--blue:#4a9eff;--green:#2ecc71;--purple:#9b59b6;--cyan:#00d4ff}
        *{margin:0;padding:0;box-sizing:border-box}
        body{font-family:-apple-system,'SF Pro Display','Noto Sans SC',sans-serif;background:var(--bg);color:var(--text);min-height:100vh;background-image:radial-gradient(ellipse at top,rgba(74,158,255,0.08),transparent 50%)}
        .container{max-width:1800px;margin:0 auto;padding:20px}
        .nav{display:flex;justify-content:space-between;align-items:center;padding:16px 24px;margin-bottom:24px;background:rgba(23,28,40,0.5);backdrop-filter:blur(20px);border:1px solid rgba(100,115,150,0.2);border-radius:16px}
        .brand{display:flex;align-items:center;gap:12px;font-size:22px;font-weight:700;background:linear-gradient(135deg,var(--blue),var(--purple));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
        .brand-emoji{font-size:32px;animation:float 3s ease-in-out infinite}@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
        .status{display:flex;align-items:center;gap:8px;padding:6px 16px;background:rgba(46,204,113,0.1);border:1px solid rgba(46,204,113,0.3);border-radius:20px}
        .status-dot{width:8px;height:8px;border-radius:50%;background:var(--green);animation:pulse 2s infinite}@keyframes pulse{0%,100%{opacity:1;box-shadow:0 0 0 0 rgba(46,204,113,0.7)}50%{opacity:0.8;box-shadow:0 0 0 6px rgba(46,204,113,0)}}
        .status-text{font-size:13px;color:var(--green);font-weight:600}
        .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin-bottom:24px}
        .card{background:rgba(23,28,40,0.6);backdrop-filter:blur(20px);border:1px solid rgba(80,90,120,0.3);border-radius:16px;padding:20px;transition:all 0.3s}
        .card:hover{transform:translateY(-4px);border-color:var(--blue);box-shadow:0 12px 40px rgba(74,158,255,0.15)}
        .card.primary{background:linear-gradient(135deg,rgba(74,158,255,0.15),rgba(155,89,182,0.1));border-color:rgba(74,158,255,0.4)}
        .card-header{display:flex;align-items:center;gap:8px;margin-bottom:12px;font-size:13px;color:var(--muted)}
        .card-value{font-size:32px;font-weight:700;background:linear-gradient(135deg,var(--blue),var(--purple));-webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1}
        .card-sub{font-size:12px;color:var(--muted);margin-top:4px}
        .main-grid{display:grid;grid-template-columns:1fr 400px;gap:16px}
        @media(max-width:1200px){.main-grid{grid-template-columns:1fr}}
        .panel{background:rgba(23,28,40,0.6);backdrop-filter:blur(20px);border:1px solid rgba(80,90,120,0.3);border-radius:16px;margin-bottom:16px}
        .panel-header{display:flex;align-items:center;gap:8px;padding:16px 20px;border-bottom:1px solid rgba(100,115,150,0.2);font-size:15px;font-weight:600}
        .panel-body{padding:20px}
        .msg-list{max-height:350px;overflow-y:auto}
        .msg-item{display:flex;gap:12px;padding:12px;margin-bottom:8px;background:rgba(0,212,255,0.05);border-radius:8px;border-left:3px solid var(--cyan)}
        .msg-avatar{width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,var(--blue),var(--cyan));display:flex;align-items:center;justify-content:center;font-size:16px;font-weight:700;color:white;flex-shrink:0}
        .msg-content{flex:1}
        .msg-user{font-size:13px;font-weight:600;margin-bottom:4px}
        .msg-text{font-size:13px;color:var(--muted);line-height:1.5}
        .msg-time{font-size:11px;color:var(--muted);margin-top:4px}
        .log-list{max-height:300px;overflow-y:auto;font-family:'SF Mono',monospace;font-size:12px}
        .log-item{padding:8px 12px;margin-bottom:4px;background:rgba(74,158,255,0.05);border-radius:8px;border-left:3px solid var(--blue);animation:slideIn 0.3s}
        @keyframes slideIn{from{opacity:0;transform:translateX(-16px)}to{opacity:1;transform:translateX(0)}}
        .queue-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}
        .queue-stat{text-align:center;padding:16px;background:rgba(0,0,0,0.2);border-radius:8px}
        .queue-icon{font-size:20px;margin-bottom:8px}
        .queue-value{font-size:20px;font-weight:700;color:var(--blue)}
        .queue-label{font-size:11px;color:var(--muted)}
        .ref-list{max-height:250px;overflow-y:auto}
        .ref-item{padding:12px;margin-bottom:8px;background:rgba(155,89,182,0.05);border-radius:8px;border-left:3px solid var(--purple)}
        .ref-text{font-size:13px;color:var(--muted);margin-bottom:4px}
        .ref-time{font-size:11px;color:var(--muted)}
        .chart-box{height:200px}
    </style>
</head>
<body>
    <div class="container">
        <nav class="nav">
            <div class="brand"><span class="brand-emoji">🧠</span>VectorBrain 指挥中心</div>
            <div class="status"><span class="status-dot" id="status-dot"></span><span class="status-text" id="status-text">系统运行正常</span></div>
        </nav>
        
        <div class="grid">
            <div class="card primary"><div class="card-header"><span>💚</span>系统健康</div><div class="card-value" id="health">正常</div><div class="card-sub">实时监测</div></div>
            <div class="card"><div class="card-header"><span>📊</span>CPU</div><div class="card-value" id="cpu">0%</div><div class="card-sub">使用率</div></div>
            <div class="card"><div class="card-header"><span>💾</span>内存</div><div class="card-value" id="mem">0%</div><div class="card-sub">使用率</div></div>
            <div class="card"><div class="card-header"><span>⏱️</span>Loop</div><div class="card-value" id="loop">0</div><div class="card-sub">心跳数</div></div>
            <div class="card"><div class="card-header"><span>📋</span>待处理</div><div class="card-value" id="pending">0</div><div class="card-sub">任务队列</div></div>
            <div class="card"><div class="card-header"><span>🧠</span>记忆</div><div class="card-value" id="memory">0</div><div class="card-sub">总数</div></div>
            <div class="card"><div class="card-header"><span>💡</span>经验</div><div class="card-value" id="exp">0</div><div class="card-sub">模式数</div></div>
            <div class="card"><div class="card-header"><span>💭</span>反思</div><div class="card-value" id="ref">0</div><div class="card-sub">记录数</div></div>
        </div>
        
        <div class="main-grid">
            <div>
                <div class="panel"><div class="panel-header"><span>💬</span>对话流 (飞书消息)</div><div class="panel-body"><div class="msg-list" id="msgs"></div></div></div>
                <div class="panel"><div class="panel-header"><span>📜</span>任务流</div><div class="panel-body"><div class="log-list" id="logs"></div></div></div>
            </div>
            <div>
                <div class="panel"><div class="panel-header"><span>🚦</span>任务队列</div><div class="panel-body"><div class="queue-grid"><div class="queue-stat"><div class="queue-icon">⏳</div><div class="queue-value" id="q-pending">0</div><div class="queue-label">等待</div></div><div class="queue-stat"><div class="queue-icon">🔄</div><div class="queue-value" id="q-running">0</div><div class="queue-label">执行</div></div><div class="queue-stat"><div class="queue-icon">✅</div><div class="queue-value" id="q-done">0</div><div class="queue-label">完成</div></div><div class="queue-stat"><div class="queue-icon">❌</div><div class="queue-value" id="q-fail">0</div><div class="queue-label">失败</div></div></div></div></div>
                <div class="panel"><div class="panel-header"><span>💭</span>反思流</div><div class="panel-body"><div class="ref-list" id="refs"></div></div></div>
                <div class="panel"><div class="panel-header"><span>📈</span>资源趋势</div><div class="panel-body"><div class="chart-box"><canvas id="chart"></canvas></div></div></div>
            </div>
        </div>
    </div>
    <script>
        const socket=io();let chart,chartData={labels:[],cpu:[],mem:[]};
        function initChart(){const ctx=document.getElementById('chart').getContext('2d');chart=new Chart(ctx,{type:'line',data:{labels:[],datasets:[{label:'CPU',data:[],borderColor:'#4a9eff',backgroundColor:'rgba(74,158,255,0.1)',tension:0.4,fill:true},{label:'内存',data:[],borderColor:'#9b59b6',backgroundColor:'rgba(155,89,182,0.1)',tension:0.4,fill:true}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:true}},scales:{y:{beginAtZero:true,max:100,grid:{color:'rgba(80,90,120,0.2)'}},x:{grid:{color:'rgba(80,90,120,0.2)'}}}}});}
        function updateChart(cpu,mem){const now=new Date().toLocaleTimeString('zh-CN',{hour:'2-digit',minute:'2-digit',second:'2-digit'});chartData.labels.push(now);chartData.cpu.push(cpu);chartData.mem.push(mem);if(chartData.labels.length>20){chartData.labels.shift();chartData.cpu.shift();chartData.mem.shift()}chart.data.labels=chartData.labels;chart.data.datasets[0].data=chartData.cpu;chart.data.datasets[1].data=chartData.mem;chart.update('none');}
        socket.on('state_update',d=>{
            const dot=document.getElementById('status-dot'),txt=document.getElementById('status-text'),h=document.getElementById('health');
            if(d.system_health==='healthy'){dot.style.background='#2ecc71';txt.textContent='系统运行正常';h.textContent='🟢 正常';h.style.color='var(--green)'}
            else if(d.system_health==='warning'){dot.style.background='#f1c40f';txt.textContent='需要注意';h.textContent='⚠️ 警告';h.style.color='#f1c40f'}
            else{dot.style.background='#e74c3c';txt.textContent='系统异常';h.textContent='❌ 异常';h.style.color='#e74c3c'}
            document.getElementById('cpu').textContent=d.cpu_usage.toFixed(1)+'%';
            document.getElementById('mem').textContent=d.memory_usage.toFixed(1)+'%';
            document.getElementById('loop').textContent=d.loop_ticks;
            document.getElementById('pending').textContent=d.tasks_pending;
            document.getElementById('memory').textContent=d.memories_total;
            document.getElementById('exp').textContent=d.experiences_total;
            document.getElementById('ref').textContent=d.reflections_count;
            updateChart(d.cpu_usage,d.memory_usage);
            if(d.task_queue){document.getElementById('q-pending').textContent=d.task_queue.pending||0;document.getElementById('q-running').textContent=d.task_queue.running||0;document.getElementById('q-done').textContent=d.task_queue.completed||0;document.getElementById('q-fail').textContent=d.task_queue.failed||0}
            const mc=document.getElementById('msgs');
            if(d.feishu_messages&&d.feishu_messages.length>0){mc.innerHTML='';d.feishu_messages.forEach(m=>{const div=document.createElement('div');div.className='msg-item';const ini=(m.user||'U').substring(0,2).toUpperCase();div.innerHTML='<div class="msg-avatar">'+ini+'</div><div class="msg-content"><div class="msg-user">'+(m.user||'未知')+'</div><div class="msg-text">'+(m.content||'')+'</div><div class="msg-time">'+(m.timestamp||'')+'</div></div>';mc.appendChild(div)});mc.scrollTop=mc.scrollHeight}
            const lc=document.getElementById('logs');
            if(d.recent_logs&&d.recent_logs.length>0){lc.innerHTML='';d.recent_logs.forEach(l=>{const div=document.createElement('div');div.className='log-item';div.textContent=l;lc.appendChild(div)});lc.scrollTop=lc.scrollHeight}
            const rc=document.getElementById('refs');
            if(d.recent_reflections&&d.recent_reflections.length>0){rc.innerHTML='';d.recent_reflections.forEach(r=>{const div=document.createElement('div');div.className='ref-item';const t=r.created_at?new Date(r.created_at).toLocaleString('zh-CN'):'';div.innerHTML='<div class="ref-text">'+(r.analysis||r.outcome||'无')+'</div><div class="ref-time">'+t+'</div>';rc.appendChild(div)})}});
        document.addEventListener('DOMContentLoaded',initChart);
    </script>
</body>
</html>'''

@app.route('/')
def index(): return render_template_string(HTML)

@socketio.on('connect')
def connect(): print("[VB v3] ✅ 客户端已连接"); emit('state_update', state)

def run():
    threading.Thread(target=background_update, daemon=True).start()
    print("="*60)
    print("🧠 VectorBrain 指挥中心 v3 - MOS 现代风格")
    print("="*60)
    print("  🌐 地址：http://localhost:18790")
    print("  📊 功能：实时监控 / 任务队列 / 记忆库 / 反思流")
    print("  💬 对话流：飞书消息")
    print("  📈 图表：Chart.js 资源趋势")
    print("="*60)
    socketio.run(app, host='0.0.0.0', port=18790, debug=False, allow_unsafe_werkzeug=True)

if __name__ == '__main__': run()
