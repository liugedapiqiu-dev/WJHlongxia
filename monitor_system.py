#!/usr/bin/env python3
"""VectorBrain 任务监控脚本"""

import time
import sys
from pathlib import Path

# 添加 VectorBrain src 到路径
VECTORBRAIN_SRC = Path.home() / '.vectorbrain' / 'src'
sys.path.insert(0, str(VECTORBRAIN_SRC))

from task_manager import get_task_manager
from memory_manager import get_memory_manager
from opportunity.opportunity_engine import get_opportunity_engine

def monitor_system():
    """监控系统状态"""
    tm = get_task_manager()
    mm = get_memory_manager()
    oe = get_opportunity_engine()
    
    print("🧠 VectorBrain 系统监控")
    print("=" * 60)
    print("按 Ctrl+C 停止监控")
    print("=" * 60)
    
    try:
        while True:
            # 获取任务统计
            task_stats = tm.get_stats()
            processed = task_stats['by_status'].get('done', 0) + task_stats['by_status'].get('failed', 0)
            
            # 获取记忆统计
            memory_stats = mm.get_stats()
            
            # 获取机会统计
            opportunity_stats = oe.get_stats()
            
            # 清屏并显示统计信息
            print("\033[H\033[J", end='')  # 清屏
            print("🧠 VectorBrain 系统监控")
            print("=" * 60)
            print(f"任务状态：")
            print(f"  已处理：{processed}")
            print(f"  待处理：{task_stats['by_status'].get('pending', 0)}")
            print(f"  运行中：{task_stats['by_status'].get('running', 0)}")
            print(f"  总任务：{task_stats['total']}")
            print()
            print(f"记忆状态：")
            print(f"  情景记忆：{memory_stats['episodic_count']}")
            print(f"  知识记忆：{memory_stats['knowledge_count']}")
            print()
            print(f"机会状态：")
            print(f"  总发现：{opportunity_stats['total']}")
            print(f"  待处理：{opportunity_stats['by_status'].get('pending', 0)}")
            print()
            print(f"活跃 Workers：{task_stats['active_workers']}")
            print("=" * 60)
            print(f"上次更新：{time.strftime('%Y-%m-%d %H:%M:%S')}")
            print("按 Ctrl+C 停止监控")
            
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n监控停止")

if __name__ == "__main__":
    monitor_system()