#!/bin/bash
# VectorBrain 启动脚本

echo "🧠 启动 VectorBrain..."
echo ""

# 检查是否已经在运行
if pgrep -f "agent_core_loop.py" > /dev/null; then
    echo "⚠️  VectorBrain 已经在运行!"
    pgrep -f "agent_core_loop.py" -a
    exit 1
fi

# 启动
echo "启动 Agent Core Loop..."
nohup python3 ~/.vectorbrain/agent_core_loop.py > ~/.vectorbrain/agent_core.log 2>&1 &

PID=$!
echo "✅ VectorBrain 已启动 (PID: $PID)"
echo ""
echo "查看日志：tail -f ~/.vectorbrain/agent_core.log"
echo "停止运行：kill $PID 或 pkill -f agent_core_loop.py"
