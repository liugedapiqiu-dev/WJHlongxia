#!/usr/bin/env python3
"""
VectorBrain 启动入口文件

用法：
1. 直接运行：python ~/.vectorbrain/run_brain.py
2. 后台运行：nohup python ~/.vectorbrain/run_brain.py &

作用：
- 启动 VectorBrain
- 自动加载所有模块
- 自动运行 Agent Core Loop
"""

import sys
import time
from pathlib import Path

# 添加 VectorBrain src 到路径
VECTORBRAIN_SRC = Path.home() / '.vectorbrain' / 'src'
sys.path.insert(0, str(VECTORBRAIN_SRC))

# 导入所有模块
from planner.planner import get_planner
from goals.goal_manager import get_goal_manager
from reflection.reflection_engine import get_reflection_engine
from opportunity.opportunity_engine import get_opportunity_engine


def start_brain():
    """
    启动 VectorBrain 主循环
    
    基础版本：只扫描机会
    完整版本：运行 Agent Core Loop
    """
    print("🧠 初始化 VectorBrain 模块...")
    
    planner = get_planner()
    goal_manager = get_goal_manager()
    reflection = get_reflection_engine()
    opportunity = get_opportunity_engine()
    
    print("🧠 VectorBrain 启动成功")
    print(f"   Planner: {planner}")
    print(f"   Goal Manager: {goal_manager}")
    print(f"   Reflection: {reflection}")
    print(f"   Opportunity: {opportunity}")
    print("")
    
    print("🔄 进入 Brain Loop...")
    print("   (按 Ctrl+C 停止)")
    print("")
    
    iteration = 0
    
    while True:
        try:
            iteration += 1
            
            print(f"[{iteration}] Brain Loop Running...")
            
            # 扫描机会
            findings = opportunity.scan_environment()
            
            if findings:
                print(f"   ⚡ 发现 {len(findings)} 个机会/问题:")
                for finding in findings:
                    print(f"      [{finding['type']}] {finding['title']}")
                    print(f"          建议：{finding['suggested_action']}")
            else:
                print("   ✓ 未发现明显问题或机会")
            
            # 等待
            time.sleep(10)
            
        except KeyboardInterrupt:
            print("\n\n收到中断信号，停止 Brain Loop...")
            break
        except Exception as e:
            print(f"   ❌ Brain Error: {e}")
            time.sleep(5)
    
    print("VectorBrain 已停止")


if __name__ == "__main__":
    start_brain()
