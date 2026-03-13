#!/usr/bin/env python3
"""
VectorBrain Worker Connector - Worker 与 VectorBrain 的连接接口

这个模块说明 OpenClaw Worker 如何调用 VectorBrain。

架构：
VectorBrain (大脑)
    ↓
Agent Core Loop (思考循环)
    ↓
Worker Connector (神经接口)
    ↓
OpenClaw Workers (身体)
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# VectorBrain 根目录
VECTORBRAIN_ROOT = Path.home() / '.vectorbrain'
STATE_DIR = VECTORBRAIN_ROOT / 'state'


class WorkerConnector:
    """
    Worker Connector - OpenClaw Worker 与 VectorBrain 的连接接口
    
    使用方法：
    
    1. OpenClaw Worker 启动时：
       connector = WorkerConnector()
       connector.register_worker("openclaw_main")
    
    2. 执行任务时：
       connector.execute_with_vectorbrain("抓取公司数据")
    
    3. 任务完成后：
       connector.complete_task(result)
    
    4. OpenClaw Worker 关闭时：
       connector.unregister_worker()
    """
    
    def __init__(self, worker_name: str = "unknown"):
        """
        初始化 Worker Connector
        
        Args:
            worker_name: Worker 名称（如：openclaw_main, feishu_bot）
        """
        self.worker_name = worker_name
        self.worker_id = f"{worker_name}_{uuid.uuid4().hex[:8]}"
        self.current_task = None
        
        # 确保 state 目录存在
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        
        print(f"[{self.worker_id}] Worker Connector 已初始化")
    
    def register_worker(self, worker_type: str = "openclaw"):
        """
        注册 Worker 到 brain_state.json
        
        Args:
            worker_type: Worker 类型
        """
        state_file = STATE_DIR / 'brain_state.json'
        
        try:
            # 读取或创建状态文件
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
                'worker_name': self.worker_name,
                'worker_type': worker_type,
                'hostname': Path.home().name,
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
            print(f"[{self.worker_id}] 当前活跃 Workers: {len(state['active_workers'])}")
            
        except Exception as e:
            print(f"[{self.worker_id}] 注册失败：{e}")
    
    def unregister_worker(self):
        """注销 Worker"""
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
    
    def execute_with_vectorbrain(self, task_description: str, priority: int = 5) -> str:
        """
        通过 VectorBrain 执行任务
        
        Args:
            task_description: 任务描述
            priority: 优先级 (1-10)
            
        Returns:
            task_id
        """
        from task_manager import get_task_manager
        from planner import get_planner
        
        tm = get_task_manager()
        planner = get_planner()
        
        # 创建任务
        task_id = tm.create_task(
            title=task_description,
            description=f"由 {self.worker_name} 提交",
            priority=priority,
            created_by=self.worker_id
        )
        
        print(f"[{self.worker_id}] 创建任务：{task_id}")
        print(f"[{self.worker_id}] 任务描述：{task_description}")
        
        # 使用 Planner 拆解任务
        plan = planner.create_plan(task_description, steps=5)
        print(f"[{self.worker_id}] 生成 {len(plan)} 个步骤:")
        for step in plan:
            print(f"  Step{step['step_number']}: {step['description']}")
        
        self.current_task = task_id
        
        return task_id
    
    def complete_task(self, result: str, success: bool = True):
        """
        完成任务并进行反思
        
        Args:
            result: 任务结果
            success: 是否成功
        """
        if not self.current_task:
            print(f"[{self.worker_id}] 没有当前任务")
            return
        
        from task_manager import get_task_manager
        from reflection import get_reflection_engine
        from memory_manager import get_memory_manager
        
        tm = get_task_manager()
        reflection = get_reflection_engine()
        memory = get_memory_manager()
        
        # 完成任务
        if success:
            tm.complete_task(self.current_task, result)
            print(f"[{self.worker_id}] 任务完成：{self.current_task}")
        else:
            tm.fail_task(self.current_task, result)
            print(f"[{self.worker_id}] 任务失败：{self.current_task}")
        
        # 反思
        reflection_id = reflection.reflect(
            task_id=self.current_task,
            outcome=result,
            success=success,
            analysis=f"由 {self.worker_name} 执行",
            created_by=self.worker_id
        )
        print(f"[{self.worker_id}] 反思记录：{reflection_id}")
        
        # 写入记忆
        memory_id = memory.save_memory(
            'episodic',
            {
                'timestamp': datetime.utcnow().isoformat(),
                'event_type': 'task_completed',
                'content': result,
                'metadata': {
                    'task_id': self.current_task,
                    'success': success,
                    'worker': self.worker_name
                }
            },
            self.worker_id
        )
        print(f"[{self.worker_id}] 记忆 ID: {memory_id}")
        
        self.current_task = None
    
    def get_active_workers(self) -> List[Dict]:
        """获取所有活跃的 Workers"""
        state_file = STATE_DIR / 'brain_state.json'
        
        try:
            if state_file.exists():
                with open(state_file, 'r') as f:
                    state = json.load(f)
                return state.get('active_workers', [])
            return []
        except Exception as e:
            print(f"[{self.worker_id}] 获取 Workers 失败：{e}")
            return []
    
    def get_system_status(self) -> Dict:
        """获取系统状态"""
        from task_manager import get_task_manager
        from experience_manager import get_experience_manager
        
        tm = get_task_manager()
        em = get_experience_manager()
        
        return {
            'worker_id': self.worker_id,
            'worker_name': self.worker_name,
            'active_workers': len(self.get_active_workers()),
            'task_stats': tm.get_stats(),
            'experience_stats': em.get_stats(),
            'current_task': self.current_task
        }


# 使用示例
if __name__ == "__main__":
    # 示例：OpenClaw Worker 如何使用 Worker Connector
    
    print("="*60)
    print("Worker Connector 使用示例")
    print("="*60)
    
    # 1. 初始化
    connector = WorkerConnector("openclaw_main")
    
    # 2. 注册 Worker
    connector.register_worker("openclaw")
    
    # 3. 执行任务
    task_id = connector.execute_with_vectorbrain("抓取天眼查公司名称", priority=1)
    
    # 4. 模拟执行
    print(f"\n[{connector.worker_id}] 模拟执行任务...")
    
    # 5. 完成任务
    connector.complete_task(
        result="成功抓取 100 条公司名称",
        success=True
    )
    
    # 6. 获取系统状态
    status = connector.get_system_status()
    print(f"\n[{connector.worker_id}] 系统状态:")
    print(f"  活跃 Workers: {status['active_workers']}")
    print(f"  任务统计：{status['task_stats']}")
    print(f"  经验统计：{status['experience_stats']}")
    
    # 7. 注销 Worker
    connector.unregister_worker()
    
    print("\n示例完成！")
