#!/usr/bin/env python3
"""
VectorBrain Agent Core - AI 操作系统主循环

这是整个 AI 系统的核心，所有模块都通过这个循环运行。

架构：
VectorBrain (大脑)
    ↓
Agent Core Loop (思考循环)
    ↓
OpenClaw Workers (身体)
"""

import time
import uuid
import signal
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

# 添加 VectorBrain src 到路径
sys.path.insert(0, str(Path.home() / '.vectorbrain' / 'src'))

# 导入所有模块
from memory_manager import get_memory_manager
from task_manager import get_task_manager
from experience_manager import get_experience_manager
from planner import get_planner
from goals import get_goal_manager
from reflection import get_reflection_engine
from opportunity import get_opportunity_engine

# VectorBrain 根目录
VECTORBRAIN_ROOT = Path.home() / '.vectorbrain'
STATE_DIR = VECTORBRAIN_ROOT / 'state'

class AgentCore:
    """
    Agent Core - AI 操作系统主循环
    
    这个循环是整个 AI 系统的核心：
    1. 接收任务
    2. 调用 planner 拆解
    3. 执行任务
    4. 调用 reflection 反思
    5. 写入 memory
    6. opportunity 扫描
    """
    
    def __init__(self, worker_id: str = None):
        """
        初始化 Agent Core
        
        Args:
            worker_id: Worker 标识符
        """
        # 生成 Worker ID
        self.worker_id = worker_id or f"worker_{uuid.uuid4().hex[:8]}"
        self.worker_type = "agent_core"
        self.hostname = Path.home().name
        self.pid = None
        
        # 状态
        self.running = False
        self.last_opportunity_scan = 0
        self.opportunity_scan_interval = 300  # 5 分钟扫描一次
        
        # 统计
        self.stats = {
            'tasks_processed': 0,
            'tasks_success': 0,
            'tasks_failed': 0,
            'reflections_created': 0,
            'opportunities_found': 0,
            'start_time': None,
            'last_task_time': None
        }
        
        # 初始化所有模块
        print(f"[{self.worker_id}] 初始化 VectorBrain 模块...")
        self.memory = get_memory_manager()
        self.tasks = get_task_manager()
        self.experience = get_experience_manager()
        self.planner = get_planner()
        self.goals = get_goal_manager()
        self.reflection = get_reflection_engine()
        self.opportunity = get_opportunity_engine()
        
        print(f"[{self.worker_id}] 所有模块已初始化")
        print(f"[{self.worker_id}] Memory: {self.memory}")
        print(f"[{self.worker_id}] Tasks: {self.tasks}")
        print(f"[{self.worker_id}] Experience: {self.experience}")
        print(f"[{self.worker_id}] Planner: {self.planner}")
        print(f"[{self.worker_id}] Goals: {self.goals}")
        print(f"[{self.worker_id}] Reflection: {self.reflection}")
        print(f"[{self.worker_id}] Opportunity: {self.opportunity}")
    
    def register_worker(self):
        """注册 Worker 到 brain_state.json"""
        import json
        
        state_file = STATE_DIR / 'brain_state.json'
        
        try:
            if state_file.exists():
                with open(state_file, 'r') as f:
                    state = json.load(f)
            else:
                state = {
                    'active_workers': [],
                    'current_goals': [],
                    'system_health': 'initializing',
                    'last_update': datetime.utcnow().isoformat()
                }
            
            # 添加当前 Worker
            worker_info = {
                'worker_id': self.worker_id,
                'worker_type': self.worker_type,
                'hostname': self.hostname,
                'pid': self.pid,
                'status': 'active',
                'registered_at': datetime.utcnow().isoformat()
            }
            
            # 移除旧的相同 worker
            state['active_workers'] = [
                w for w in state['active_workers']
                if w.get('worker_id') != self.worker_id
            ]
            
            # 添加新 worker
            state['active_workers'].append(worker_info)
            state['last_update'] = datetime.utcnow().isoformat()
            
            # 保存
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
            
            print(f"[{self.worker_id}] 已注册到 brain_state.json")
            
        except Exception as e:
            print(f"[{self.worker_id}] 注册失败：{e}")
    
    def unregister_worker(self):
        """注销 Worker"""
        import json
        
        state_file = STATE_DIR / 'brain_state.json'
        
        try:
            if state_file.exists():
                with open(state_file, 'r') as f:
                    state = json.load(f)
                
                # 移除当前 worker
                state['active_workers'] = [
                    w for w in state['active_workers']
                    if w.get('worker_id') != self.worker_id
                ]
                state['last_update'] = datetime.utcnow().isoformat()
                
                with open(state_file, 'w') as f:
                    json.dump(state, f, indent=2)
                
                print(f"[{self.worker_id}] 已注销")
                
        except Exception as e:
            print(f"[{self.worker_id}] 注销失败：{e}")
    
    def get_next_task(self) -> Optional[Dict]:
        """
        获取下一个待处理任务
        
        Returns:
            任务字典或 None
        """
        pending_tasks = self.tasks.get_pending_tasks(limit=1)
        
        if pending_tasks:
            task = pending_tasks[0]
            # 分配给当前 worker
            self.tasks.assign_task(task['task_id'], self.worker_id)
            return task
        
        return None
    
    def execute_task(self, task: Dict) -> Dict:
        """
        执行任务
        
        Args:
            task: 任务字典
            
        Returns:
            执行结果
        """
        print(f"[{self.worker_id}] 执行任务：{task['title']}")
        
        # 这里简化实现，实际应该根据任务类型调用不同的执行器
        result = {
            'success': True,
            'output': f"任务 {task['title']} 已完成",
            'details': ''
        }
        
        # 模拟执行
        time.sleep(1)
        
        return result
    
    def run_main_loop(self):
        """
        主循环
        
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
        self.running = True
        self.stats['start_time'] = datetime.utcnow().isoformat()
        
        print(f"[{self.worker_id}] " + "="*60)
        print(f"[{self.worker_id}] Agent Core 主循环已启动")
        print(f"[{self.worker_id}] Worker ID: {self.worker_id}")
        print(f"[{self.worker_id}] PID: {self.pid}")
        print(f"[{self.worker_id}] " + "="*60)
        
        # 注册 Worker
        self.register_worker()
        
        try:
            while self.running:
                # ========== 1. 接收任务 ==========
                task = self.get_next_task()
                
                if not task:
                    # 没有任务，扫描机会
                    if time.time() - self.last_opportunity_scan > self.opportunity_scan_interval:
                        self._scan_opportunities()
                    
                    # 等待
                    time.sleep(5)
                    continue
                
                self.stats['last_task_time'] = datetime.utcnow().isoformat()
                
                # ========== 2. 调用 planner ==========
                print(f"[{self.worker_id}] 规划任务：{task['title']}")
                plan = self.planner.create_plan(task['title'], steps=5)
                print(f"[{self.worker_id}] 生成 {len(plan)} 个步骤")
                
                # ========== 3. 执行任务 ==========
                print(f"[{self.worker_id}] 执行中...")
                result = self.execute_task(task)
                
                # ========== 4. 调用 reflection ==========
                print(f"[{self.worker_id}] 反思任务结果...")
                reflection_id = self.reflection.reflect(
                    task_id=task['task_id'],
                    outcome=result['output'],
                    success=result['success'],
                    analysis=result.get('details', ''),
                    created_by=self.worker_id
                )
                self.stats['reflections_created'] += 1
                print(f"[{self.worker_id}] 反思记录：{reflection_id}")
                
                # ========== 5. 写入 memory ==========
                print(f"[{self.worker_id}] 写入记忆...")
                memory_id = self.memory.save_memory(
                    'episodic',
                    {
                        'timestamp': datetime.utcnow().isoformat(),
                        'event_type': 'task_completed',
                        'content': f"任务 {task['title']} 已完成",
                        'metadata': {
                            'task_id': task['task_id'],
                            'result': result['output'],
                            'success': result['success']
                        }
                    },
                    self.worker_id
                )
                print(f"[{self.worker_id}] 记忆 ID: {memory_id}")
                
                # ========== 6. opportunity 扫描 ==========
                if time.time() - self.last_opportunity_scan > self.opportunity_scan_interval:
                    self._scan_opportunities()
                
                # 更新统计
                self.stats['tasks_processed'] += 1
                if result['success']:
                    self.stats['tasks_success'] += 1
                else:
                    self.stats['tasks_failed'] += 1
                
                # 完成任务
                if result['success']:
                    self.tasks.complete_task(task['task_id'], result['output'])
                else:
                    self.tasks.fail_task(task['task_id'], result['output'])
                
                print(f"[{self.worker_id}] 任务完成，统计：{self.stats}")
                
                # 短暂等待
                time.sleep(2)
        
        except KeyboardInterrupt:
            print(f"[{self.worker_id}] 收到中断信号，停止主循环...")
        
        finally:
            # 注销 Worker
            self.unregister_worker()
            self.running = False
    
    def _scan_opportunities(self):
        """扫描环境和机会"""
        print(f"[{self.worker_id}] 扫描环境和机会...")
        
        findings = self.opportunity.scan_environment()
        
        if findings:
            print(f"[{self.worker_id}] 发现 {len(findings)} 个问题/机会:")
            for finding in findings:
                print(f"  [{finding['type'].upper()}] {finding['title']} ({finding['severity']})")
                print(f"    建议：{finding['suggested_action']}")
            
            self.stats['opportunities_found'] += len(findings)
        else:
            print(f"[{self.worker_id}] 未发现明显问题或机会")
        
        self.last_opportunity_scan = time.time()
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return self.stats.copy()
    
    def stop(self):
        """停止主循环"""
        self.running = False


# 单例模式
_agent_core_instance = None

def get_agent_core(worker_id: str = None) -> AgentCore:
    """获取 Agent Core 单例"""
    global _agent_core_instance
    if _agent_core_instance is None:
        _agent_core_instance = AgentCore(worker_id)
    return _agent_core_instance


# 信号处理
def signal_handler(sig, frame):
    """处理中断信号"""
    print("\n收到中断信号，正在停止...")
    if _agent_core_instance:
        _agent_core_instance.stop()
    sys.exit(0)


if __name__ == "__main__":
    # 设置信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 设置 PID
    import os
    worker_id = f"agent_{os.getpid()}"
    
    # 创建并运行 Agent Core
    agent = get_agent_core(worker_id)
    agent.pid = os.getpid()
    
    # 启动主循环
    agent.run_main_loop()
