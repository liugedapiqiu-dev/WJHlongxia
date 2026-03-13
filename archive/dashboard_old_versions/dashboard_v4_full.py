# 续写 dashboard_v4.py - 添加 HTML 模板

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>🧠 VectorBrain 企业级指挥中心</title>
    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        :root{--bg:#0a0e1a;--card:rgba(23,28,40,0.7);--text:#e8ecf1;--muted:#9aa5b5;--blue:#4a9eff;--green:#2ecc71;--yellow:#f1c40f;--red:#e74c3c;--purple:#9b59b6}
        *{margin:0;padding:0;box-sizing:border-box}
        body{font-family:-apple-system,'SF Pro Display','Noto Sans SC',sans-serif;background:var(--bg);color:var(--text);min-height:100vh;background-image:radial-gradient(ellipse at top,rgba(74,158,255,0.08),transparent 50%)}
        .container{max-width:2000px;margin:0 auto;padding:20px}
        .nav{display:flex;justify-content:space-between;align-items:center;padding:16px 24px;margin-bottom:24px;background:rgba(23,28,40,0.5);backdrop-filter:blur(20px);border:1px solid rgba(100,115,150,0.2);border-radius:16px}
        .brand{display:flex;align-items:center;gap:12px;font-size:22px;font-weight:700;background:linear-gradient(135deg,var(--blue),var(--purple));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
        .brand-emoji{font-size:32px;animation:float 3s ease-in-out infinite}@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
        .nav-right{display:flex;align-items:center;gap:16px}
        .uptime{font-size:13px;color:var(--muted)}
        .status{display:flex;align-items:center;gap:8px;padding:6px 16px;background:rgba(46,204,113,0.1);border:1px solid rgba(46,204,113,0.3);border-radius:20px}
        .status-dot{width:8px;height:8px;border-radius:50%;background:var(--green);animation:pulse 2s infinite}@keyframes pulse{0%,100%{opacity:1;box-shadow:0 0 0 0 rgba(46,204,113,0.7)}50%{opacity:0.8;box-shadow:0 0 0 6px rgba(46,204,113,0)}}
        .status-text{font-size:13px;color:var(--green);font-weight:600}
        .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px;margin-bottom:24px}
        .card{background:var(--card);backdrop-filter:blur(20px);border:1px solid rgba(80,90,120,0.3);border-radius:16px;padding:20px;transition:all 0.3s;position:relative}
        .card:hover{transform:translateY(-4px);border-color:var(--blue);box-shadow:0 12px 40px rgba(74,158,255,0.15)}
        .card.primary{background:linear-gradient(135deg,rgba(74,158,255,0.15),rgba(155,89,182,0.1));border-color:rgba(74,158,255,0.4)}
        .card.warning{border-color:var(--yellow);box-shadow:0 0 20px rgba(241,196,15,0.2)}
        .card-header{display:flex;align-items:center;gap:8px;margin-bottom:12px;font-size:13px;color:var(--muted)}
        .card-value{font-size:28px;font-weight:700;line-height:1}
        .card-sub{font-size:11px;color:var(--muted);margin-top:6px}
        .main-grid{display:grid;grid-template-columns:1fr 450px;gap:16px;margin-bottom:16px}
        @media(max-width:1200px){.main-grid{grid-template-columns:1fr}}
        .panel{background:var(--card);backdrop-filter:blur(20px);border:1px solid rgba(80,90,120,0.3);border-radius:16px;margin-bottom:16px}
        .panel-header{display:flex;justify-content:space-between;align-items:center;padding:16px 20px;border-bottom:1px solid rgba(100,115,150,0.2)}
        .panel-title{display:flex;align-items:center;gap:8px;font-size:15px;font-weight:600}
        .panel-body{padding:20px}
        .msg-list{max-height:300px;overflow-y:auto}
        .msg-item{display:flex;gap:12px;padding:12px;margin-bottom:8px;background:rgba(0,212,255,0.05);border-radius:8px;border-left:3px solid #00d4ff;transition:all 0.2s}
        .msg-item:hover{background:rgba(0,212,255,0.1);transform:translateX(4px)}
        .msg-avatar{width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,var(--blue),#00d4ff);display:flex;align-items:center;justify-content:center;font-size:16px;font-weight:700;color:white;flex-shrink:0}
        .msg-content{flex:1}
        .msg-user{font-size:13px;font-weight:600;margin-bottom:4px}
        .msg-text{font-size:13px;color:var(--muted);line-height:1.5}
        .msg-time{font-size:11px;color:var(--muted);margin-top:4px}
        .log-list{max-height:400px;overflow-y:auto}
        .log-item{padding:12px;margin-bottom:8px;border-radius:8px;border-left:3px solid var(--blue);transition:all 0.2s;position:relative}
        .log-item:hover{transform:translateX(4px)}
        .log-item.info{background:rgba(74,158,255,0.05)}
        .log-item.error{background:rgba(231,76,60,0.1);border-left-color:var(--red)}
        .log-item.completed{background:rgba(46,204,113,0.05);border-left-color:var(--green)}
        .log-item.running{background:rgba(241,196,15,0.05);border-left-color:var(--yellow)}
        .log-time{font-size:11px;color:var(--muted);margin-right:12px}
        .log-task{font-size:13px;font-weight:600;color:var(--text);margin-right:8px}
        .log-status{font-size:11px;padding:2px 8px;border-radius:4px;display:inline-block;margin-right:8px}
        .log-status.completed{background:rgba(46,204,113,0.2);color:var(--green)}
        .log-status.failed{background:rgba(231,76,60,0.2);color:var(--red)}
        .log-status.running{background:rgba(241,196,15,0.2);color:var(--yellow)}
        .log-message{font-size:12px;color:var(--muted)}
        .queue-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}
        .queue-stat{text-align:center;padding:16px;background:rgba(0,0,0,0.2);border-radius:8px;position:relative;cursor:pointer}
        .queue-stat:hover{background:rgba(74,158,255,0.1)}
        .queue-stat.has-detail::after{content:'📋';position:absolute;top:4px;right:8px;font-size:12px}
        .queue-icon{font-size:20px;margin-bottom:8px}
        .queue-value{font-size:20px;font-weight:700;color:var(--blue)}
        .queue-label{font-size:11px;color:var(--muted)}
        .ref-list{max-height:250px;overflow-y:auto}
        .ref-item{padding:12px;margin-bottom:8px;background:rgba(155,89,182,0.05);border-radius:8px;border-left:3px solid var(--purple)}
        .ref-time{font-size:11px;color:var(--muted);margin-bottom:4px}
        .ref-summary{font-size:13px;color:var(--text);line-height:1.5}
        .chart-box{height:200px}
        .session-list{max-height:200px;overflow-y:auto}
        .session-item{padding:10px;margin-bottom:6px;background:rgba(74,158,255,0.05);border-radius:6px;display:flex;justify-content:space-between;align-items:center}
        .session-name{font-size:13px;font-weight:600}
        .session-meta{font-size:11px;color:var(--muted)}
        .diagnostic-box{background:rgba(241,196,15,0.05);border:1px solid rgba(241,196,15,0.3);border-radius:8px;padding:12px;margin-top:12px}
        .diagnostic-title{font-size:13px;font-weight:600;color:var(--yellow);margin-bottom:8px}
        .diagnostic-item{font-size:12px;color:var(--muted);margin-bottom:4px;padding-left:16px;position:relative}
        .diagnostic-item::before{content:'•';color:var(--yellow);position:absolute;left:0}
        .tooltip{position:relative}
        .tooltip:hover::after{content:attr(data-tip);position:absolute;bottom:100%;left:50%;transform:translateX(-50%);background:rgba(0,0,0,0.9);color:white;padding:8px 12px;border-radius:6px;font-size:12px;white-space:nowrap;z-index:1000;margin-bottom:4px}
        .export-btn{padding:6px 16px;background:var(--blue);border:none;border-radius:6px;color:white;font-size:12px;cursor:pointer;transition:all 0.2s}
        .export-btn:hover{background:#3a8eef}
    </style>
</head>
<body>
    <div class="container">
        <nav class="nav">
            <div class="brand"><span class="brand-emoji">🧠</span>VectorBrain 企业级指挥中心</div>
            <div class="nav-right">
                <span class="uptime" id="uptime">运行时间：0 分钟</span>
                <div class="status"><span class="status-dot" id="status-dot"></span><span class="status-text" id="status-text">系统运行正常</span></div>
            </div>
        </nav>
        
        <div class="grid">
            <div class="card primary tooltip" id="health-card" data-tip=""><div class="card-header"><span>💚</span>系统健康</div><div class="card-value" id="health" style="color:var(--green)">正常</div><div class="card-sub">实时诊断</div></div>
            <div class="card"><div class="card-header"><span>📊</span>CPU</div><div class="card-value" id="cpu" style="color:var(--blue)">0%</div><div class="card-sub">使用率</div></div>
            <div class="card"><div class="card-header"><span>💾</span>内存</div><div class="card-value" id="mem" style="color:var(--purple)">0%</div><div class="card-sub">使用率</div></div>
            <div class="card"><div class="card-header"><span>⏱️</span>运行时长</div><div class="card-value" id="uptime-val" style="color:var(--green)">0 分钟</div><div class="card-sub">持续运行</div></div>
            <div class="card tooltip" id="pending-card" data-tip=""><div class="card-header"><span>📋</span>待处理</div><div class="card-value" id="pending" style="color:var(--yellow)">0</div><div class="card-sub">任务队列</div></div>
            <div class="card"><div class="card-header"><span>🧠</span>记忆库</div><div class="card-value" id="memory" style="color:var(--blue)">0</div><div class="card-sub">总记录</div></div>
            <div class="card"><div class="card-header"><span>💡</span>经验库</div><div class="card-value" id="exp" style="color:var(--cyan)">0</div><div class="card-sub">模式数</div></div>
            <div class="card"><div class="card-header"><span>💭</span>反思</div><div class="card-value" id="ref" style="color:var(--purple)">0</div><div class="card-sub">记录数</div></div>
        </div>
        
        <div class="main-grid">
            <div>
                <div class="panel"><div class="panel-header"><div class="panel-title"><span>💬</span>对话流</div></div><div class="panel-body"><div class="msg-list" id="msgs"><div style="text-align:center;color:var(--muted);padding:20px">等待消息...</div></div></div></div>
                <div class="panel"><div class="panel-header"><div class="panel-title"><span>📜</span>任务流（实时解析）</span></div><div style="font-size:12px;color:var(--muted)">✅ 自动翻译大白话 | ⏰ 时间标记 | 🏷️ 状态识别</div></div><div class="panel-body"><div class="log-list" id="logs"><div style="text-align:center;color:var(--muted);padding:20px">等待任务...</div></div></div></div>
            </div>
            <div>
                <div class="panel"><div class="panel-header"><div class="panel-title"><span>🚦</span>任务队列</span></div><span class="export-btn" onclick="exportTasks()">📤 导出</span></div><div class="panel-body"><div class="queue-grid"><div class="queue-stat has-detail tooltip" id="qs-pending" data-tip="点击查看详情"><div class="queue-icon">⏳</div><div class="queue-value" id="q-pending">0</div><div class="queue-label">等待中</div></div><div class="queue-stat"><div class="queue-icon">🔄</div><div class="queue-value" id="q-running">0</div><div class="queue-label">执行中</div></div><div class="queue-stat"><div class="queue-icon">✅</div><div class="queue-value" id="q-done">0</div><div class="queue-label">已完成</div></div><div class="queue-stat"><div class="queue-icon">❌</div><div class="queue-value" id="q-fail">0</div><div class="queue-label">失败</div></div></div></div></div>
                <div class="panel"><div class="panel-header"><div class="panel-title"><span>💭</span>反思摘要</span></div></div><div class="panel-body"><div class="ref-list" id="refs"><div style="text-align:center;color:var(--muted);padding:20px">暂无反思</div></div></div></div>
                <div class="panel"><div class="panel-header"><div class="panel-title"><span></span>活跃会话</span></div></div><div class="panel-body"><div class="session-list" id="sessions"><div style="text-align:center;color:var(--muted);padding:20px">无活跃会话</div></div></div></div>
                <div class="panel"><div class="panel-header"><div class="panel-title"><span>📈</span>资源趋势</span></div></div><div class="panel-body"><div class="chart-box"><canvas id="chart"></canvas></div></div></div>
            </div>
        </div>
        
        <div class="panel" id="diagnostic-panel" style="display:none"><div class="panel-header"><div class="panel-title"><span>🔍</span>系统诊断报告</span></div></div><div class="panel-body"><div class="diagnostic-box"><div class="diagnostic-title">🔴 发现的问题</div><div id="diag-issues"></div></div><div class="diagnostic-box" style="background:rgba(74,158,255,0.05);border-color:rgba(74,158,255,0.3)"><div class="diagnostic-title" style="color:var(--blue)">💡 优化建议</div><div id="diag-suggestions"></div></div></div></div>
    </div>
    
    <script>
        const socket=io();let chart,chartData={labels:[],cpu:[],mem:[]},taskDetails=[];
        function initChart(){const ctx=document.getElementById('chart').getContext('2d');chart=new Chart(ctx,{type:'line',data:{labels:[],datasets:[{label:'CPU',data:[],borderColor:'#4a9eff',backgroundColor:'rgba(74,158,255,0.1)',tension:0.4,fill:true},{label:'内存',data:[],borderColor:'#9b59b6',backgroundColor:'rgba(155,89,182,0.1)',tension:0.4,fill:true}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:true}},scales:{y:{beginAtZero:true,max:100,grid:{color:'rgba(80,90,120,0.2)'}},x:{grid:{color:'rgba(80,90,120,0.2)'}}}}});}
        function updateChart(cpu,mem){const now=new Date().toLocaleTimeString('zh-CN',{hour:'2-digit',minute:'2-digit',second:'2-digit'});chartData.labels.push(now);chartData.cpu.push(cpu);chartData.mem.push(mem);if(chartData.labels.length>20){chartData.labels.shift();chartData.cpu.shift();chartData.mem.shift()}chart.data.labels=chartData.labels;chart.data.datasets[0].data=chartData.cpu;chart.data.datasets[1].data=chartData.mem;chart.update('none');}
        function formatUptime(seconds){const h=Math.floor(seconds/3600),m=Math.floor((seconds%3600)/60);return h>0?h+'小时'+m+' 分钟':m+' 分钟'}
        socket.on('state_update',d=>{
            const dot=document.getElementById('status-dot'),txt=document.getElementById('status-text'),h=document.getElementById('health'),hc=document.getElementById('health-card');
            let statusColor='var(--green)',statusText='系统运行正常';
            if(d.system_health==='critical'){statusColor='var(--red)';statusText='系统异常';h.textContent='❌ 异常';h.style.color='var(--red)';hc.classList.add('warning')}
            else if(d.system_health==='warning'){statusColor='var(--yellow)';statusText='需要注意';h.textContent='⚠️ 警告';h.style.color='var(--yellow)';hc.classList.add('warning')}
            else{h.textContent='🟢 正常';h.style.color='var(--green)';hc.classList.remove('warning')}
            dot.style.background=statusColor;txt.textContent=statusText;
            document.getElementById('cpu').textContent=d.cpu_usage.toFixed(1)+'%';
            document.getElementById('mem').textContent=d.memory_usage.toFixed(1)+'%';
            document.getElementById('uptime-val').textContent=formatUptime(d.uptime_seconds);
            document.getElementById('uptime').textContent='运行时间：'+formatUptime(d.uptime_seconds);
            document.getElementById('pending').textContent=d.tasks_pending;
            document.getElementById('memory').textContent=d.memories_total;
            document.getElementById('exp').textContent=d.experiences_total;
            document.getElementById('ref').textContent=d.reflections_count;
            updateChart(d.cpu_usage,d.memory_usage);
            if(d.task_queue){document.getElementById('q-pending').textContent=d.task_queue.pending||0;document.getElementById('q-running').textContent=d.task_queue.running||0;document.getElementById('q-done').textContent=d.task_queue.completed||0;document.getElementById('q-fail').textContent=d.task_queue.failed||0}
            taskDetails=d.task_details||[];
            const pc=document.getElementById('pending-card');
            if(taskDetails.length>0){pc.setAttribute('data-tip',taskDetails.map(t=>t.name).join('， '));pc.classList.add('tooltip')}
            const qsPending=document.getElementById('qs-pending');
            if(taskDetails.length>0){qsPending.setAttribute('data-tip',taskDetails.map(t=>'📋 '+t.name+' ('+t.created+')').join('\\n'));qsPending.classList.add('tooltip')}
            if(d.health_suggestions&&d.health_suggestions.length>0){document.getElementById('diagnostic-panel').style.display='block';document.getElementById('diag-issues').innerHTML=d.health_issues.map(i=>'<div class="diagnostic-item">• '+i+'</div>').join('');document.getElementById('diag-suggestions').innerHTML=d.health_suggestions.map(s=>'<div class="diagnostic-item">• '+s+'</div>').join('')}
            const mc=document.getElementById('msgs');
            if(d.feishu_messages&&d.feishu_messages.length>0){mc.innerHTML='';d.feishu_messages.forEach(m=>{const div=document.createElement('div');div.className='msg-item';const ini=(m.user||'U').substring(0,2).toUpperCase();div.innerHTML='<div class="msg-avatar">'+ini+'</div><div class="msg-content"><div class="msg-user">'+(m.user||'未知用户')+'</div><div class="msg-text">'+(m.content||'')+'</div><div class="msg-time">'+(m.timestamp||'')+'</div></div>';mc.appendChild(div)});mc.scrollTop=mc.scrollHeight}
            const lc=document.getElementById('logs');
            if(d.parsed_logs&&d.parsed_logs.length>0){lc.innerHTML='';d.parsed_logs.slice(0,20).forEach(l=>{const div=document.createElement('div');div.className='log-item '+(l.type||'info');const statusClass=l.status==='completed'?'completed':l.status==='failed'?'failed':l.status==='running'?'running':'';div.innerHTML='<span class="log-time">'+l.time+'</span><span class="log-task">['+l.task+']</span><span class="log-status '+statusClass+'">'+(l.status==='completed'?'✅ 完成':l.status==='failed'?'❌ 失败':'🔄 进行中')+'</span><span class="log-message">'+l.message+'</span>';lc.appendChild(div)});lc.scrollTop=lc.scrollHeight}
            const rc=document.getElementById('refs');
            if(d.reflections&&d.reflections.length>0){rc.innerHTML='';d.reflections.forEach(r=>{const div=document.createElement('div');div.className='ref-item';div.innerHTML='<div class="ref-time">🕐 '+r.time+'</div><div class="ref-summary">'+r.summary+'</div>';rc.appendChild(div)})}
            const sc=document.getElementById('sessions');
            if(d.active_sessions&&d.active_sessions.length>0){sc.innerHTML='';d.active_sessions.forEach(s=>{const div=document.createElement('div');div.className='session-item';div.innerHTML='<div class="session-name">'+(s.label||s.id)+'</div><div class="session-meta">'+s.model+' · '+s.tokens+' tokens · '+s.updated+'</div>';sc.appendChild(div)})}
        });
        function exportTasks(){const data=taskDetails.map(t=>t.name+'\\t'+t.status+'\\t'+t.created).join('\\n');const blob=new Blob([data],{type:'text/plain'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='tasks-'+new Date().toISOString().split('T')[0]+'.txt';a.click();URL.revokeObjectURL(url)}
        document.addEventListener('DOMContentLoaded',initChart);
    </script>
</body>
</html>'''

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@socketio.on('connect')
def connect(): print("[VB v4] ✅ 客户端已连接"); emit('state_update', state)

def run():
    threading.Thread(target=background_update, daemon=True).start()
    print("="*60)
    print("🧠 VectorBrain 企业级指挥中心 v4")
    print("="*60)
    print("  🌐 地址：http://localhost:18790")
    print("  ✨ 新增功能:")
    print("     - 任务流大白话翻译 + 时间标记 + 状态识别")
    print("     - 反思流智能摘要（可读性提升）")
    print("     - 系统健康诊断 + 修复建议")
    print("     - 任务悬停显示详情")
    print("     - 活跃会话监控")
    print("     - 数据导出功能")
    print("="*60)
    socketio.run(app, host='0.0.0.0', port=18790, debug=False, allow_unsafe_werkzeug=True)

if __name__ == '__main__': run()
