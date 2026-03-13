#!/usr/bin/env python3
"""
VectorBrain Memory Migrator - 记忆迁移工具

将 ~/.openclaw 的所有知识迁移到 VectorBrain 大脑

四步操作：
1. Deep Discovery (全盘扫描)
2. Intelligent Triage (三维分流)
3. Semantic Anchoring (语义锚点)
4. Clean & Verify (清理验证)
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# 添加 VectorBrain src 到路径
sys.path.append(str(Path.home() / '.vectorbrain' / 'src'))
from memory_manager import get_memory_manager
from experience_manager import get_experience_manager
from task_manager import get_task_manager

class MemoryMigrator:
    """记忆迁移器"""
    
    def __init__(self):
        """初始化迁移器"""
        self.source_dir = Path.home() / '.openclaw'
        self.memory = get_memory_manager()
        self.experience = get_experience_manager()
        self.tasks = get_task_manager()
        
        # 统计
        self.stats = {
            'files_scanned': 0,
            'files_migrated': 0,
            'experience_migrated': 0,
            'knowledge_migrated': 0,
            'episodic_migrated': 0,
            'errors': 0
        }
        
        print(f"[Migrator] 已初始化")
        print(f"  源目录：{self.source_dir}")
        print(f"  目标：~/.vectorbrain/memory/")
    
    def classify_content(self, content: str, file_path: Path) -> str:
        """
        分类内容
        
        Returns:
            'experience' | 'knowledge' | 'episodic'
        """
        content_lower = content.lower()
        file_path_str = str(file_path).lower()
        
        # 经验类关键词
        experience_keywords = ['失败', '错误', '教训', 'error', 'fail', 'mistake', 'lesson', 'learn']
        if any(kw in content_lower or kw in file_path_str for kw in experience_keywords):
            return 'experience'
        
        # 情景类关键词（日期、时间、事件）
        episodic_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # 日期格式
            r'今天|昨天|明天|本周|上周',
            r'today|yesterday|tomorrow|this week'
        ]
        if any(re.search(pattern, content_lower) for pattern in episodic_patterns):
            # 如果包含具体日期和事件描述，是情景记忆
            if '会议|沟通|完成|做|见|讨论' in content_lower:
                return 'episodic'
        
        # 默认：事实类知识
        return 'knowledge'
    
    def extract_tags(self, content: str, file_path: Path) -> List[str]:
        """
        提取语义标签
        
        Returns:
            标签列表
        """
        tags = set()
        
        # 从文件路径提取
        path_parts = str(file_path).lower().split('/')
        for part in path_parts:
            if part not in ['workspace', 'memory', 'learnings', 'skills']:
                tags.add(f"#{part.replace('-', '_')}")
        
        # 从内容提取关键词
        business_keywords = {
            'amazon': '#FBA',
            'fba': '#FBA',
            'qc': '#QC',
            '质量': '#QC',
            '不合格': '#QC',
            '供应链': '#SupplyChain',
            '供应商': '#SupplyChain',
            '背包': '#Product_Backpack',
            '毛巾': '#Product_Towel',
            'ios': '#iOS_App',
            '停车': '#iOS_Parking',
            '支付': '#Payment',
            'sku': '#SKU',
            '库存': '#Inventory',
            '错误': '#Error',
            '教训': '#Lesson',
            'openclaw': '#OpenClaw',
            'vectorbrain': '#VectorBrain'
        }
        
        content_lower = content.lower()
        for keyword, tag in business_keywords.items():
            if keyword in content_lower:
                tags.add(tag)
        
        return list(tags)
    
    def migrate_file(self, file_path: Path) -> bool:
        """
        迁移单个文件
        
        Returns:
            是否成功
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                return True  # 空文件，跳过
            
            # 分类
            category = self.classify_content(content, file_path)
            
            # 提取标签
            tags = self.extract_tags(content, file_path)
            
            # 分流存储
            if category == 'experience':
                # 经验类 → error_patterns.db
                self.experience.record_error(
                    pattern=f"从 {file_path.name} 中学到的教训",
                    solution=content[:500],  # 截断前 500 字
                    category='migration',
                    source_worker='memory_migrator',
                    tags=tags
                )
                self.stats['experience_migrated'] += 1
                print(f"  [经验] {file_path.name} → error_patterns.db")
                
            elif category == 'episodic':
                # 情景类 → episodic_memory.db
                self.memory.save_memory(
                    'episodic',
                    {
                        'timestamp': datetime.utcnow().isoformat(),
                        'event_type': 'migrated_memory',
                        'content': content[:1000],  # 截断前 1000 字
                        'metadata': {
                            'source_file': str(file_path),
                            'migrated_at': datetime.utcnow().isoformat(),
                            'tags': tags
                        }
                    },
                    'memory_migrator'
                )
                self.stats['episodic_migrated'] += 1
                print(f"  [情景] {file_path.name} → episodic_memory.db")
                
            else:  # knowledge
                # 事实类 → knowledge_memory.db
                # 提取关键信息
                title = file_path.stem.replace('-', ' ').replace('_', ' ').title()
                
                self.memory.save_memory(
                    'knowledge',
                    {
                        'category': 'migrated_knowledge',
                        'key': title,
                        'value': content[:2000],  # 截断前 2000 字
                        'source_worker': 'memory_migrator',
                        'metadata': {
                            'source_file': str(file_path),
                            'tags': tags
                        }
                    },
                    'memory_migrator'
                )
                self.stats['knowledge_migrated'] += 1
                print(f"  [知识] {file_path.name} → knowledge_memory.db")
            
            self.stats['files_migrated'] += 1
            return True
            
        except Exception as e:
            print(f"  ❌ 迁移失败 {file_path.name}: {e}")
            self.stats['errors'] += 1
            return False
    
    def run_migration(self, dry_run: bool = False):
        """
        执行迁移
        
        Args:
            dry_run: 如果为 True，只扫描不迁移
        """
        print(f"\n[Migrator] 开始迁移...")
        print(f"  模式：{'DRY RUN (只扫描)' if dry_run else '实际迁移'}")
        print("")
        
        # 关键目录和文件
        targets = [
            # 学习记录
            self.source_dir / 'workspace' / '.learnings',
            # 记忆文件
            self.source_dir / 'workspace' / 'memory',
            # 核心文档
            self.source_dir / 'workspace' / 'SOUL.md',
            self.source_dir / 'workspace' / 'IDENTITY.md',
            self.source_dir / 'workspace' / 'USER.md',
            self.source_dir / 'workspace' / 'AGENTS.md',
            # OpenClaw 原生记忆
            self.source_dir / 'memory' / '2026-03-06.md',
        ]
        
        # 扫描并迁移
        for target in targets:
            if not target.exists():
                continue
            
            if target.is_file():
                print(f"\n📄 处理文件：{target.name}")
                if not dry_run:
                    self.migrate_file(target)
                else:
                    print(f"  [DRY RUN] 会迁移：{target.name}")
                    self.stats['files_scanned'] += 1
            
            elif target.is_dir():
                print(f"\n📁 处理目录：{target.relative_to(self.source_dir)}")
                for md_file in target.rglob('*.md'):
                    # 跳过 node_modules
                    if 'node_modules' in str(md_file):
                        continue
                    
                    self.stats['files_scanned'] += 1
                    
                    if not dry_run:
                        self.migrate_file(md_file)
                    else:
                        print(f"  [DRY RUN] 会迁移：{md_file.relative_to(target)}")
        
        # 输出统计
        print("\n" + "="*60)
        print("[Migrator] 迁移完成统计:")
        print(f"  扫描文件数：{self.stats['files_scanned']}")
        print(f"  迁移文件数：{self.stats['files_migrated']}")
        print(f"    - 经验类：{self.stats['experience_migrated']}")
        print(f"    - 知识类：{self.stats['knowledge_migrated']}")
        print(f"    - 情景类：{self.stats['episodic_migrated']}")
        print(f"  错误数：{self.stats['errors']}")
        print("="*60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="VectorBrain Memory Migrator")
    parser.add_argument('--dry-run', action='store_true', help='只扫描不迁移')
    
    args = parser.parse_args()
    
    migrator = MemoryMigrator()
    migrator.run_migration(dry_run=args.dry_run)
