#!/bin/bash
# VectorBrain 停止脚本

echo "🛑 停止 VectorBrain..."

# 查找进程
PIDS=$(pgrep -f "agent_core_loop.py")

if [ -z "$PIDS" ]; then
    echo "⚠️  VectorBrain 未运行"
    exit 0
fi

# 停止
kill $PIDS
echo "✅ VectorBrain 已停止 (PIDs: $PIDS)"
