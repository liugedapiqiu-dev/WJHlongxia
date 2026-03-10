# 🦞 OpenClaw + VectorBrain 完整备份指南

**版本:** 3.0 (2026-03-10 更新)
**维护人:** 阿豪 🦞
**适用系统:** macOS (Darwin)

---

## 📋 目录

1. [备份概述](#备份概述)
2. [备份内容清单](#备份内容清单)
3. [自动备份脚本](#自动备份脚本)
4. [恢复指南](#恢复指南)
5. [新增功能备份](#新增功能备份)
6. [常见问题](#常见问题)

---

## 📦 备份概述

### 核心目录结构

```
~/.openclaw/
├── workspace/          # 工作区（身份、配置、记忆）
├── skills/             # 技能目录
├── extensions/         # 插件
├── hooks/              # 钩子（boot.md 等）
└── config.json         # 配置文件

~/.vectorbrain/
├── memory/             # 记忆数据库
├── reflection/         # 反思记录
├── tasks/              # 任务队列
├── goals/              # 目标系统
├── connector/          # 连接器脚本
└── src/                # VectorBrain 核心代码
```

### 备份策略

| 类型 | 频率 | 方式 | 存储位置 |
|------|------|------|----------|
| **完整备份** | 每周 | ZIP 压缩包 | Desktop + GitHub |
| **增量备份** | 每日 | Git 提交 | GitHub 私有仓库 |
| **数据库备份** | 实时 | SQLite dump | Desktop + 云存储 |

---

## 📝 备份内容清单

### ✅ 必须备份的核心文件

#### OpenClaw 工作区
- `~/.openclaw/workspace/SOUL.md` - 人格定义
- `~/.openclaw/workspace/USER.md` - 用户信息
- `~/.openclaw/workspace/IDENTITY.md` - 身份配置
- `~/.openclaw/workspace/TOOLS.md` - 工具配置
- `~/.openclaw/workspace/AGENTS.md` - Agent 指南
- `~/.openclaw/workspace/HEARTBEAT.md` - 心跳配置
- `~/.openclaw/config.json` - 主配置
- `~/.openclaw/.env` - 环境变量（敏感！）

#### 技能系统
- `~/.openclaw/skills/` - 所有技能
  - 重点备份新增的 6 个自动化技能
  - 包含 skill.json 和 SKILL.md

#### VectorBrain 核心
- `~/.vectorbrain/memory/episodic_memory.db` - 情景记忆
- `~/.vectorbrain/memory/knowledge_memory.db` - 知识记忆
- `~/.vectorbrain/reflection/reflections.db` - 反思记录
- `~/.vectorbrain/tasks/task_queue.db` - 任务队列
- `~/.vectorbrain/goals/goals.db` - 目标系统

#### 自动化脚本
- `~/.openclaw/skills/brain-health-monitor/` - 健康监控
- `~/.openclaw/skills/memory-extraction-engine/` - 记忆提炼
- `~/.openclaw/skills/auto-reflection-engine/` - 任务反思
- `~/.openclaw/skills/auto-archive-system/` - 归档系统
- `~/.openclaw/skills/knowledge-dedup/` - 去重机制
- `~/.openclaw/skills/auto_skill_checker.py` - 技能检查器

---

## 🤖 自动备份脚本

### 一键备份脚本

创建 `backup_all.sh`:

```bash
#!/bin/bash

BACKUP_NAME="skill-WJH002_$(date +%Y-%m-%d)"
BACKUP_DIR="$HOME/Desktop/$BACKUP_NAME"
ZIP_FILE="$HOME/Desktop/${BACKUP_NAME}.zip"

echo "🦞 开始完整备份..."

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 复制 OpenClaw 工作区
echo "📂 复制 OpenClaw 工作区..."
cp -r ~/.openclaw/workspace "$BACKUP_DIR/"
cp ~/.openclaw/config.json "$BACKUP_DIR/" 2>/dev/null
cp -r ~/.openclaw/skills "$BACKUP_DIR/"
cp -r ~/.openclaw/extensions "$BACKUP_DIR/"
cp -r ~/.openclaw/hooks "$BACKUP_DIR/"

# 复制 VectorBrain 核心
echo "🧠 复制 VectorBrain 核心..."
mkdir -p "$BACKUP_DIR/vectorbrain"
cp ~/.vectorbrain/memory/*.db "$BACKUP_DIR/vectorbrain/" 2>/dev/null
cp ~/.vectorbrain/reflection/*.db "$BACKUP_DIR/vectorbrain/" 2>/dev/null
cp ~/.vectorbrain/tasks/*.db "$BACKUP_DIR/vectorbrain/" 2>/dev/null
cp ~/.vectorbrain/goals/*.db "$BACKUP_DIR/vectorbrain/" 2>/dev/null
cp -r ~/.vectorbrain/connector "$BACKUP_DIR/vectorbrain/"

# 创建 README
cat > "$BACKUP_DIR/README.md" << 'EOF'
# OpenClaw + VectorBrain 备份

**备份日期:** $(date +%Y-%m-%d)
**系统:** macOS
**包含内容:**
- OpenClaw 工作区配置
- VectorBrain 核心数据库
- 自动化技能系统

**恢复说明:**
1. 解压到桌面
2. 复制文件到对应位置
3. 恢复数据库
4. 重启 Gateway

详细恢复指南见主仓库 README.md
EOF

# 压缩备份
echo "📦 创建压缩包..."
cd ~/Desktop
zip -r "${BACKUP_NAME}.zip" "$BACKUP_NAME" -x "*.DS_Store" -x "__pycache__/*" -x "*.pyc"

# 清理临时目录
rm -rf "$BACKUP_DIR"

# 计算哈希
echo "🔐 计算文件哈希..."
shasum -a 256 "$ZIP_FILE" > "${ZIP_FILE}.sha256"

echo ""
echo "✅ 备份完成!"
echo "📍 位置：$ZIP_FILE"
echo "📊 大小：$(du -h "$ZIP_FILE" | cut -f1)"
echo "🔐 SHA256: $(cat ${ZIP_FILE}.sha256)"
```

### 使用方法

```bash
# 赋予执行权限
chmod +x backup_all.sh

# 执行备份
./backup_all.sh
```

---

## 🔄 恢复指南

### 从备份恢复

1. **解压备份**
   ```bash
   unzip skill-WJH002_2026-03-10.zip -d ~/Desktop/
   ```

2. **恢复 OpenClaw**
   ```bash
   cp -r ~/Desktop/skill-WJH002/workspace/* ~/.openclaw/workspace/
   cp ~/Desktop/skill-WJH002/config.json ~/.openclaw/
   cp -r ~/Desktop/skill-WJH002/skills/* ~/.openclaw/skills/
   ```

3. **恢复 VectorBrain**
   ```bash
   cp ~/Desktop/skill-WJH002/vectorbrain/*.db ~/.vectorbrain/memory/
   cp ~/Desktop/skill-WJH002/vectorbrain/*.db ~/.vectorbrain/reflection/
   cp ~/Desktop/skill-WJH002/vectorbrain/*.db ~/.vectorbrain/tasks/
   cp ~/Desktop/skill-WJH002/vectorbrain/*.db ~/.vectorbrain/goals/
   ```

4. **重启服务**
   ```bash
   openclaw gateway restart
   ```

---

## 🆕 新增功能备份

### 第二阶段新增（2026-03-10）

#### 1. 记忆提炼引擎
```bash
~/.openclaw/skills/memory-extraction-engine/
├── memory_extraction_engine.py
└── skill.json
```

#### 2. 任务反思引擎
```bash
~/.openclaw/skills/auto-reflection-engine/
├── auto_reflection_engine.py
└── skill.json
```

#### 3. 大脑健康监控
```bash
~/.openclaw/skills/brain-health-monitor/
├── brain_health_monitor.py
└── skill.json
```

### 第三阶段新增（2026-03-10）

#### 4. 归档系统
```bash
~/.openclaw/skills/auto-archive-system/
├── auto_archive.py
└── skill.json
```

#### 5. 去重机制
```bash
~/.openclaw/skills/knowledge-dedup/
├── knowledge_dedup.py
└── skill.json
```

#### 6. 技能检查器
```bash
~/.openclaw/skills/auto_skill_checker.py
```

---

## ❓ 常见问题

### Q: 备份文件太大怎么办？
**A:** 排除以下目录：
- `~/.openclaw/venv*/` - Python 虚拟环境
- `~/.openclaw/media/` - 媒体文件
- `~/.vectorbrain/*.log` - 日志文件
- `__pycache__/` - Python 缓存

### Q: 如何自动备份？
**A:** 使用 Cron 定时任务：
```bash
# 每周日 凌晨 3 点备份
0 3 * * 0 ~/.openclaw/backup_all.sh
```

### Q: .env 文件包含敏感信息怎么办？
**A:** 
1. 不要将 .env 上传到 GitHub
2. 创建 `.env.example` 作为模板
3. 恢复后手动填入真实的 API Keys

### Q: 数据库恢复后无法启动？
**A:** 
1. 检查文件权限：`chmod 644 ~/.vectorbrain/memory/*.db`
2. 验证数据库：`sqlite3 ~/.vectorbrain/memory/episodic_memory.db ".tables"`
3. 重启 Gateway：`openclaw gateway restart`

---

## 📊 备份验证清单

每次备份后检查：
- [ ] 压缩包创建成功
- [ ] SHA256 哈希已记录
- [ ] 核心文件已包含（SOUL.md, IDENTITY.md 等）
- [ ] 数据库文件已包含
- [ ] 新增技能已包含
- [ ] 备份文件已上传到安全位置

---

**最后更新:** 2026-03-10
**维护状态:** ✅ 活跃维护
**下次审查:** 2026-03-17
