#!/usr/bin/env python3
"""
VectorBrain Planner - 规划引擎
将目标拆解为可执行的步骤
"""

import json
from datetime import datetime
from typing import List, Dict
from pathlib import Path

class Planner:
    """规划引擎 - 将目标拆解为步骤"""
    
    def __init__(self):
        """初始化规划引擎"""
        # 预定义的任务模板
        self.task_templates = {
            'development': [
                '需求分析',
                '技术选型',
                '架构设计',
                '数据库设计',
                'API 开发',
                '前端开发',
                '测试',
                '部署'
            ],
            'research': [
                '确定研究范围',
                '收集资料',
                '分析资料',
                '总结结论',
                '输出报告'
            ],
            'web_scraping': [
                '研究目标网站结构',
                '分析 API/HTML',
                '编写爬虫代码',
                '处理反爬机制',
                '解析数据',
                '存储数据',
                '测试验证'
            ],
            'data_analysis': [
                '数据收集',
                '数据清洗',
                '探索性分析',
                '建模分析',
                '可视化',
                '输出结论'
            ]
        }
    
    def create_plan(self, goal: str, steps: int = 5) -> List[Dict]:
        """
        创建计划
        
        Args:
            goal: 目标描述
            steps: 步骤数量
            
        Returns:
            步骤列表
        """
        # 分析目标类型
        goal_lower = goal.lower()
        
        if any(word in goal_lower for word in ['开发', '系统', '软件', 'app', '网站']):
            template = self.task_templates['development']
        elif any(word in goal_lower for word in ['研究', '分析', '调查']):
            template = self.task_templates['research']
        elif any(word in goal_lower for word in ['抓取', '爬虫', 'spider', 'scrape']):
            template = self.task_templates['web_scraping']
        elif any(word in goal_lower for word in ['数据', 'data', '统计']):
            template = self.task_templates['data_analysis']
        else:
            # 通用模板
            template = [
                '理解任务需求',
                '制定方案',
                '执行方案',
                '验证结果',
                '总结反馈'
            ]
        
        # 生成步骤
        plan = []
        for i, task in enumerate(template[:steps], 1):
            plan.append({
                'step_id': f'step_{i:03d}',
                'step_number': i,
                'description': task,
                'status': 'pending',
                'estimated_time': None,
                'dependencies': [f'step_{i-1:03d}'] if i > 1 else [],
                'created_at': datetime.utcnow().isoformat()
            })
        
        return plan
    
    def refine_plan(self, plan: List[Dict], feedback: str) -> List[Dict]:
        """
        根据反馈优化计划
        
        Args:
            plan: 原计划
            feedback: 反馈信息
            
        Returns:
            优化后的计划
        """
        # 简单实现：在计划末尾添加反馈相关的步骤
        if feedback:
            plan.append({
                'step_id': f'step_{len(plan)+1:03d}',
                'step_number': len(plan) + 1,
                'description': f'根据反馈调整：{feedback}',
                'status': 'pending',
                'dependencies': [plan[-1]['step_id']] if plan else [],
                'created_at': datetime.utcnow().isoformat()
            })
        
        return plan
    
    def get_plan_status(self, plan: List[Dict]) -> Dict:
        """获取计划状态"""
        total = len(plan)
        completed = sum(1 for step in plan if step.get('status') == 'completed')
        pending = sum(1 for step in plan if step.get('status') == 'pending')
        running = sum(1 for step in plan if step.get('status') == 'running')
        
        return {
            'total_steps': total,
            'completed': completed,
            'pending': pending,
            'running': running,
            'progress': f'{completed}/{total} ({completed/total*100:.1f}%)' if total > 0 else '0%'
        }
    
    def __repr__(self):
        return "Planner()"


# 单例模式
_planner_instance = None

def get_planner() -> Planner:
    """获取规划引擎单例"""
    global _planner_instance
    if _planner_instance is None:
        _planner_instance = Planner()
    return _planner_instance


if __name__ == "__main__":
    # 测试
    planner = get_planner()
    
    print("测试 1: 开发 ERP 系统")
    plan = planner.create_plan("开发一个 ERP 系统", steps=5)
    for step in plan:
        print(f"  Step{step['step_number']}: {step['description']}")
    
    print("\n测试 2: 抓取天眼查数据")
    plan = planner.create_plan("抓取天眼查公司名称", steps=5)
    for step in plan:
        print(f"  Step{step['step_number']}: {step['description']}")
    
    print("\n计划状态:")
    print(f"  {planner.get_plan_status(plan)}")
