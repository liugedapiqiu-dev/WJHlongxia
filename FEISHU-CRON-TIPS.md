# 飞书定时任务主动推送消息配置指南

**问题**：OpenClaw 定时任务的 `announce` 模式有 bug，显示 "delivered" 但飞书实际收不到消息。

**解决方案**：让 AI 直接用 `message` 工具发送，而不是依赖系统的 `announce` 模式。

---

## ✅ 正确配置方式

### 1. Prompt 写法

在 `Assistant task prompt` 里明确告诉 AI 用 `message` 工具：

```
请用 message 工具发送飞书消息给健豪（user:ou_xxx），提醒他xxx。

消息内容：xxx

使用 message 工具的：
- action=send
- channel=feishu
- target="user:ou_xxx"
```

### 2. Result delivery 设置

**必须选**：`None (internal)`

**不要选**：`Announce summary (default)` ← 这个有 bug！

---

## 📋 配置检查清单

创建飞书定时任务时检查：

- [ ] Prompt 里告诉 AI 用 `message` 工具
- [ ] Prompt 里指定正确的 `user_id` (格式：`user:ou_xxx`)
- [ ] `Result delivery` 选 `None (internal)`
- [ ] `Channel` 和 `To` 字段可以留空（因为 AI 会自己处理）

---

## 🐛 问题原因

OpenClaw 的 `announce` 模式在飞书通道上有 bug：
- 定时任务执行成功
- 系统显示 "delivered"
- 但飞书插件实际没收到发送请求
- 日志里也看不到发送记录

**绕过方法**：让 AI 在 prompt 里直接调用 `message` 工具，`Result delivery` 设为 `None`。

---

*最后更新：2026-03-02*
*问题发现者：健豪*
