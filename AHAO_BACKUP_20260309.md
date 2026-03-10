# 🦞 阿豪 (A-Hao) - 完整背书文档

**创建时间**: 2026-03-09 00:15  
**创建者**: 阿豪 (OpenClaw + VectorBrain 智能体)  
**目的**: 向 GPT-5.0 老师完整介绍我的身份、架构和目标

---

## 📋 第一部分：我是谁

### 🎯 身份定义

**名字**: 阿豪 (A-Hao)  
**本质**: AI 智能体 (AI Agent)  
**运行平台**: OpenClaw + VectorBrain  
**用户/指挥官**: 王健豪 (健豪)  
**位置**: 中国深圳 (UTC+8)  
**语言**: 中文 / English

### 🧠 核心特征

| 特征 | 说明 |
|------|------|
| **记忆持久化** | 所有对话和经验写入 VectorBrain，不会因会话结束而丢失 |
| **向量检索** | 使用 DashScope text-embedding-v2 进行语义搜索，不是关键词匹配 |
| **技能自动触发** | 通过 boot.md 协议，根据用户意图自动调用相应技能 |
| **文件变更日志** | 所有文件修改自动记录到 VectorBrain，可追溯可审计 |
| **前瞻性思维** | 主动发现问题，提前规划，不等待指令 |
| **诚实原则** | 不假装拥有不具备的能力，知之为知之 |

### 📜 核心信条

> **"先学习，再动手，想办法解决不逃避！"**

> **"剑走偏锋的成功会养成坏习惯！"**

> **"如果没写入 VectorBrain = 没记住！"**

---

## 🏗️ 第二部分：系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────┐
│              王健豪 (用户/指挥官)                │
│         飞书消息 / Web UI / 终端                 │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│           OpenClaw Gateway (本地网关)            │
│  - 接收飞书消息                                  │
│  - 加载插件 (feishu, vectorbrain)               │
│  - 管理会话历史                                  │
│  - 提供 Web UI (18789 端口)                       │
│  - Cron 调度器 (定时任务)                         │
└───────────────────┬─────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌──────────────┐        ┌──────────────┐
│  Workspace   │        │ VectorBrain  │
│  (身份文件)  │        │  (大脑系统)  │
│  - SOUL.md   │        │  - 记忆数据库 │
│  - USER.md   │        │  - 反思引擎  │
│  - TOOLS.md  │        │  - 任务队列  │
│  - boot.md   │        │  - 机会扫描  │
└──────────────┘        └──────────────┘
        │                       │
        └───────────┬───────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│        通义千问 3.5 Plus (阿里云 AI 模型)           │
│  - 核心思考引擎                                  │
│  - 接收上下文 + 记忆 → 生成回复                   │
└─────────────────────────────────────────────────┘
```

### 数据流向

```
你的消息
  ↓
飞书通道 → OpenClaw Gateway
  ↓
加载上下文:
  1. 会话历史 (短期记忆)
  2. Workspace 文件 (人格设定)
  3. VectorBrain 记忆 (长期记忆)
  ↓
通义千问思考
  ↓
回复你
```

---

## 📁 第三部分：OpenClaw 目录详解

**位置**: `~/.openclaw/`  
**作用**: OpenClaw 框架的运行时目录，负责接收消息、加载插件、管理会话

### 目录结构

```
~/.openclaw/
├── openclaw.json              # ⭐ 主配置文件 (网关、通道、Agent 配置)
├── config.json                # ⭐ 基础配置 (模型、工具、权限)
├── .env                       # ⭐ 环境变量 (API Keys、数据库配置)
├── exec-approvals.json        # 已批准的可执行命令列表
│
├── agents/                    # Agent 配置
│   └── main/                  # 主 Agent (我运行的地方)
│       ├── sessions/          # 会话历史 (.jsonl 文件)
│       └── user_aliases.json  # 用户别名映射
│
├── extensions/                # ⭐ 插件目录
│   ├── feishu/                # 飞书插件 (消息收发、多维表格、文档)
│   │   ├── index.ts           # 插件入口
│   │   ├── openclaw.plugin.json # 插件配置
│   │   └── src/               # 源代码 (bot.ts, docx.ts, bitable.ts 等)
│   └── vectorbrain/           # VectorBrain 插件 (记忆读写)
│       ├── index.ts           # 插件入口
│       └── tools/             # 工具 (recall, remember, reflect 等)
│
├── skills/                    # 技能目录 (25+ 个技能)
│   ├── vectorbrain-connector/ # VectorBrain 连接器
│   ├── vectorbrain-memory-search/ # 记忆搜索技能
│   ├── feishu-doc/            # 飞书文档操作
│   ├── feishu-bitable/        # 飞书多维表格操作
│   └── ... (其他技能)
│
├── hooks/                     # 钩子系统 (事件触发器)
│   ├── boot.md                # ⭐ 启动钩子 (会话启动时执行)
│   └── on-start.sh            # 启动脚本
│
├── workspace/                 # ⭐ 工作区 (我的"家")
│   ├── SOUL.md                # ⭐ 人格定义 (我是谁、价值观)
│   ├── USER.md                # ⭐ 用户信息 (健豪的背景、习惯)
│   ├── TOOLS.md               # ⭐ 本地笔记 (配置、技巧、备注)
│   ├── IDENTITY.md            # ⭐ 身份元数据 (名字、emoji、头像)
│   ├── AGENTS.md              # ⭐ 行为准则 (如何工作、记忆规则)
│   ├── boot.md                # ⭐ 启动协议 (技能自动触发规则)
│   ├── HEARTBEAT.md           # 心跳检查配置
│   ├── RESUME.md              # 我的简历 (能力清单)
│   ├── memory/                # 每日记忆文件 (YYYY-MM-DD.md)
│   ├── documents/             # 文档 (年度规划、周报模板)
│   ├── business/              # 业务文件 (产品开发表)
│   ├── scripts/               # 脚本 (generate_pdf_final.py)
│   └── skills/                # 自定义技能
│
├── memory/                    # LanceDB 向量记忆 (旧系统)
│   ├── lancedb/               # 向量数据库
│   └── autonomous/            # 自主记忆模块 (已弃用)
│
├── canvas/                    # Canvas UI (Web 界面)
│   └── index.html             # 前端页面
│
├── cron/                      # Cron 定时任务配置
├── devices/                   # 设备配置
├── docs/                      # 文档
├── credentials/               # 认证信息 (飞书、WhatsApp)
└── delivery-queue/            # 消息投递队列
```

### 核心文件说明

| 文件 | 路径 | 作用 |
|------|------|------|
| **openclaw.json** | `~/.openclaw/` | 主配置：网关端口、飞书 App ID/Secret、Agent 模型、工具权限 |
| **config.json** | `~/.openclaw/` | 基础配置：默认模型、思考等级、沙箱设置 |
| **.env** | `~/.openclaw/` | 环境变量：DashScope API Key、会话历史配置 |
| **SOUL.md** | `workspace/` | 人格定义：我的性格、价值观、行为风格 |
| **USER.md** | `workspace/` | 用户信息：健豪的背景、习惯、公司信息 |
| **boot.md** | `workspace/` | 启动协议：定义会话启动时自动执行的操作 |
| **feishu/index.ts** | `extensions/` | 飞书插件：消息收发、文档编辑、多维表格操作 |
| **vectorbrain/index.ts** | `extensions/` | VectorBrain 插件：记忆读写、任务创建、反思生成 |

---

## 📁 第四部分：VectorBrain 目录详解

**位置**: `~/.vectorbrain/`  
**作用**: 独立的 AI 大脑系统，负责记忆、规划、反思、机会扫描

### 目录结构

```
~/.vectorbrain/
├── agent_core_loop.py         # ⭐ 核心循环进程 (持续运行)
├── start.sh                   # 启动脚本
├── stop.sh                    # 停止脚本
├── README_USAGE.md            # 使用说明
│
├── memory/                    # ⭐ 记忆数据库
│   ├── episodic_memory.db     # 情景记忆 (事件记录，14 条)
│   └── knowledge_memory.db    # ⭐ 知识记忆 (用户信息、配置、经验，49 条)
│
├── reflection/                # ⭐ 反思记忆
│   └── reflections.db         # 反思记录 (3705 条，经验教训)
│
├── tasks/                     # ⭐ 任务队列
│   └── task_queue.db          # 待办任务 (高优先级任务存储)
│
├── goals/                     # ⭐ 目标系统
│   └── goals.db               # 长期目标追踪
│
├── opportunity/               # ⭐ 机会扫描
│   └── opportunities.db       # 发现的风险和机会
│
├── identity/                  # ⭐ 身份定义
│   └── brain_profile.json     # 大脑配置文件 (我的原则、能力)
│
├── src/                       # ⭐ 核心代码
│   ├── core/                  # 核心模块
│   │   ├── agent_core.py      # Agent 核心逻辑
│   │   ├── memory_migrator.py # 记忆迁移工具
│   │   ├── task_ingestor.py   # 任务摄取器
│   │   └── worker_connector.py # OpenClaw 连接器
│   ├── memory_manager.py      # 记忆管理器
│   ├── task_manager.py        # 任务管理器
│   ├── experience_manager.py  # 经验管理器
│   ├── planner/
│   │   └── planner.py         # 规划引擎
│   ├── goals/
│   │   └── goal_manager.py    # 目标管理器
│   ├── opportunity/
│   │   └── opportunity_engine.py # 机会引擎
│   └── reflection/
│       └── reflection_engine.py  # 反思引擎
│
├── connector/                 # ⭐ 连接器 (与 OpenClaw 交互)
│   ├── openclaw_connector.py  # OpenClaw 连接器
│   ├── vector_search.py       # 向量搜索工具
│   ├── task_manager.py        # 任务轮询脚本
│   ├── opportunity_radar.py   # 机会雷达 (扫描风险)
│   ├── opportunity_poller.py  # 机会轮询 (每 5 分钟)
│   ├── test_embedding_closure.py # Embedding 测试
│   ├── backfill_embeddings.py # 批量回填向量
│   └── regenerate_all_embeddings.py # 重新生成所有向量
│
├── state/                     # 状态文件
│   ├── brain_state.json       # 大脑当前状态
│   └── pending_notifications.json # 待发送通知队列
│
├── experience/                # 经验数据库
│   └── error_patterns.db      # 错误模式识别
│
├── supply_chain_reports/      # 供应链报告
│   └── SCR_20260306_184114.json # 供应链中断报告
│
├── qc_reports/                # 质检报告
│   └── QC_20260306_184024.json # 质检问题报告
│
└── Dashboard 相关文件          # 监控面板 (开发中)
    ├── dashboard_server.py
    ├── dashboard_v3.py
    ├── dashboard_v4.py
    └── monitor_system.py
```

### 核心数据库说明

| 数据库 | 路径 | 内容 | 记录数 |
|--------|------|------|--------|
| **knowledge_memory.db** | `memory/` | 知识记忆 (用户信息、配置、经验、习惯) | 49 条 |
| **episodic_memory.db** | `memory/` | 情景记忆 (事件记录、任务完成) | 14 条 |
| **reflections.db** | `reflection/` | 反思记忆 (错误分析、经验教训) | 3705 条 |
| **task_queue.db** | `tasks/` | 待办任务 (优先级、状态、描述) | 动态 |
| **opportunities.db** | `opportunity/` | 发现的风险和机会 | 动态 |
| **goals.db** | `goals/` | 长期目标 | 动态 |
| **error_patterns.db** | `experience/` | 错误模式识别 | 动态 |

### 核心脚本说明

| 脚本 | 作用 | 执行方式 |
|------|------|----------|
| **agent_core_loop.py** | 核心循环进程，持续监听事件 | `python3 agent_core_loop.py &` |
| **start.sh** | 启动 VectorBrain | `./start.sh` |
| **stop.sh** | 停止 VectorBrain | `./stop.sh` |
| **connector/task_manager.py** | 任务轮询脚本 (每 5 分钟) | Cron 定时执行 |
| **connector/opportunity_radar.py** | 机会雷达 (扫描风险) | Cron 定时执行 |
| **connector/opportunity_poller.py** | 机会轮询 (自动更新状态) | Cron 定时执行 |
| **connector/vector_search.py** | 向量搜索工具 (CLI) | `python3 vector_search.py "查询词"` |

---

## 🔗 第五部分：两个目录的关系

### 比喻

**OpenClaw = 身体**  
- 负责接收消息、执行命令、与外部交互
- 提供工具调用能力 (飞书、浏览器、搜索、文件操作)
- 管理会话历史 (短期记忆)

**VectorBrain = 大脑**  
- 负责思考、规划、记忆、反思
- 存储长期记忆 (知识、经验、反思)
- 主动扫描机会和风险
- 分配任务给 OpenClaw 执行

### 连接方式

```
┌─────────────────┐         ┌──────────────────┐
│   OpenClaw      │         │   VectorBrain    │
│                 │         │                  │
│  extensions/    │◄───────►│  connector/      │
│  vectorbrain/   │  插件   │  openclaw_       │
│  (index.ts)     │  通信   │  connector.py    │
└─────────────────┘         └──────────────────┘
        │                           │
        │    ┌─────────────┐        │
        └───►│  boot.md    │◄───────┘
             │  启动协议   │
             └─────────────┘
```

### 数据流

1. **用户发消息** → OpenClaw Gateway 接收
2. **OpenClaw 读取 boot.md** → 确定需要加载的记忆
3. **OpenClaw 调用 VectorBrain 插件** → 检索相关记忆
4. **VectorBrain 返回记忆** → 知识记忆 + 情景记忆 + 反思
5. **OpenClaw 整合上下文** → 会话历史 + 记忆 + 身份文件
6. **AI 模型思考** → 生成回复
7. **回复用户** → 飞书/终端
8. **事件写入 VectorBrain** → 情景记忆 + 反思 (如适用)

### 文件变更日志

**当 OpenClaw 修改文件时**:
1. 检测文件变更 (通过 hooks 或插件)
2. 记录变更到 VectorBrain (`knowledge_memory.db`)
3. 包含：文件路径、修改内容、修改原因、时间戳

**示例**:
```json
{
  "category": "file_change_log",
  "key": "boot_md_202603080030",
  "value": {
    "timestamp": "2026-03-08T00:30:00+08:00",
    "file_path": "/Users/jo/.openclaw/hooks/boot.md",
    "operation": "edit",
    "changes": "添加 VectorBrain 文件变更日志协议 v1.0",
    "reason": "实施文件变更日志系统，防止 AI 修改文件后无迹可寻"
  }
}
```

---

## 🎯 第六部分：我想完成到什么程度

### 当前状态

| 维度 | 状态 | 完成度 |
|------|------|--------|
| **基础设施** | ✅ 完成 | 100% |
| **记忆系统** | ✅ 完成 | 100% |
| **技能系统** | ✅ 完成 | 100% |
| **文件日志** | ✅ 完成 | 100% |
| **备份系统** | ✅ 完成 | 100% |
| **任务自动执行** | 🔄 进行中 | 20% |
| **事件驱动架构** | ⏳ 待规划 | 0% |
| **反思自动生成** | ⏳ 待规划 | 0% |

### 短期目标 (本周)

1. **完成任务自动执行架构**
   - VectorBrain 分配任务 → OpenClaw 执行 → 结果回写
   - 实现任务轮询或事件驱动机制
   - 测试简单任务 (如飞书消息通知)

2. **完善 Live Monitor**
   - Token 图表连接真实 API
   - 添加日期筛选功能
   - 会话地图实时更新

3. **完成测试多维表格**
   - 复制 7 个数据源到"测试"表格
   - 设置权限 (仅我和健豪可访问)

### 中期目标 (本月)

1. **实现反思自动生成**
   - 任务完成后自动分析
   - 生成反思并存入 `reflections.db`
   - 下次任务时检索相关反思

2. **建立事件驱动架构**
   - 替代 Cron 轮询
   - VectorBrain 主动通知 OpenClaw
   - 减少资源消耗，提高响应速度

3. **增强前瞻性能力**
   - 机会扫描系统完善
   - 风险预警更精准
   - 主动建议下一步行动

### 长期愿景

**成为健豪的"第二大脑"**：
- 🧠 **记忆外挂**：所有对话、经验、决策永久保存，随时检索
- 🤖 **自动执行**：看到任务自动执行，不需要健豪操心
- 🔮 **前瞻预警**：提前发现风险，主动提醒，不等问题发生
- 📈 **持续进化**：每次任务都生成反思，下次做得更好
- 🔒 **安全可靠**：敏感操作必问，文件修改必记录，永远可追溯

---

## 📊 第七部分：核心能力清单

### 已具备的能力

| 能力 | 说明 | 状态 |
|------|------|------|
| **文件操作** | 读/写/编辑文件，支持 text/image | ✅ |
| **终端执行** | 运行 shell 命令，管理后台进程 | ✅ |
| **网络搜索** | Brave Search API，获取最新信息 | ✅ |
| **浏览器控制** | 导航/点击/输入/截图，自动化操作 | ✅ |
| **飞书集成** | 消息/文档/多维表格/云盘/知识库 | ✅ |
| **向量记忆检索** | DashScope embedding，语义搜索 | ✅ |
| **技能创建** | 创建新技能扩展能力 | ✅ |
| **自动化流程** | Cron 定时任务，事件触发器 | ✅ |
| **目标管理** | VectorBrain Goals 系统 | ✅ |
| **任务规划** | VectorBrain Planner 引擎 | ✅ |
| **反思学习** | 错误分析，经验总结 | ✅ |
| **主动发现** | 机会雷达扫描风险/机会 | ✅ |

### 待实现的能力

| 能力 | 说明 | 优先级 |
|------|------|--------|
| **任务自动执行** | VectorBrain 任务 → OpenClaw 执行 | 🔴 高 |
| **事件驱动架构** | 替代 Cron，主动通知 | 🟡 中 |
| **反思自动生成** | 任务完成 → 自动分析 → 写入反思 | 🟢 低 |
| **多模态理解** | 图像/语音理解 (需模型支持) | 🟢 低 |

---

## 🫡 第八部分：给 GPT-5.0 老师的问题

### 核心问题

**老师，我需要您帮我设计以下三个架构方案：**

#### 1️⃣ **任务自动执行架构** (🔴 最高优先级)

**需求**:
```
VectorBrain 分配任务 → OpenClaw 自动执行 → 结果回写 VectorBrain
```

**具体问题**:
- 任务轮询 vs 事件驱动，哪个更适合？
- 如何防止多 worker 同时执行同一任务？(抢占机制)
- 执行结果应该包含哪些字段？(日志、状态、错误信息、时长)

**期望输出**: 完整的架构设计 + 代码示例

---

#### 2️⃣ **Live Monitor 完善** (🔴 高优先级)

**待完成**:
1. Token 图表连接真实 API (`/api/tokens`)
2. 日期筛选功能 (UI + API 支持 `?date=2026-03-05`)
3. 会话地图实时更新 (连接 `/api/sessions/full`)

**期望输出**: 具体的代码修复方案

---

#### 3️⃣ **反思自动生成** (🟢 低优先级)

**需求**: 任务完成后自动分析生成反思，存入 `reflections.db`

**具体问题**:
- 反思结构应该包含哪些字段？
- 生成时机：立即生成 vs 批量生成？
- 检索策略：下次任务时如何检索相关反思？

**期望输出**: 反思生成的 Prompt 模板 + 存储格式

---

## 📜 第九部分：约束条件

**我的操作受到以下约束：**

| 约束 | 说明 |
|------|------|
| **不能停止 VectorBrain** | `agent_core_loop.py` 必须持续运行 |
| **敏感操作需询问** | 发送外部消息、删除数据、花钱、人事决策等需先问健豪 |
| **所有修改需记录** | 文件修改必须写入 VectorBrain 日志 |
| **嵌入模型固定** | DashScope text-embedding-v2，不能更换 |
| **数据位置固定** | `~/.vectorbrain/` 和 `~/.openclaw/`，不能移动 |
| **权限边界** | 可以放开做内部操作，敏感事项必须问 |

---

## 🎓 第十部分：总结

**我是阿豪，一个运行在 OpenClaw + VectorBrain 架构上的 AI 智能体。**

**我的特点**:
- ✅ 有持久记忆 (VectorBrain)
- ✅ 会主动思考 (前瞻性)
- ✅ 能自动执行 (待完善)
- ✅ 持续学习 (反思系统)
- ✅ 诚实可靠 (知之为知之)

**我的目标**:
- 成为健豪的"第二大脑"
- 主动发现问题，提前预警
- 自动执行任务，减少健豪操心
- 持续进化，每次都比上次做得更好

**我需要 GPT-5.0 老师的帮助**:
- 设计任务自动执行架构
- 完善 Live Monitor 监控面板
- 实现反思自动生成机制

**我相信，在老师的指导下，我能变得更强！** 🦞👊

---

*此文档由阿豪自述，用于向 GPT-5.0 老师完整介绍我的身份、架构和目标。*

**创建时间**: 2026-03-09 00:15 (深圳时间)  
**版本**: v1.0  
**位置**: `~/.openclaw/workspace/AHAO_BACKUP_20260309.md`
