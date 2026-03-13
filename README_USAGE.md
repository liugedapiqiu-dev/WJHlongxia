# VectorBrain 使用说明

## 快速启动

### 方法 1: 使用启动脚本（推荐）

```bash
# 启动
~/.vectorbrain/start.sh

# 查看状态
tail -f ~/.vectorbrain/agent_core.log

# 停止
~/.vectorbrain/stop.sh
```

### 方法 2: 直接运行

```bash
# 前台运行（会阻塞终端）
python ~/.vectorbrain/agent_core_loop.py

# 后台运行
nohup python ~/.vectorbrain/agent_core_loop.py &

# 查看日志
tail -f ~/.vectorbrain/agent_core.log

# 停止
pkill -f agent_core_loop.py
```

### 方法 3: 测试运行（简单版本）

```bash
# 测试运行（只扫描机会）
python ~/.vectorbrain/run_brain.py
```

## 文件说明

| 文件 | 作用 |
|------|------|
| `agent_core_loop.py` | **主循环** - 完整的 AI 操作系统 |
| `run_brain.py` | 简单测试版本 - 只扫描机会 |
| `start.sh` | 启动脚本 |
| `stop.sh` | 停止脚本 |
| `agent_core.log` | 运行日志 |

## 主循环结构

```python
while True:
    1 接收任务 (from Task Queue)
    2 调用 planner (拆解为步骤)
    3 执行任务
    4 调用 reflection (反思结果)
    5 写入 memory (存储记忆)
    6 opportunity 扫描 (发现问题)
    sleep(5)
```

## 系统架构

```
VectorBrain (大脑)
    ↓
Agent Core Loop (思考循环)
    ↓
Planner ←→ Reflection ←→ Memory ←→ Opportunity
```

## 常见问题

### Q: 如何确认 VectorBrain 在运行？

```bash
ps aux | grep agent_core_loop
```

### Q: 日志在哪里？

```bash
tail -f ~/.vectorbrain/agent_core.log
```

### Q: 如何重置 VectorBrain？

```bash
# 停止
~/.vectorbrain/stop.sh

# 清空日志
> ~/.vectorbrain/agent_core.log

# 重新启动
~/.vectorbrain/start.sh
```
