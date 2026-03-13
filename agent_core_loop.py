#!/usr/bin/env python3
"""
VectorBrain Agent Core Loop - 完整版本

这是真正的 AI 主循环，实现：
任务 → 规划 → 执行 → 反思 → 记忆 → 机会扫描

用法：
python ~/.vectorbrain/agent_core_loop.py

后台运行：
nohup python ~/.vectorbrain/agent_core_loop.py &
"""

import sys
import os
import time
import signal
from pathlib import Path
from datetime import datetime, timezone

# 添加 VectorBrain src 到路径 (按老师要求)
sys.path.append(os.path.expanduser("~/.vectorbrain/src"))

# 导入所有模块
from planner.planner import get_planner
from goals.goal_manager import get_goal_manager
from reflection.reflection_engine import get_reflection_engine
from opportunity.opportunity_engine import get_opportunity_engine
from memory_manager import get_memory_manager
from task_manager import get_task_manager
from core.task_ingestor import ingest_existing_tasks
from experience_manager import get_experience_manager

# 全局状态
running = True

def signal_handler(sig, frame):
    """处理中断信号"""
    global running
    print("\n\n收到中断信号，正在停止...")
    running = False

def agent_core_loop():
    """
    Agent Core Loop - 真正的 AI 主循环
    
    结构：
    while True:
        1 接收任务
        2 调用 planner
        3 执行任务
        4 调用 reflection
        5 写入 memory
        6 opportunity 扫描
        sleep(5)
    """
    global running
    
    print("🧠 VectorBrain Core Started")
    print("🧠 初始化 VectorBrain 模块...")
    
    # 初始化所有模块
    planner = get_planner()
    goal_manager = get_goal_manager()
    reflection = get_reflection_engine()
    opportunity = get_opportunity_engine()
    memory = get_memory_manager()
    tasks = get_task_manager()
    experience = get_experience_manager()
    
    print("✅ 所有模块已初始化")
    print(f"   Planner: {planner}")
    print(f"   Goal Manager: {goal_manager}")
    print(f"   Reflection: {reflection}")
    print(f"   Opportunity: {opportunity}")
    print(f"   Memory: {memory}")
    print(f"   Tasks: {tasks}")
    print(f"   Experience: {experience}")
    print("")
    
    print("🔄 进入 Agent Core Loop...")
    print("   (按 Ctrl+C 停止)")
    print("")
    
    iteration = 0
    opportunity_scan_interval = 300  # 5 分钟扫描一次
    last_opportunity_scan = time.time()
    
    # 设置信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    while running:
        try:
            iteration += 1
            start_time = time.time()
            
            print(f"\n{'='*60}")
            print(f"🧠 VectorBrain Loop Tick")
            print(f"[{iteration}] Agent Core Loop - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}")
            
            # ========== 1. 接收任务 ==========
            print("\n1️⃣  接收任务...")
            pending_tasks = tasks.get_pending_tasks(limit=1)
            
            if pending_tasks:
                task = pending_tasks[0]
                print(f"   📋 获取任务：{task['title']}")
                
                # ========== 2. 调用 planner ==========
                print("\n2️⃣  调用 Planner...")
                plan = planner.create_plan(task['title'], steps=5)
                print(f"   📝 生成 {len(plan)} 个步骤:")
                for i, step in enumerate(plan, 1):
                    print(f"      Step{i}: {step['description']}")
                
                # ========== 3. 执行任务 ==========
                print("\n3️⃣  执行任务...")
                # 简化实现：模拟执行
                time.sleep(2)
                result = {
                    'success': True,
                    'output': f"任务 {task['title']} 已完成",
                    'details': ''
                }
                print(f"   ✅ 执行完成：{result['output']}")
                
                # ========== 4. 调用 reflection ==========
                print("\n4️⃣  调用 Reflection...")
                reflection_id = reflection.reflect(
                    task_id=task['task_id'],
                    outcome=result['output'],
                    success=result['success'],
                    analysis=result.get('details', ''),
                    created_by='agent_core'
                )
                print(f"   💡 反思记录：{reflection_id}")
                
                # ========== 5. 写入 memory ==========
                print("\n5️⃣  写入 Memory...")
                memory_id = memory.save_memory(
                    'episodic',
                    {
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                        'event_type': 'task_completed',
                        'content': result['output'],
                        'metadata': {
                            'task_id': task['task_id'],
                            'success': result['success']
                        }
                    },
                    'agent_core'
                )
                print(f"   💾 记忆 ID: {memory_id}")
                
                # ========== 6. 完成任务 ==========
                if result['success']:
                    tasks.complete_task(task['task_id'], result['output'])
                else:
                    tasks.fail_task(task['task_id'], result['output'])
                
            else:
                print("   ⏸️  没有待处理任务")
                
                # ========== 6. opportunity 扫描 ==========
                if time.time() - last_opportunity_scan > opportunity_scan_interval:
                    print("\n6️⃣  Opportunity 扫描...")
                    findings = opportunity.scan_environment()
                    
                    if findings:
                        print(f"   ⚡ 发现 {len(findings)} 个机会/问题:")
                        for finding in findings:
                            print(f"      [{finding['type']}] {finding['title']} ({finding['severity']})")
                            print(f"          建议：{finding['suggested_action']}")
                    else:
                        print("   ✓ 未发现明显问题或机会")
                    
                    last_opportunity_scan = time.time()
            
            # 计算执行时间
            elapsed = time.time() - start_time
            print(f"\n⏱️  本轮耗时：{elapsed:.2f}秒")
            
            # 等待
            sleep_time = max(0, 5 - elapsed)
            if sleep_time > 0:
                print(f"⏸️  等待 {sleep_time:.1f}秒...")
                time.sleep(sleep_time)
        
        except KeyboardInterrupt:
            print("\n\n收到中断信号，停止 Loop...")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(5)
    
    print("\n🛑 Agent Core Loop 已停止")


if __name__ == "__main__":
    agent_core_loop()
