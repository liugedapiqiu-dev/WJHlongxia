#!/usr/bin/env python3
"""
VectorBrain Opportunity Engine - 主动发现引擎
扫描环境，发现问题和机会
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict

# VectorBrain 根目录
VECTORBRAIN_ROOT = Path.home() / '.vectorbrain'
OPPORTUNITY_DIR = VECTORBRAIN_ROOT / 'opportunity'

class OpportunityEngine:
    """主动发现引擎"""
    
    def __init__(self):
        """初始化主动发现引擎"""
        # 确保目录存在
        OPPORTUNITY_DIR.mkdir(parents=True, exist_ok=True)
        
        # 数据库路径
        self.db_path = OPPORTUNITY_DIR / 'opportunities.db'
        
        # 初始化数据库
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 机会/风险表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS opportunities (
                opportunity_id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                severity TEXT DEFAULT 'medium',
                suggested_action TEXT,
                status TEXT DEFAULT 'pending',
                detected_at TEXT DEFAULT CURRENT_TIMESTAMP,
                addressed_at TEXT
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_type ON opportunities(type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_severity ON opportunities(severity)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON opportunities(status)')
        
        conn.commit()
        conn.close()
    
    def scan_environment(self) -> List[Dict]:
        """
        扫描环境，发现问题和机会
        
        Returns:
            发现的问题和机会列表
        """
        findings = []
        
        # 1. 检查磁盘空间
        disk_finding = self._check_disk_space()
        if disk_finding:
            findings.append(disk_finding)
        
        # 2. 检查待处理任务
        task_finding = self._check_pending_tasks()
        if task_finding:
            findings.append(task_finding)
        
        # 3. 检查失败的任务
        failed_task_finding = self._check_failed_tasks()
        if failed_task_finding:
            findings.append(failed_task_finding)
        
        # 4. 检查长时间未更新的目标
        goal_finding = self._check_stale_goals()
        if goal_finding:
            findings.append(goal_finding)
        
        # 5. 检查错误模式
        error_finding = self._check_error_patterns()
        if error_finding:
            findings.append(error_finding)
        
        # 保存发现到数据库
        for finding in findings:
            self._save_opportunity(finding)
        
        return findings
    
    def _check_disk_space(self) -> Dict:
        """检查磁盘空间"""
        try:
            import shutil
            stat = shutil.disk_usage(Path.home())
            usage_percent = (stat.used / stat.total) * 100
            
            if usage_percent > 90:
                return {
                    'type': 'risk',
                    'title': '磁盘空间严重不足',
                    'description': f'磁盘使用率：{usage_percent:.1f}%',
                    'severity': 'high',
                    'suggested_action': '立即清理磁盘空间，删除不必要的文件'
                }
            elif usage_percent > 80:
                return {
                    'type': 'risk',
                    'title': '磁盘空间紧张',
                    'description': f'磁盘使用率：{usage_percent:.1f}%',
                    'severity': 'medium',
                    'suggested_action': '考虑清理磁盘空间'
                }
        except Exception as e:
            pass
        
        return None
    
    def _check_pending_tasks(self) -> Dict:
        """检查待处理任务"""
        try:
            from sys import path
            path.insert(0, str(Path.home() / '.vectorbrain' / 'src'))
            from task_manager import get_task_manager
            
            tm = get_task_manager()
            stats = tm.get_stats()
            pending_count = stats['by_status'].get('pending', 0)
            
            if pending_count > 10:
                return {
                    'type': 'opportunity',
                    'title': '大量待处理任务',
                    'description': f'有 {pending_count} 个任务等待处理',
                    'severity': 'medium',
                    'suggested_action': '建议分配更多 Workers 处理任务队列'
                }
        except Exception:
            pass
        
        return None
    
    def _check_failed_tasks(self) -> Dict:
        """检查失败的任务"""
        try:
            from sys import path
            path.insert(0, str(Path.home() / '.vectorbrain' / 'src'))
            from task_manager import get_task_manager
            
            # 这里简化实现，实际需要查询数据库
            # 检查 experience 数据库中的错误模式
            exp_db = Path.home() / '.vectorbrain' / 'experience' / 'error_patterns.db'
            if exp_db.exists():
                conn = sqlite3.connect(str(exp_db))
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM error_patterns')
                error_count = cursor.fetchone()[0]
                conn.close()
                
                if error_count > 5:
                    return {
                        'type': 'risk',
                        'title': '多个错误模式已记录',
                        'description': f'已记录 {error_count} 个错误模式',
                        'severity': 'medium',
                        'suggested_action': '建议 review 错误模式并制定预防措施'
                    }
        except Exception:
            pass
        
        return None
    
    def _check_stale_goals(self) -> Dict:
        """检查长时间未更新的目标"""
        # 简化实现
        return None
    
    def _check_error_patterns(self) -> Dict:
        """检查错误模式趋势"""
        try:
            exp_db = Path.home() / '.vectorbrain' / 'experience' / 'error_patterns.db'
            if exp_db.exists():
                conn = sqlite3.connect(str(exp_db))
                cursor = conn.cursor()
                cursor.execute('SELECT category, COUNT(*) as count FROM error_patterns GROUP BY category ORDER BY count DESC LIMIT 1')
                row = cursor.fetchone()
                conn.close()
                
                if row and row[1] > 3:
                    return {
                        'type': 'risk',
                        'title': f'{row[0]} 类别错误频发',
                        'description': f'{row[0]} 类别已记录 {row[1]} 个错误',
                        'severity': 'high',
                        'suggested_action': f'建议针对 {row[0]} 类别制定专门的预防措施'
                    }
        except Exception:
            pass
        
        return None
    
    def _save_opportunity(self, finding: Dict) -> str:
        """保存发现到数据库"""
        import uuid
        opportunity_id = f"opp_{uuid.uuid4().hex[:8]}"
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO opportunities 
            (opportunity_id, type, title, description, severity, suggested_action, status)
            VALUES (?, ?, ?, ?, ?, ?, 'pending')
        ''', (
            opportunity_id,
            finding['type'],
            finding['title'],
            finding['description'],
            finding['severity'],
            finding['suggested_action']
        ))
        conn.commit()
        conn.close()
        
        return opportunity_id
    
    def get_opportunities(self, type: str = None, 
                          limit: int = 10) -> List[Dict]:
        """获取发现的机会/风险"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if type:
            cursor.execute('''
                SELECT * FROM opportunities 
                WHERE type = ? AND status = 'pending'
                ORDER BY detected_at DESC 
                LIMIT ?
            ''', (type, limit))
        else:
            cursor.execute('''
                SELECT * FROM opportunities 
                WHERE status = 'pending'
                ORDER BY 
                    CASE severity 
                        WHEN 'high' THEN 1 
                        WHEN 'medium' THEN 2 
                        WHEN 'low' THEN 3 
                    END,
                    detected_at DESC 
                LIMIT ?
            ''', (limit,))
        
        opportunities = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return opportunities
    
    def address_opportunity(self, opportunity_id: str) -> bool:
        """标记机会/风险已处理"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE opportunities 
            SET status = 'addressed',
                addressed_at = ?
            WHERE opportunity_id = ?
        ''', (datetime.utcnow().isoformat(), opportunity_id))
        
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return updated
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        stats = {}
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 总数
        cursor.execute('SELECT COUNT(*) FROM opportunities')
        stats['total'] = cursor.fetchone()[0]
        
        # 按类型统计
        cursor.execute('''
            SELECT type, COUNT(*) as count 
            FROM opportunities 
            GROUP BY type
        ''')
        stats['by_type'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 按严重程度统计
        cursor.execute('''
            SELECT severity, COUNT(*) as count 
            FROM opportunities 
            GROUP BY severity
        ''')
        stats['by_severity'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 按状态统计
        cursor.execute('''
            SELECT status, COUNT(*) as count 
            FROM opportunities 
            GROUP BY status
        ''')
        stats['by_status'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return stats
    
    def __repr__(self):
        stats = self.get_stats()
        return f"OpportunityEngine(findings={stats['total']}, pending={stats['by_status'].get('pending', 0)})"


# 单例模式
_opportunity_engine_instance = None

def get_opportunity_engine() -> OpportunityEngine:
    """获取主动发现引擎单例"""
    global _opportunity_engine_instance
    if _opportunity_engine_instance is None:
        _opportunity_engine_instance = OpportunityEngine()
    return _opportunity_engine_instance


if __name__ == "__main__":
    # 测试
    oe = get_opportunity_engine()
    print(f"Opportunity Engine initialized: {oe}")
    print(f"Stats: {oe.get_stats()}")
    
    # 扫描环境
    print("\n扫描环境...")
    findings = oe.scan_environment()
    
    if findings:
        print(f"发现 {len(findings)} 个问题/机会:")
        for finding in findings:
            print(f"  [{finding['type'].upper()}] {finding['title']} ({finding['severity']})")
            print(f"    {finding['description']}")
            print(f"    建议：{finding['suggested_action']}")
    else:
        print("未发现明显问题或机会")
    
    print(f"\nStats after scan: {oe.get_stats()}")
