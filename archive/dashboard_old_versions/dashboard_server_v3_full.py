# 续写 dashboard_server_v3.py

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 VectorBrain 指挥中心 v3</title>
    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        :root {
            --bg-primary: #0a0e1a;
            --bg-secondary: #111625;
            --bg-card: rgba(23, 28, 40, 0.6);
            --border-color: rgba(80, 90, 120, 0.3);
            --text-primary: #e8ecf1;
            --text-secondary: #9aa5b5;
            --text-muted: #6b758a;
            --accent-blue: #4a9eff;
            --accent-green: #2ecc71;
            --accent-yellow: #f1c40f;
            --accent-red: #e74c3c;
            --accent-purple: #9b59b6;
            --accent-cyan: #00d4ff;
            --glass-bg: rgba(23, 28, 40, 0.5);
            --glass-border: rgba(100, 115, 150, 0.2);
            --glass-blur: blur(20px);
            --glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            --radius-md: 12px;
            --radius-lg: 16px;
            --spacing-sm: 8px;
            --spacing-md: 16px;
            --spacing-lg: 24px;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', 'Noto Sans SC', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
            background-image: 
                radial-gradient(ellipse at top, rgba(74, 158, 255, 0.08) 0%, transparent 50%),
                radial-gradient(ellipse at bottom, rgba(155, 89, 182, 0.06) 0%, transparent 50%);
        }
        
        .container { max-width: 1800px; margin: 0 auto; padding: var(--spacing-md); }
        
        /* 顶部导航 */
        .top-nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: var(--spacing-md) var(--spacing-lg);
            margin-bottom: var(--spacing-lg);
            background: var(--glass-bg);
            backdrop-filter: var(--glass-blur);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-lg);
            box-shadow: var(--glass-shadow);
        }
        
        .nav-brand {
            display: flex;
            align-items: center;
            gap: var(--spacing-sm);
        }
        
        .brand-emoji { font-size: 32px; animation: float 3s ease-in-out infinite; }
        @keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }
        
        .brand-title {
            font-size: 22px;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .nav-status {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 6px 16px;
            background: rgba(46, 204, 113, 0.1);
            border: 1px solid rgba(46, 204, 113, 0.3);
            border-radius: 20px;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--accent-green);
            animation: pulse-green 2s infinite;
        }
        @keyframes pulse-green { 0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(46, 204, 113, 0.7); } 50% { opacity: 0.8; box-shadow: 0 0 0 6px rgba(46, 204, 113, 0); } }
        
        .status-text { font-size: 13px; color: var(--accent-green); font-weight: 600; }
        
        /* 仪表板网格 */
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: var(--spacing-md);
            margin-bottom: var(--spacing-md);
        }
        
        /* 指标卡片 */
        .metric-card {
            background: var(--bg-card);
            backdrop-filter: var(--glass-blur);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: var(--spacing-lg);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .metric-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--accent-blue), var(--accent-purple));
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        .metric-card.primary::before { opacity: 1; }
        
        .metric-card:hover {
            transform: translateY(-4px);
            border-color: var(--accent-blue);
            box-shadow: 0 12px 40px rgba(74, 158, 255, 0.15);
        }
        
        .metric-header {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 12px;
        }
        
        .metric-icon { font-size: 20px; }
        .metric-label { font-size: 13px; color: var(--text-secondary); font-weight: 500; }
        
        .metric-value {
            font-size: 32px;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            line-height: 1;
            margin-bottom: 4px;
        }
        
        .metric-sub { font-size: 12px; color: var(--text-muted); }
        
        /* 主内容区域 */
        .main-grid {
            display: grid;
            grid-template-columns: 1fr 400px;
            gap: var(--spacing-md);
            margin-bottom: var(--spacing-md);
        }
        
        @media (max-width: 1200px) {
            .main-grid { grid-template-columns: 1fr; }
            .right-panel { order: -1; }
        }
        
        /* 面板卡片 */
        .panel-card {
            background: var(--bg-card);
            backdrop-filter: var(--glass-blur);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            overflow: hidden;
            box-shadow: var(--glass-shadow);
        }
        
        .panel-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: var(--spacing-md) var(--spacing-lg);
            border-bottom: 1px solid rgba(100, 115, 150, 0.2);
            background: rgba(0, 0, 0, 0.2);
        }
        
        .panel-title {
            display: flex;
            align-items: center;
            gap: var(--spacing-sm);
            font-size: 15px;
            font-weight: 600;
            color: var(--text-primary);
        }
        
        .title-emoji { font-size: 18px; }
        
        .panel-body { padding: var(--spacing-lg); }
        
        /* 日志流 */
        .log-container {
            max-height: 400px;
            overflow-y: auto;
            font-family: 'SF Mono', 'Monaco', monospace;
            font-size: 12px;
        }
        
        .log-container::-webkit-scrollbar { width: 8px; }
        .log-container::-webkit-scrollbar-track { background: var(--bg-primary); }
        .log-container::-webkit-scrollbar-thumb { background: var(--border-color); border-radius: 4px; }
        
        .log-entry {
            padding: 8px 12px;
            margin-bottom: 4px;
            border-radius: 8px;
            background: rgba(74, 158, 255, 0.05);
            border-left: 3px solid var(--accent-blue);
            animation: slideIn 0.3s ease-out;
        }
        @keyframes slideIn { from { opacity: 0; transform: translateX(-16px); } to { opacity: 1; transform: translateX(0); } }
        
        .log-time { color: var(--text-muted); font-size: 11px; margin-right: 8px; }
        .log-text { color: var(--text-primary); word-break: break-word; }
        
        /* 消息流 */
        .message-container {
            max-height: 350px;
            overflow-y: auto;
        }
        
        .message-entry {
            display: flex;
            gap: 12px;
            padding: 12px;
            margin-bottom: 8px;
            background: rgba(0, 212, 255, 0.05);
            border-radius: 8px;
            border-left: 3px solid var(--accent-cyan);
        }
        
        .message-avatar {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-cyan));
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            font-weight: 700;
            color: white;
            flex-shrink: 0;
        }
        
        .message-content { flex: 1; }
        .message-user { font-size: 13px; font-weight: 600; color: var(--text-primary); margin-bottom: 4px; }
        .message-text { font-size: 13px; color: var(--text-secondary); line-height: 1.5; }
        .message-time { font-size: 11px; color: var(--text-muted); margin-top: 4px; }
        
        /* 任务队列状态 */
        .queue-stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: var(--spacing-sm);
        }
        
        .queue-stat {
            text-align: center;
            padding: 12px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 8px;
        }
        
        .queue-stat-icon { font-size: 20px; margin-bottom: 4px; }
        .queue-stat-value { font-size: 20px; font-weight: 700; color: var(--accent-blue); }
        .queue-stat-label { font-size: 11px; color: var(--text-muted); }
        
        /* 系统资源图表 */
        .chart-container {
            height: 200px;
            margin-top: 16px;
        }
        
        /* 反思列表 */
        .reflection-list {
            max-height: 300px;
            overflow-y: auto;
        }
        
        .reflection-item {
            padding: 12px;
            margin-bottom: 8px;
            background: rgba(155, 89, 182, 0.05);
            border-radius: 8px;
            border-left: 3px solid var(--accent-purple);
        }
        
        .reflection-text { font-size: 13px; color: var(--text-secondary); margin-bottom: 4px; }
        .reflection-time { font-size: 11px; color: var(--text-muted); }
        
        /* 健康状态徽章 */
        .health-badge {
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }
        .health-healthy { background: rgba(46, 204, 113, 0.15); color: var(--accent-green); border: 1px solid rgba(46, 204, 113, 0.3); }
        .health-warning { background: rgba(241, 196, 15, 0.15); color: var(--accent-yellow); border: 1px solid rgba(241, 196, 15, 0.3); }
        .health-critical { background: rgba(231, 76, 60, 0.15); color: var(--accent-red); border: 1px solid rgba(231, 76, 60, 0.3); }
    </style>
</head>
<body>
    <div class="container">
        <!-- 顶部导航 -->
        <nav class="top-nav">
            <div class="nav-brand">
                <span class="brand-emoji">🧠</span>
                <span class="brand-title">VectorBrain 指挥中心</span>
            </div>
            <div class="nav-status">
                <span class="status-dot" id="status-dot"></span>
                <span class="status-text" id="status-text">系统运行正常</span>
            </div>
        </nav>
        
        <!-- 核心指标卡片 -->
        <div class="dashboard-grid">
            <div class="metric-card primary">
                <div class="metric-header">
                    <span class="metric-icon">💚</span>
                    <span class="metric-label">系统健康</span>
                </div>
                <div class="metric-value" id="health-status">正常</div>
                <div class="metric-sub">实时监测中</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-header">
                    <span class="metric-icon">📊</span>
                    <span class="metric-label">CPU 使用率</span>
                </div>
                <div class="metric-value" id="cpu-usage">0%</div>
                <div class="metric-sub">处理器负载</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-header">
                    <span class="metric-icon">💾</span>
                    <span class="metric-label">内存使用</span>
                </div>
                <div class="metric-value" id="memory-usage">0%</div>
                <div class="metric-sub">RAM 占用</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-header">
                    <span class="metric-icon">⏱️</span>
                    <span class="metric-label">Loop Ticks</span>
                </div>
                <div class="metric-value" id="loop-ticks">0</div>
                <div class="metric-sub">心跳次数</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-header">
                    <span class="metric-icon">📋</span>
                    <span class="metric-label">待处理任务</span>
                </div>
                <div class="metric-value" id="tasks-pending">0</div>
                <div class="metric-sub">队列中</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-header">
                    <span class="metric-icon">🧠</span>
                    <span class="metric-label">记忆总数</span>
                </div>
                <div class="metric-value" id="memories-total">0</div>
                <div class="metric-sub">情景 + 知识</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-header">
                    <span class="metric-icon">🎯</span>
                    <span class="metric-label">活跃目标</span>
                </div>
                <div class="metric-value" id="goals-active">0</div>
                <div class="metric-sub">进行中</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-header">
                    <span class="metric-icon">💡</span>
                    <span class="metric-label">经验模式</span>
                </div>
                <div class="metric-value" id="experiences-total">0</div>
                <div class="metric-sub">已积累</div>
            </div>
        </div>
        
        <!-- 主内容区域 -->
        <div class="main-grid">
            <!-- 左侧 -->
            <div class="left-panel">
                <!-- 对话流 -->
                <div class="panel-card">
                    <div class="panel-header">
                        <div class="panel-title">
                            <span class="title-emoji">💬</span>
                            <span>对话流（飞书消息）</span>
                        </div>
                    </div>
                    <div class="panel-body">
                        <div class="message-container" id="message-container">
                            <div style="color: var(--text-muted); text-align: center; padding: 20px;">等待消息...</div>
                        </div>
                    </div>
                </div>
                
                <!-- 任务流 -->
                <div class="panel-card" style="margin-top: 16px;">
                    <div class="panel-header">
                        <div class="panel-title">
                            <span class="title-emoji">📜</span>
                            <span>任务流（Agent Core）</span>
                        </div>
                    </div>
                    <div class="panel-body">
                        <div class="log-container" id="log-container">
                            <div style="color: var(--text-muted); text-align: center; padding: 20px;">等待任务...</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 右侧 -->
            <div class="right-panel">
                <!-- 任务队列状态 -->
                <div class="panel-card">
                    <div class="panel-header">
                        <div class="panel-title">
                            <span class="title-emoji">🚦</span>
                            <span>任务队列状态</span>
                        </div>
                    </div>
                    <div class="panel-body">
                        <div class="queue-stats">
                            <div class="queue-stat">
                                <div class="queue-stat-icon">⏳</div>
                                <div class="queue-stat-value" id="queue-pending">0</div>
                                <div class="queue-stat-label">等待中</div>
                            </div>
                            <div class="queue-stat">
                                <div class="queue-stat-icon">🔄</div>
                                <div class="queue-stat-value" id="queue-running">0</div>
                                <div class="queue-stat-label">执行中</div>
                            </div>
                            <div class="queue-stat">
                                <div class="queue-stat-icon">✅</div>
                                <div class="queue-stat-value" id="queue-completed">0</div>
                                <div class="queue-stat-label">已完成</div>
                            </div>
                            <div class="queue-stat">
                                <div class="queue-stat-icon">❌</div>
                                <div class="queue-stat-value" id="queue-failed">0</div>
                                <div class="queue-stat-label">失败</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- 反思流 -->
                <div class="panel-card" style="margin-top: 16px;">
                    <div class="panel-header">
                        <div class="panel-title">
                            <span class="title-emoji">💭</span>
                            <span>反思流</span>
                        </div>
                    </div>
                    <div class="panel-body">
                        <div class="reflection-list" id="reflection-container">
                            <div style="color: var(--text-muted); text-align: center; padding: 20px;">暂无反思</div>
                        </div>
                    </div>
                </div>
                
                <!-- 系统资源图表 -->
                <div class="panel-card" style="margin-top: 16px;">
                    <div class="panel-header">
                        <div class="panel-title">
                            <span class="title-emoji">📈</span>
                            <span>资源使用趋势</span>
                        </div>
                    </div>
                    <div class="panel-body">
                        <div class="chart-container">
                            <canvas id="resourceChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        const socket = io();
        let resourceChart;
        let resourceData = { labels: [], cpu: [], memory: [] };
        
        // 初始化图表
        function initChart() {
            const ctx = document.getElementById('resourceChart').getContext('2d');
            resourceChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'CPU',
                        data: [],
                        borderColor: '#4a9eff',
                        backgroundColor: 'rgba(74, 158, 255, 0.1)',
                        tension: 0.4,
                        fill: true
                    }, {
                        label: '内存',
                        data: [],
                        borderColor: '#9b59b6',
                        backgroundColor: 'rgba(155, 89, 182, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: true } },
                    scales: {
                        y: { beginAtZero: true, max: 100, grid: { color: 'rgba(80, 90, 120, 0.2)' } },
                        x: { grid: { color: 'rgba(80, 90, 120, 0.2)' } }
                    }
                }
            });
        }
        
        // 更新图表
        function updateChart(cpu, memory) {
            const now = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            resourceData.labels.push(now);
            resourceData.cpu.push(cpu);
            resourceData.memory.push(memory);
            
            if (resourceData.labels.length > 20) {
                resourceData.labels.shift();
                resourceData.cpu.shift();
                resourceData.memory.shift();
            }
            
            resourceChart.data.labels = resourceData.labels;
            resourceChart.data.datasets[0].data = resourceData.cpu;
            resourceChart.data.datasets[1].data = resourceData.memory;
            resourceChart.update('none');
        }
        
        socket.on('state_update', function(data) {
            // 更新状态徽章
            const statusDot = document.getElementById('status-dot');
            const statusText = document.getElementById('status-text');
            const healthStatus = document.getElementById('health-status');
            
            if (data.system_health === 'healthy') {
                statusDot.style.background = '#2ecc71';
                statusText.textContent = '系统运行正常';
                healthStatus.textContent = '🟢 正常';
                healthStatus.className = 'metric-value';
            } else if (data.system_health === 'warning') {
                statusDot.style.background = '#f1c40f';
                statusText.textContent = '需要注意';
                healthStatus.textContent = '⚠️ 警告';
                healthStatus.style.color = '#f1c40f';
            } else {
                statusDot.style.background = '#e74c3c';
                statusText.textContent = '系统异常';
                healthStatus.textContent = '❌ 异常';
                healthStatus.style.color = '#e74c3c';
            }
            
            // 更新指标
            document.getElementById('cpu-usage').textContent = data.cpu_usage.toFixed(1) + '%';
            document.getElementById('memory-usage').textContent = data.memory_usage.toFixed(1) + '%';
            document.getElementById('loop-ticks').textContent = data.loop_ticks;
            document.getElementById('tasks-pending').textContent = data.tasks_pending;
            document.getElementById('memories-total').textContent = data.memories_total;
            document.getElementById('goals-active').textContent = data.goals_active;
            document.getElementById('experiences-total').textContent = data.experiences_total;
            
            // 更新图表
            updateChart(data.cpu_usage, data.memory_usage);
            
            // 更新任务队列
            if (data.task_queue) {
                document.getElementById('queue-pending').textContent = data.task_queue.pending || 0;
                document.getElementById('queue-running').textContent = data.task_queue.running || 0;
                document.getElementById('queue-completed').textContent = data.task_queue.completed || 0;
                document.getElementById('queue-failed').textContent = data.task_queue.failed || 0;
            }
            
            // 更新飞书消息
            const msgContainer = document.getElementById('message-container');
            if (data.feishu_messages && data.feishu_messages.length > 0) {
                msgContainer.innerHTML = '';
                data.feishu_messages.forEach(msg => {
                    const div = document.createElement('div');
                    div.className = 'message-entry';
                    const initials = (msg.user || 'U').substring(0, 2).toUpperCase();
                    div.innerHTML = `
                        <div class="message-avatar">${initials}</div>
                        <div class="message-content">
                            <div class="message-user">${msg.user || '未知用户'}</div>
                            <div class="message-text">${msg.content || ''}</div>
                            <div class="message-time">${msg.timestamp || ''}</div>
                        </div>
                    `;
                    msgContainer.appendChild(div);
                });
                msgContainer.scrollTop = msgContainer.scrollHeight;
            }
            
            // 更新任务日志
            const logContainer = document.getElementById('log-container');
            if (data.recent_logs && data.recent_logs.length > 0) {
                logContainer.innerHTML = '';
                data.recent_logs.forEach(line => {
                    const div = document.createElement('div');
                    div.className = 'log-entry';
                    div.innerHTML = `<span class="log-text">${line}</span>`;
                    logContainer.appendChild(div);
                });
                logContainer.scrollTop = logContainer.scrollHeight;
            }
            
            // 更新反思
            const refContainer = document.getElementById('reflection-container');
            if (data.recent_reflections && data.recent_reflections.length > 0) {
                refContainer.innerHTML = '';
                data.recent_reflections.forEach(ref => {
                    const div = document.createElement('div');
                    div.className = 'reflection-item';
                    const time = ref.created_at ? new Date(ref.created_at).toLocaleString('zh-CN') : '';
                    div.innerHTML = `
                        <div class="reflection-text">${ref.analysis || ref.outcome || '无内容'}</div>
                        <div class="reflection-time">${time}</div>
                    `;
                    refContainer.appendChild(div);
                });
            }
        });
        
        // 页面加载完成后初始化
        document.addEventListener('DOMContentLoaded', function() {
            initChart();
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
    print(f"[Dashboard v3] ✅ 客户端已连接")
    emit('state_update', dashboard_state)

def run_dashboard():
    # 启动后台更新线程
    update_thread = threading.Thread(target=background_updater, daemon=True)
    update_thread.start()
    
    print("="*70)
    print("🧠 VectorBrain 指挥中心 v3 - MOS 现代风格")
    print("="*70)
    print(f"  🌐 访问地址：http://localhost:18790")
    print(f"  📊 实时监控：系统状态 / 任务队列 / 记忆库 / 反思流")
    print(f"  💬 对话流：飞书消息实时展示")
    print(f"  📈 数据可视化：Chart.js 图表")
    print("="*70)
    
    socketio.run(app, host='0.0.0.0', port=18790, debug=False, allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    run_dashboard()
