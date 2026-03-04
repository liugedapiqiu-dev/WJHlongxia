# OpenClaw Cron 定时任务配置要点

**创建时间**: 2026-03-03 12:05  
**创建者**: 王健豪  
**重要性**: ⭐⭐⭐⭐⭐

---

## 🎯 核心知识点

**定时任务的关键点不在于其他设定，就关键在于助手任务提示词（prompt）！**

**重要规则**：以后健豪定制定时任务时，**一定要在 prompt 里加入这句话**：
```
请用 message 工具发送飞书消息给健豪（user:ou_cd2f520717fd4035c6ef3db89a53b748）：
```

---

## ✅ 正确的 Prompt 格式

```
请用 message 工具发送飞书消息给健豪（user:ou_cd2f520717fd4035c6ef3db89a53b748）：
[消息内容]
使用 message 工具的 action=send，channel=feishu，target="user:ou_cd2f520717fd4035c6ef3db89a53b748"
```

**关键要素**：
1. **明确指示**：直接告诉 agent 用 message 工具
2. **指定目标**：明确写出 user ID
3. **指定渠道**：明确写出 channel=feishu
4. **指定动作**：明确写出 action=send

---

## ❌ 错误的做法

1. **加条件判断**：让 agent 自己判断时间 → agent 会困惑
2. **依赖 delivery 配置**：期望系统自动发送 → 不可靠
3. **模糊的 prompt**：如"发送提醒" → agent 不知道用什么工具

---

## 📋 完整配置示例

```bash
openclaw cron add \
  --name "任务名称" \
  --cron "30 13 * * 1-5" \
  --tz "Asia/Shanghai" \
  --message "请用 message 工具发送飞书消息给健豪（user:ou_cd2f520717fd4035c6ef3db89a53b748）：
消息内容
使用 message 工具的 action=send，channel=feishu，target=\"user:ou_cd2f520717fd4035c6ef3db89a53b748\"" \
  --description "任务描述"
```

---

## 💡 成功关键

- **prompt 要明确直接**：让 agent 一眼就知道要做什么
- **不要加复杂逻辑**：条件判断会让 agent 困惑
- **参考成功案例**：午饭提醒是成功范例

---

*最后更新：2026-03-03 12:05*
