#!/usr/bin/env python3
"""
VectorBrain Memory Migrator v2 - 记忆迁移工具（带备份和清理）

将 ~/.openclaw 的所有知识迁移到 VectorBrain 大脑，并备份到 ~/openclaw 老记录/
"""

import os
import sys
import json
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# 添加 VectorBrain src 到路径
sys.path.append(str(Path.home() / '.vectorbrain' / 'src'))
from memory_manager import get_memory_manager
from experience_manager import get_experience_manager

class MemoryMigratorV2:
    """记忆迁移器 v2（带备份和清理）"""
    
    def __init__(self, backup_dir: str = None):
        """初始化迁移器"""
        self.source_dir = Path.home() / '.openclaw'
        self.backup_dir = Path(backup_dir) if backup_dir else Path.home() / 'openclaw 老记录'
        self.memory = get_memory_manager()
        self.experience = get_experience_manager()
        
        # 统计
        self.stats = {
            'files_scanned': 0,
            'files_migrated': 0,
            'files_backed_up': 0,
            'files_deleted': 0,
            'experience_migrated': 0,
            'knowledge_migrated': 0,
            'episodic_migrated': 0,
            'errors': 0
        }
        
        # 确保备份目录存在
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"[Migrator v2] 已初始化")
        print(f"  源目录：{self.source_dir}")
        print(f"  备份目录：{self.backup_dir}")
        print(f"  目标：~/.vectorbrain/memory/")
    
    def classify_content(self, content: str, file_path: Path) -> str:
        """分类内容"""
        content_lower = content.lower()
        file_path_str = str(file_path).lower()
        
        # 经验类关键词
        experience_keywords = ['失败', '错误', '教训', 'error', 'fail', 'mistake', 'lesson', 'learn']
        if any(kw in content_lower or kw in file_path_str for kw in experience_keywords):
            return 'experience'
        
        # 情景类关键词
        episodic_patterns = [r'\d{4}-\d{2}-\d{2}', r'今天 | 昨天 | 明天|本周 | 上周', r'today|yesterday|tomorrow']
        if any(re.search(pattern, content_lower) for pattern in episodic_patterns):
            if '会议 | 沟通 | 完成 | 做 | 见 | 讨论' in content_lower:
                return 'episodic'
        
        return 'knowledge'
    
    def extract_tags(self, content: str, file_path: Path) -> List[str]:
        """提取语义标签"""
        tags = set()
        
        path_parts = str(file_path).lower().split('/')
        for part in path_parts:
            if part not in ['workspace', 'memory', 'learnings', 'skills', 'openclaw']:
                tags.add(f"#{part.replace('-', '_')}")
        
        business_keywords = {
            'amazon': '#FBA', 'fba': '#FBA', 'qc': '#QC', '质量': '#QC',
            '供应链': '#SupplyChain', '供应商': '#SupplyChain',
            '背包': '#Product_Backpack', '毛巾': '#Product_Towel',
            'ios': '#iOS_App', '停车': '#iOS_Parking', '支付': '#Payment',
            'sku': '#SKU', '库存': '#Inventory', '错误': '#Error',
            '教训': '#Lesson', 'openclaw': '#OpenClaw', 'vectorbrain': '#VectorBrain'
        }
        
        content_lower = content.lower()
        for keyword, tag in business_keywords.items():
            if keyword in content_lower:
                tags.add(tag)
        
        return list(tags)
    
    def backup_file(self, file_path: Path) -> bool:
        """备份文件"""
        try:
            # 计算相对路径
            rel_path = file_path.relative_to(self.source_dir)
            backup_path = self.backup_dir / rel_path
            
            # 创建目录
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 复制文件
            shutil.copy2(file_path, backup_path)
            
            print(f"  💾 已备份：{rel_path}")
            self.stats['files_backed_up'] += 1
            return True
            
        except Exception as e:
            print(f"  ❌ 备份失败 {file_path.name}: {e}")
            self.stats['errors'] += 1
            return False
    
    def migrate_file(self, file_path: Path) -> bool:
        """迁移单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                return True
            
            category = self.classify_content(content, file_path)
            tags = self.extract_tags(content, file_path)
            
            if category == 'experience':
                self.experience.record_error(
                    pattern=f"从 {file_path.name} 中学到的教训",
                    solution=content[:500],
                    category='migration',
                    source_worker='memory_migrator_v2',
                    tags=tags
                )
                self.stats['experience_migrated'] += 1
                print(f"  [经验] {file_path.name} → error_patterns.db")
                
            elif category == 'episodic':
                self.memory.save_memory(
                    'episodic',
                    {
                        'timestamp': datetime.utcnow().isoformat(),
                        'event_type': 'migrated_memory',
                        'content': content[:1000],
                        'metadata': {
                            'source_file': str(file_path),
                            'migrated_at': datetime.utcnow().isoformat(),
                            'tags': tags
                        }
                    },
                    'memory_migrator_v2'
                )
                self.stats['episodic_migrated'] += 1
                print(f"  [情景] {file_path.name} → episodic_memory.db")
                
            else:  # knowledge
                title = file_path.stem.replace('-', ' ').replace('_', ' ').title()
                self.memory.save_memory(
                    'knowledge',
                    {
                        'category': 'migrated_knowledge',
                        'key': title,
                        'value': content[:2000],
                        'source_worker': 'memory_migrator_v2',
                        'metadata': {
                            'source_file': str(file_path),
                            'tags': tags
                        }
                    },
                    'memory_migrator_v2'
                )
                self.stats['knowledge_migrated'] += 1
                print(f"  [知识] {file_path.name} → knowledge_memory.db")
            
            self.stats['files_migrated'] += 1
            return True
            
        except Exception as e:
            print(f"  ❌ 迁移失败 {file_path.name}: {e}")
            self.stats['errors'] += 1
            return False
    
    def delete_original(self, file_path: Path) -> bool:
        """删除原文件"""
        try:
            file_path.unlink()
            print(f"  🗑️  已删除：{file_path.name}")
            self.stats['files_deleted'] += 1
            return True
        except Exception as e:
            print(f"  ❌ 删除失败 {file_path.name}: {e}")
            self.stats['errors'] += 1
            return False
    
    def run_migration(self, delete_originals: bool = True):
        """执行迁移"""
        print(f"\n[Migrator v2] 开始迁移...")
        print(f"  删除原文件：{delete_originals}")
        print("")
        
        targets = [
            self.source_dir / 'workspace' / '.learnings',
            self.source_dir / 'workspace' / 'memory',
            self.source_dir / 'workspace' / 'SOUL.md',
            self.source_dir / 'workspace' / 'IDENTITY.md',
            self.source_dir / 'workspace' / 'USER.md',
            self.source_dir / 'workspace' / 'AGENTS.md',
            self.source_dir / 'memory' / '2026-03-06.md',
        ]
        
        for target in targets:
            if not target.exists():
                continue
            
            if target.is_file():
                print(f"\n📄 处理文件：{target.name}")
                
                # 1. 备份
                self.backup_file(target)
                
                # 2. 迁移
                if self.migrate_file(target):
                    # 3. 删除原文件
                    if delete_originals:
                        self.delete_original(target)
            
            elif target.is_dir():
                print(f"\n📁 处理目录：{target.relative_to(self.source_dir)}")
                for md_file in target.rglob('*.md'):
                    if 'node_modules' in str(md_file):
                        continue
                    
                    self.stats['files_scanned'] += 1
                    
                    print(f"\n  文件：{md_file.relative_to(target)}")
                    
                    # 1. 备份
                    self.backup_file(md_file)
                    
                    # 2. 迁移
                    if self.migrate_file(md_file):
                        # 3. 删除原文件
                        if delete_originals:
                            self.delete_original(md_file)
        
        # 输出统计
        print("\n" + "="*60)
        print("[Migrator v2] 迁移完成统计:")
        print(f"  扫描文件数：{self.stats['files_scanned']}")
        print(f"  备份文件数：{self.stats['files_backed_up']}")
        print(f"  迁移文件数：{self.stats['files_migrated']}")
        print(f"    - 经验类：{self.stats['experience_migrated']}")
        print(f"    - 知识类：{self.stats['knowledge_migrated']}")
        print(f"    - 情景类：{self.stats['episodic_migrated']}")
        print(f"  删除文件数：{self.stats['files_deleted']}")
        print(f"  错误数：{self.stats['errors']}")
        print("="*60)
        
        if self.stats['errors'] == 0:
            print("\n✅ 迁移成功完成！")
        else:
            print(f"\n⚠️  迁移完成，但有 {self.stats['errors']} 个错误")


if __name__ == "__main__":
    backup_dir = str(Path.home() / 'openclaw 老记录')
    migrator = MemoryMigratorV2(backup_dir=backup_dir)
    migrator.run_migration(delete_originals=True)
