# 抽烟提醒设置

**创建时间**: 2026-03-03 09:37
**设置者**: 王健豪

## 提醒规则

- **频率**: 工作日，从 9:00 开始，每隔 45 分钟
- **午休时间**: 12:00-13:30 不发送
- **结束时间**: 18:00 后不发送

## 具体提醒时间点

**上午**:
- 09:00
- 09:45
- 10:30
- 11:15

**下午**:
- 13:30
- 14:15
- 15:00
- 15:45
- 16:30
- 17:15

## 消息内容

"💨 抽烟时间到了，记得多喝水"

## 执行方式

✅ **已迁移到 OpenClaw 内置 cron** (2026-03-03 10:00)

使用 OpenClaw Gateway 内置 cron 调度器，和 weekday-lunch-reminder 同样的架构。

**系统 crontab 版本已删除**，现在全部使用 OpenClaw 内置 cron。

## Cron 配置

```bash
# OpenClaw 内置 cron (用 openclaw cron list 查看)
# 工作日抽烟提醒 (周一到周五)
smoking-09-00   # 09:00
smoking-09-45   # 09:45
smoking-10-30   # 10:30
smoking-11-15   # 11:15
smoking-13-30   # 13:30 (午休后)
smoking-14-15   # 14:15
smoking-15-00   # 15:00
smoking-15-45   # 15:45
smoking-16-30   # 16:30
smoking-17-15   # 17:15
```

**验证命令**:
```bash
openclaw cron list          # 查看所有任务
openclaw cron run <ID>      # 手动运行测试
openclaw cron runs          # 查看运行历史
```
