# 📦 GitHub 备份仓库配置

**更新时间：** 2026-03-11 23:22  
**记录位置：** `~/.vectorbrain/GITHUB_BACKUP_CONFIG.md`

---

## 🏠 仓库信息

**仓库地址：** `https://github.com/liugedapiqiu-dev/WJHlongxia`

**SSH 地址：** `git@github.com:liugedapiqiu-dev/WJHlongxia.git`

**仓库名称：** WJHlongxia（龙厦）

**所有者：** liugedapiqiu-dev（健豪）

---

## 🔧 Git 配置

### 远程仓库配置
```bash
# OpenClaw 工作区
cd ~/.openclaw/workspace
git remote set-url origin git@github.com:liugedapiqiu-dev/WJHlongxia.git
```

### SSH 密钥
- **密钥文件：** `~/.ssh/github_ahao`
- **公钥文件：** `~/.ssh/github_ahao.pub`
- **关联账户：** liugedapiqiu-dev

---

## 📊 备份内容

### OpenClaw 工作区备份
**路径：** `~/.openclaw/workspace/`

**包含：**
- ✅ 文档体系（docs/）
- ✅ 记忆文件（memory/）
- ✅ 技能配置（skills/）
- ✅ 配置文件（*.md, *.json）

### VectorBrain 备份
**路径：** `~/.vectorbrain/`

**包含：**
- ✅ Smart Proxy 代码和文档
- ✅ 连接器脚本
- ✅ 长期目标文档

---

## 🚀 备份命令

### 完整备份流程
```bash
# 1. 更新远程仓库
cd ~/.openclaw/workspace
git remote set-url origin git@github.com:liugedapiqiu-dev/WJHlongxia.git

# 2. 添加所有变更
git add docs/*.md memory/*.md *.md

# 3. 提交
git commit -m "📚 备份：$(date +%Y-%m-%d)"

# 4. 推送
GIT_SSH_COMMAND="ssh -i ~/.ssh/github_ahao -o IdentitiesOnly=yes" git push origin main
```

### 快速备份别名
```bash
# 添加到 ~/.zshrc
alias ahao-backup='cd ~/.openclaw/workspace && git add -A && git commit -m "📚 自动备份：$(date +%Y-%m-%d)" && GIT_SSH_COMMAND="ssh -i ~/.ssh/github_ahao -o IdentitiesOnly=yes" git push origin main'
```

---

## 📅 备份历史

| 日期 | 提交哈希 | 说明 |
|------|---------|------|
| 2026-03-11 | 待推送 | 📚 文档体系完善 + Smart Proxy 经验 |
| 2026-03-10 | c387aa6 | Phase 2&3 upgrade - 6 automation skills |
| 2026-03-10 | 61b230c | 🚀 第二阶段和第三阶段升级完成 |
| 2026-03-09 | 9155b72 | 🧠 记忆系统统一 + HEARTBEAT 重构 |

---

## ⚠️ 注意事项

1. **SSH 密钥权限：** 确保 `~/.ssh/github_ahao` 权限为 600
2. **全局配置：** 已删除 URL 重写配置（`url.https://github.com/.insteadof`）
3. **分支名称：** 使用 `phase2-upgrade` 分支推送

---

## 🔗 相关链接

- **GitHub 仓库：** https://github.com/liugedapiqiu-dev/WJHlongxia
- **SSH 测试：** `ssh -i ~/.ssh/github_ahao -T git@github.com`
- **OpenClaw 文档：** https://docs.openclaw.ai

---

**最后验证：** 2026-03-11 23:22  
**下次备份：** 每次重要更新后
