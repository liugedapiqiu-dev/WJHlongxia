#!/usr/bin/env python3
"""
🧠 VectorBrain Dashboard Server v4 - 全面监控升级版

升级特性 (v4 - 2026-03-11):
- MOS 现代设计风格 (毛玻璃 + 渐变 + 流畅动画)
- 全中文界面 + Emoji 图标
- 实时数据可视化 (Chart.js 图表)
- 任务队列状态实时监控
- 记忆库/经验/反思统计
- 系统资源监控
- 🆕 脚本运行状态监控 (9 个核心脚本)
- 🆕 网络状态实时显示
- 🆕 智能健康度计算
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
    'feishu_messages': [], 'task_queue': {'pending': 0, 'running': 0, 'completed': 0, 'failed': 0},
    'scripts': {},  # 新增：脚本监控状态
    'scheduled_tasks': []  # 新增：定时任务监控
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

def get_task_monitor_stats():
    """读取定时任务监控统计数据"""
    stats_file = Path.home() / ".vectorbrain/state/task_monitor_stats.json"
    if not stats_file.exists():
        return []
    try:
        with open(stats_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('tasks', [])
    except:
        return []

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

def get_pid(pattern):
    """获取进程 PID"""
    import subprocess
    try:
        result = subprocess.run(["pgrep", "-f", pattern], capture_output=True, text=True)
        pids = result.stdout.strip().split('\n')
        return [p for p in pids if p] if pids else []
    except: return []

def get_script_status():
    """获取所有脚本的运行状态"""
    import subprocess
    
    scripts = {
        'network_monitor': {'name': '网络监控', 'pattern': 'network_monitor.py', 'critical': True},
        'task_manager': {'name': '任务执行', 'pattern': 'task_manager', 'critical': False},
        'task_monitor': {'name': '任务监控', 'pattern': 'task_monitor', 'critical': False},
        'opportunity_poller': {'name': '机会发现', 'pattern': 'opportunity_poller', 'critical': False},
        'spiderman_monitor': {'name': '群组监控', 'pattern': 'spiderman', 'critical': False},
        'dashboard': {'name': 'Dashboard', 'pattern': 'dashboard_running.py', 'critical': False},
        'ollama': {'name': 'Ollama 服务', 'pattern': 'ollama serve', 'critical': True},
        'openclaw': {'name': 'OpenClaw', 'pattern': 'openclaw', 'critical': True},
        'agent_core': {'name': 'Agent Core', 'pattern': 'agent_core_loop.py', 'critical': True},
        # 自动反思脚本监控
        'auto_reflection': {'name': '🧠 自动反思', 'pattern': 'auto_reflection_engine.py', 'critical': False},
        'memory_extraction': {'name': '💡 记忆提取', 'pattern': 'memory_extraction_engine.py', 'critical': False},
        'brain_health': {'name': '🏥 大脑健康', 'pattern': 'brain_health_monitor.py', 'critical': False},
    }
    
    status = {}
    for key, config in scripts.items():
        pids = get_pid(config['pattern'])
        status[key] = {
            'name': config['name'],
            'running': len(pids) > 0,
            'pids': pids,
            'critical': config['critical']
        }
    
    return status

def check_network():
    """检查网络状态"""
    import subprocess
    try:
        result = subprocess.run(["ping", "-c", "1", "-W", "2", "8.8.8.8"], capture_output=True, timeout=3)
        return result.returncode == 0
    except: return False

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
        
        # 新增：脚本监控状态
        state['scripts'] = get_script_status()
        state['network_online'] = check_network()
        
        # 新增：定时任务监控
        state['scheduled_tasks'] = get_task_monitor_stats()
        
        # 计算健康度
        running_count = sum(1 for s in state['scripts'].values() if s['running'])
        total_count = len(state['scripts'])
        health_ratio = running_count / total_count if total_count > 0 else 0
        
        critical_down = [k for k, v in state['scripts'].items() if v['critical'] and not v['running']]
        
        if len(critical_down) > 0 or state['cpu_usage'] > 90 or state['memory_usage'] > 90:
            state['system_health'] = 'critical'
        elif health_ratio < 0.7 or state['cpu_usage'] > 70 or state['memory_usage'] > 70:
            state['system_health'] = 'warning'
        else:
            state['system_health'] = 'healthy'
        
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
        .task-list{max-height:400px;overflow-y:auto}
        .task-item{padding:16px;margin-bottom:12px;background:rgba(0,0,0,0.2);border-radius:8px;border-left:4px solid var(--blue)}
        .task-item.running{border-left-color:var(--green)}
        .task-item.stopped{border-left-color:#e74c3c}
        .task-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
        .task-name{font-size:14px;font-weight:600;color:var(--text)}
        .task-status{font-size:11px;padding:4px 8px;border-radius:12px}
        .task-status.running{background:rgba(46,204,113,0.2);color:var(--green)}
        .task-status.stopped{background:rgba(231,76,60,0.2);color:#e74c3c}
        .task-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:8px}
        .task-stat{text-align:center;padding:8px;background:rgba(255,255,255,0.05);border-radius:4px}
        .task-stat-value{font-size:16px;font-weight:700;color:var(--blue)}
        .task-stat-label{font-size:10px;color:var(--muted);margin-top:2px}
        .task-pid{font-size:10px;color:var(--muted);margin-top:4px}
        .task-last{font-size:10px;color:var(--muted);margin-top:4px}
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
                <div class="panel"><div class="panel-header"><span>🧩</span>脚本监控</div><div class="panel-body"><div class="queue-grid" id="script-status" style="grid-template-columns:repeat(auto-fit,minmax(150px,1fr))"></div></div></div>
                <div class="panel"><div class="panel-header"><span>💬</span>对话流 (飞书消息)</div><div class="panel-body"><div class="msg-list" id="msgs"></div></div></div>
                <div class="panel"><div class="panel-header"><span>📜</span>任务流</div><div class="panel-body"><div class="log-list" id="logs"></div></div></div>
            </div>
            <div>
                <div class="panel"><div class="panel-header"><span>🚦</span>任务队列</div><div class="panel-body"><div class="queue-grid"><div class="queue-stat"><div class="queue-icon">⏳</div><div class="queue-value" id="q-pending">0</div><div class="queue-label">等待</div></div><div class="queue-stat"><div class="queue-icon">🔄</div><div class="queue-value" id="q-running">0</div><div class="queue-label">执行</div></div><div class="queue-stat"><div class="queue-icon">✅</div><div class="queue-value" id="q-done">0</div><div class="queue-label">完成</div></div><div class="queue-stat"><div class="queue-icon">❌</div><div class="queue-value" id="q-fail">0</div><div class="queue-label">失败</div></div></div></div></div>
                <div class="panel"><div class="panel-header"><span>📋</span>定时任务监控</div><div class="panel-body"><div class="task-list" id="scheduled-tasks"></div></div></div>
                <div class="panel"><div class="panel-header"><span>📊</span>自动反思统计</div><div class="panel-body"><div class="queue-grid" id="reflection-stats" style="grid-template-columns:repeat(auto-fit,minmax(200px,1fr))"></div></div></div>
                
                <div class="panel"><div class="panel-header"><span>📊</span>Token 统计</div><div class="panel-body"><div class="queue-grid" id="token-stats" style="grid-template-columns:repeat(auto-fit,minmax(180px,1fr))"></div></div></div>
<div class="panel"><div class="panel-header"><span>💭</span>反思流</div><div class="panel-body"><div class="ref-list" id="refs"></div></div></div>
                <div class="panel"><div class="panel-header"><span>📈</span>资源趋势</div><div class="panel-body"><div class="chart-box"><canvas id="chart"></canvas></div></div></div>
            </div>
        </div>
    </div>
    <script>
        const socket=io();let chart,chartData={labels:[],cpu:[],mem:[]};
        function initChart(){const ctx=document.getElementById('chart').getContext('2d');chart=new Chart(ctx,{type:'line',data:{labels:[],datasets:[{label:'CPU',data:[],borderColor:'#4a9eff',backgroundColor:'rgba(74,158,255,0.1)',tension:0.4,fill:true},{label:'内存',data:[],borderColor:'#9b59b6',backgroundColor:'rgba(155,89,182,0.1)',tension:0.4,fill:true}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:true}},scales:{y:{beginAtZero:true,max:100,grid:{color:'rgba(80,90,120,0.2)'}},x:{grid:{color:'rgba(80,90,120,0.2)'}}}}});}
        function updateChart(cpu,mem){const now=new Date().toLocaleTimeString('zh-CN',{hour:'2-digit',minute:'2-digit',second:'2-digit'});chartData.labels.push(now);chartData.cpu.push(cpu);chartData.mem.push(mem);if(chartData.labels.length>20){chartData.labels.shift();chartData.cpu.shift();chartData.mem.shift()}chart.data.labels=chartData.labels;chart.data.datasets[0].data=chartData.cpu;chart.data.datasets[1].data=chartData.mem;chart.update('none');}
        
        // 自动反思统计
        function updateReflectionStats(){
            fetch("/api/reflection-stats")
            .then(r=>r.json())
            .then(d=>{
                const div=document.getElementById("reflection-stats");
                if(!div||!d||d.error)return;
                div.innerHTML="";
                Object.entries(d).forEach(([key,stat])=>{
                    const card=document.createElement("div");
                    card.className="queue-stat";
                    card.style.background="rgba(155,89,182,0.05)";
                    card.style.borderColor="rgba(155,89,182,0.3)";
                    card.style.borderWidth="2px";
                    card.style.borderStyle="solid";
                    const successRate=stat.success_rate||0;
                    const color=successRate>=80?"rgba(46,204,113,0.5)":successRate>=50?"rgba(241,196,15,0.5)":"rgba(231,76,60,0.5)";
                    card.style.borderColor=color;
                    const failuresHtml=stat.common_failures&&stat.common_failures.length>0?
                        stat.common_failures.map(f=>`<span style="font-size:9px;color:#e74c3c">⚠️${f.type}:${f.count}</span>`).join(""):
                        `<span style="font-size:9px;color:#2ecc71">✅ 无失败记录</span>`;
                    card.innerHTML=`
                        <div class="queue-icon">🧠</div>
                        <div class="queue-label" style="font-weight:600">${stat.name}</div>
                        <div class="queue-value" style="font-size:18px">${stat.total_runs}次</div>
                        <div class="queue-label">成功率：${successRate}%</div>
                        <div style="margin-top:4px">${failuresHtml}</div>
                    `;
                    div.appendChild(card);
                });
            })
            .catch(e=>console.error("获取反思统计失败:",e));
        }
        setInterval(updateReflectionStats,10000);
        updateReflectionStats();
        
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
            if(d.recent_reflections&&d.recent_reflections.length>0){rc.innerHTML='';d.recent_reflections.forEach(r=>{const div=document.createElement('div');div.className='ref-item';const t=r.created_at?new Date(r.created_at).toLocaleString('zh-CN'):'';div.innerHTML='<div class="ref-text">'+(r.analysis||r.outcome||'无')+'</div><div class="ref-time">'+t+'</div>';rc.appendChild(div)})}
            // 新增：渲染脚本状态
            const sc=document.getElementById('script-status');
            if(d.scripts){sc.innerHTML='';Object.entries(d.scripts).forEach(([key,s])=>{const div=document.createElement('div');div.className='queue-stat';div.style.borderColor=s.running?'rgba(46,204,113,0.5)':'rgba(231,76,60,0.5)';div.style.borderWidth='2px';div.style.borderStyle='solid';div.style.background=s.running?'rgba(46,204,113,0.05)':'rgba(231,76,60,0.05)';const icon=s.running?'🟢':'🔴';const pidInfo=s.pids.length>0?`<span style="font-size:10px;color:var(--muted)">PID:${s.pids[0]}</span>`:'';const critical=s.critical?'<span style="font-size:10px;color:#e74c3c">⚠️核心</span>':'';div.innerHTML=`<div class="queue-icon">${icon}</div><div class="queue-label" style="font-weight:600">${s.name}</div>${pidInfo}${critical}`;sc.appendChild(div)})}
            
            // 新增：渲染定时任务状态
            const tc=document.getElementById('scheduled-tasks');
            if(d.scheduled_tasks&&d.scheduled_tasks.length>0){tc.innerHTML='';d.scheduled_tasks.forEach(t=>{const div=document.createElement('div');div.className=`task-item ${t.status}`;const statusText=t.status==='running'?'运行中':'已停止';const statusClass=t.status;const pidInfo=t.pid?`<div class="task-pid">进程 PID: ${t.pid}</div>`:'<div class="task-pid">未运行</div>';const lastLog=t.last_log_time?`<div class="task-last">最后运行：${t.last_log_time}</div>`:'';div.innerHTML=`<div class="task-header"><div class="task-name">${t.display_name||t.name}</div><div class="task-status ${statusClass}">${statusText}</div></div>${pidInfo}${lastLog}<div class="task-stats"><div class="task-stat"><div class="task-stat-value">${t.total_runs||0}</div><div class="task-stat-label">总运行</div></div><div class="task-stat"><div class="task-stat-value" style="color:var(--green)">${t.successes||0}</div><div class="task-stat-label">成功</div></div><div class="task-stat"><div class="task-stat-value" style="color:#e74c3c">${t.errors||0}</div><div class="task-stat-label">失败</div></div></div>`;tc.appendChild(div)})}else if(tc){tc.innerHTML='<div style="text-align:center;color:var(--muted);padding:20px">暂无定时任务数据</div>'}
        });
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
    print("🧠 VectorBrain 指挥中心 v4 - 全面监控升级版")
    print("="*60)
    print("  🌐 地址：http://localhost:18790")
    print("  📊 功能：实时监控 / 任务队列 / 记忆库 / 反思流")
    print("  🆕 脚本监控：9 个核心脚本实时状态")
    print("  🆕 网络监测：断网自动检测")
    print("  🆕 智能健康：基于脚本状态 + 系统资源")
    print("="*60)
    socketio.run(app, host='0.0.0.0', port=8501, debug=False, allow_unsafe_werkzeug=True)

if __name__ == '__main__': run()

# 自动反思脚本统计 API
@app.route('/api/reflection-stats')
def reflection_stats():
    stats_file = Path.home() / '.openclaw' / 'logs' / 'reflection_stats.json'
    try:
        with open(stats_file, 'r', encoding='utf-8') as f:
            stats = json.load(f)
        
        # 分析失败原因
        analysis = {}
        for key, data in stats.items():
            analysis[key] = {
                'name': data['name'],
                'total_runs': data['total_runs'],
                'success_rate': round(data['successful_runs'] / max(data['total_runs'], 1) * 100, 1),
                'failed_runs': data['failed_runs'],
                'last_run': data['last_run'],
                'failure_reasons': data['failure_reasons'][-5:],  # 最近 5 条
                'common_failures': analyze_failure_patterns(data['failure_reasons'])
            }
        
        return json.dumps(analysis, ensure_ascii=False)
    except Exception as e:
        return json.dumps({'error': str(e)}, ensure_ascii=False)

def analyze_failure_patterns(failure_reasons):
    """分析失败模式"""
    if not failure_reasons:
        return []
    
    patterns = {}
    for failure in failure_reasons:
        error = failure.get('error', '')
        # 提取错误类型
        if 'FileNotFoundError' in error:
            patterns['文件缺失'] = patterns.get('文件缺失', 0) + 1
        elif 'PermissionError' in error:
            patterns['权限错误'] = patterns.get('权限错误', 0) + 1
        elif 'sqlite3' in error or 'database' in error.lower():
            patterns['数据库错误'] = patterns.get('数据库错误', 0) + 1
        elif 'ModuleNotFoundError' in error:
            patterns['模块缺失'] = patterns.get('模块缺失', 0) + 1
        elif 'timeout' in error.lower():
            patterns['超时错误'] = patterns.get('超时错误', 0) + 1
        else:
            patterns['其他错误'] = patterns.get('其他错误', 0) + 1
    
    return sorted([{'type': k, 'count': v} for k, v in patterns.items()], key=lambda x: x['count'], reverse=True)

print("✅ 自动反思统计 API 已加载")

# Token 统计 API
@app.route('/api/token-stats')
def token_stats():
    stats_file = Path.home() / '.vectorbrain' / 'state' / 'token_stats.db'
    if not stats_file.exists():
        return json.dumps({'today': [], 'summary': []}, ensure_ascii=False)
    
    try:
        conn = sqlite3.connect(stats_file)
        cursor = conn.cursor()
        
        # 今日统计
        cursor.execute('''
            SELECT direction, SUM(token_count), COUNT(*), AVG(token_count)
            FROM token_stats
            WHERE date(timestamp) = date('now')
            GROUP BY direction
        ''')
        today = [{'direction': r[0], 'tokens': r[1], 'count': r[2], 'avg': round(r[3], 1)} for r in cursor.fetchall()]
        
        # 最近 7 天
        cursor.execute('''
            SELECT direction, SUM(token_count), COUNT(*), AVG(token_count)
            FROM token_stats
            WHERE timestamp >= datetime('now', '-7 days')
            GROUP BY direction
        ''')
        summary = [{'direction': r[0], 'tokens': r[1], 'count': r[2], 'avg': round(r[3], 1)} for r in cursor.fetchall()]
        
        conn.close()
        return json.dumps({'today': today, 'summary': summary}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({'error': str(e)}, ensure_ascii=False)

print("✅ Token 统计 API 已加载")
