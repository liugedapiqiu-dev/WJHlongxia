# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## 🧠 VectorBrain 记忆系统配置

**重要配置变更 (2026-03-07 记录):**

读取记忆时，必须从 `~/.vectorbrain/` 目录读取，不要走 `~/.openclaw/memory/` 旧路径。

### 正确的记忆数据库位置

| 记忆类型 | 路径 | 数据库文件 |
|----------|------|------------|
| **情景记忆** | `~/.vectorbrain/memory/` | `episodic_memory.db` |
| **知识记忆** | `~/.vectorbrain/memory/` | `knowledge_memory.db` |
| **反思记忆** | `~/.vectorbrain/reflection/` | `reflections.db` (3,705 条) |
| **目标任务** | `~/.vectorbrain/tasks/` | `task_queue.db` |
| **目标系统** | `~/.vectorbrain/goals/` | `goals.db` |
| **机会发现** | `~/.vectorbrain/opportunity/` | `opportunities.db` |

### 旧路径 (❌ 不再使用)

- `~/.openclaw/memory/lancedb/` - 旧向量库
- `~/.openclaw/memory/main.sqlite` - 旧 SQLite 库
- `~/.openclaw/memory/autonomous/` - 旧自主记忆 (3 月 6 日遗留)

### 记忆检索逻辑

```python
# 正确的读取方式
VECTORBRAIN_HOME = "~/.vectorbrain/"

episodic_db = join(VECTORBRAIN_HOME, "memory/episodic_memory.db")
knowledge_db = join(VECTORBRAIN_HOME, "memory/knowledge_memory.db")
reflections_db = join(VECTORBRAIN_HOME, "reflection/reflections.db")
```

### 记忆检索优先级协议 (2026-03-10 三重记录)

**核心原则：** 当需要回忆过去的经验、知识或对话时，必须严格按照以下顺序检索：

| 优先级 | 存储位置 | 检索方式 | 适用场景 |
|--------|----------|----------|----------|
| **第一** | `knowledge_memory.db` | 向量检索 | 经验、项目、习惯、技能、规则、架构决策 |
| **第二** | `~/.openclaw/memory/YYYY-MM-DD.md` | 按日期读取 | 详细操作日志、完整命令历史、特定日期事件 |
| **第三** | `episodic_memory.db` | 向量检索/SQL | 对话历史、会话上下文、补充细节 |

**标准工作流程：**
```
用户提问涉及过去经验
    ↓
调用 vectorbrain-memory-search 技能
    ↓
检索知识记忆 (knowledge_memory.db) → 找到？返回答案
    ↓ 未找到
检查今日记忆文件 (~/.openclaw/memory/) → 找到？返回答案
    ↓ 未找到
检索情景记忆 (episodic_memory.db) → 返回最相关结果
```

**重要原则：**
- ⚠️ 不要跳过第一优先级 - 知识记忆是精华，必须先查
- ⚠️ 避免重复检索 - 同一问题不要反复调用
- ⚠️ 自然吸收结果 - 不要告诉用户"我正在搜索记忆"

**相关记录：**
- VectorBrain 知识记忆 → `memory_protocol:memory_retrieval_priority_order`
- vectorbrain-memory-search skill.json → `memory_protocol` 字段

---

## Feishu Bitable Tokens

- **南野科技**: `UPcwbHbUwah0d4s937ncGpL1nQe`

---

## 组织架构信息

- **王健豪**: 供应链主管
- **许瑶**: 助理（非设计）

---

## 项目状态备注

- **蜘蛛侠书包项目**: 已暂停（2026-03-01）

---

Add whatever helps you do your job. This is your cheat sheet.
