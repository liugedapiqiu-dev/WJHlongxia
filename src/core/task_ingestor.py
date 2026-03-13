#!/usr/bin/env python3
"""
VectorBrain Task Ingestor - 任务感知与同步

专门监听 tasks/*.json 文件，自动解析并存入 task_queue.db

这是 VectorBrain 的"海绵体"，吸收所有进入的任务！
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# 添加 VectorBrain src 到路径
import sys
sys.path.append(str(Path.home() / '.vectorbrain' / 'src'))

from task_manager import get_task_manager

# 任务目录
TASKS_DIR = Path.home() / '.vectorbrain' / 'tasks'

# 已处理的任务记录（内存中）
processed_tasks = set()


class TaskIngestor:
    """
    任务 ingestor - 监听并吸收任务
    
    就像海绵体一样，吸收所有进入 tasks/ 目录的 JSON 文件！
    """
    
    def __init__(self):
        """初始化 ingestor"""
        self.task_manager = get_task_manager()
        self.scan_interval = 2  # 每 2 秒扫描一次
        self.last_scan_time = 0
        
        # 确保任务目录存在
        TASKS_DIR.mkdir(parents=True, exist_ok=True)
        
        print(f"[TaskIngestor] 已初始化")
        print(f"  监听目录：{TASKS_DIR}")
        print(f"  扫描间隔：{self.scan_interval}秒")
    
    def scan_for_tasks(self) -> List[Dict]:
        """
        扫描任务目录，发现新的 JSON 文件
        
        Returns:
            新任务列表
        """
        new_tasks = []
        
        if not TASKS_DIR.exists():
            return new_tasks
        
        for task_file in TASKS_DIR.glob("*.json"):
            task_id = task_file.stem
            
            # 跳过已处理的任务
            if task_id in processed_tasks:
                continue
            
            try:
                # 读取并解析 JSON
                with open(task_file, 'r', encoding='utf-8') as f:
                    task_data = json.load(f)
                
                print(f"[TaskIngestor] 📬 发现新任务：{task_id}")
                print(f"  任务名称：{task_data.get('task_name', 'unknown')}")
                print(f"  优先级：{task_data.get('priority', 5)}")
                
                new_tasks.append({
                    'file': task_file,
                    'data': task_data,
                    'task_id': task_id
                })
                
            except Exception as e:
                print(f"[TaskIngestor] ❌ 读取任务失败 {task_file}: {e}")
        
        return new_tasks
    
    def ingest_task(self, task_file: Path, task_data: Dict) -> bool:
        """
        吸收任务到 task_queue.db
        
        Args:
            task_file: 任务文件路径
            task_data: 任务数据
            
        Returns:
            是否成功
        """
        try:
            # 创建任务到 task_queue.db
            task_id = self.task_manager.create_task(
                title=task_data.get('task_name', task_data.get('title', 'unknown')),
                description=task_data.get('description', '') or f"从 {task_file.name} 导入",
                priority=task_data.get('priority', 5),
                created_by=task_data.get('submitted_by', 'ingestor')
            )
            
            print(f"[TaskIngestor] ✅ 任务已存入数据库：{task_id}")
            
            # 标记为已处理
            processed_tasks.add(task_file.stem)
            
            # 可选：删除原始 JSON 文件（避免重复处理）
            # task_file.unlink()
            
            return True
            
        except Exception as e:
            print(f"[TaskIngestor] ❌ 吸收任务失败：{e}")
            return False
    
    def run(self, duration: int = None):
        """
        运行监听器
        
        Args:
            duration: 运行时长（秒），None 表示持续运行
        """
        print(f"[TaskIngestor] 🚀 开始监听任务...")
        
        start_time = time.time()
        scan_count = 0
        
        try:
            while True:
                current_time = time.time()
                
                # 检查是否超过运行时长
                if duration and (current_time - start_time) > duration:
                    print(f"[TaskIngestor] ⏱️  达到运行时长 ({duration}秒)，停止监听")
                    break
                
                # 扫描新任务
                new_tasks = self.scan_for_tasks()
                
                if new_tasks:
                    print(f"[TaskIngestor] 📥 吸收 {len(new_tasks)} 个新任务...")
                    
                    for task in new_tasks:
                        success = self.ingest_task(task['file'], task['data'])
                        
                        if success:
                            # 删除已处理的 JSON 文件
                            try:
                                task['file'].unlink()
                                print(f"  🗑️  已清理：{task['file'].name}")
                            except Exception as e:
                                print(f"  ⚠️  清理失败：{e}")
                
                scan_count += 1
                self.last_scan_time = current_time
                
                # 等待下一次扫描
                time.sleep(self.scan_interval)
        
        except KeyboardInterrupt:
            print(f"\n[TaskIngestor] 🛑 收到中断信号，停止监听")
        
        print(f"[TaskIngestor] 📊 扫描统计：{scan_count}次扫描，{len(processed_tasks)}个任务已处理")


def ingest_existing_tasks():
    """
    立即吸收现有任务（一次性）
    
    用于处理积压的任务文件
    """
    print("[TaskIngestor] 🚀 开始吸收现有任务...")
    
    ingestor = TaskIngestor()
    new_tasks = ingestor.scan_for_tasks()
    
    if new_tasks:
        print(f"[TaskIngestor] 📥 发现 {len(new_tasks)} 个待处理任务")
        
        for task in new_tasks:
            success = ingestor.ingest_task(task['file'], task['data'])
            
            if success:
                # 删除原始文件
                try:
                    task['file'].unlink()
                    print(f"  🗑️  已清理：{task['file'].name}")
                except Exception as e:
                    print(f"  ⚠️  清理失败：{e}")
    else:
        print("[TaskIngestor] ℹ️  没有新任务需要处理")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="VectorBrain Task Ingestor")
    parser.add_argument('--continuous', action='store_true', help='持续监听模式')
    parser.add_argument('--duration', type=int, help='运行时长（秒）')
    
    args = parser.parse_args()
    
    if args.continuous:
        # 持续监听模式
        ingestor = TaskIngestor()
        ingestor.run(duration=args.duration)
    else:
        # 一次性吸收现有任务
        ingest_existing_tasks()
