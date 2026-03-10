# 技能配置完整性检查报告

**检查时间:** 2026-03-10T14:56:28.299594
**技能总数:** 11
**完整配置率:** 81.8%

---

## ✅ 配置完整的技能 (9)

- agent-browser
- office-automation-skill
- vectorbrain-connector
- self-improvement
- startup-healthcheck
- desktop-control
- vectorbrain-memory-search
- gupiaozhushou
- tavily

---

## ⚠️ 配置缺失的技能

### 缺少 skill.json (0)

无

### 缺少 SKILL.md (1)

- brain-health-monitor

### 两者都缺失 (0)

无

---

## 🚫 已禁用的技能 (1)

- local-brain.disabled

---

## 🔧 建议操作

### 自动修复命令

```bash
# 为缺失配置的技能创建模板
python3 ~/.openclaw/skills/auto_skill_fixer.py
```

### 手动修复

1. 为缺少 skill.json 的技能创建配置文件
2. 为缺少 SKILL.md 的技能创建文档
3. 考虑移除或启用已禁用的技能
