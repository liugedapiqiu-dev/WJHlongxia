# Live Monitor 完善任务 - 待继续

**创建时间**: 2026-03-05 23:28
**状态**: ⏳ 暂停，待下次继续
**优先级**: 高

---

## 📋 任务背景

完善 OpenClaw Live Monitor 监控面板，使其显示真实、准确、实时的系统数据。

---

## ✅ 已完成的功能

| 功能 | 状态 | 说明 |
|------|------|------|
| 系统健康评分 | ✅ 完成 | 从 `openclaw status` 解析，实时显示 100 分 |
| 网关状态 | ✅ 完成 | 在线/离线检测 |
| 飞书通道状态 | ✅ 完成 | 从日志解析 `feishu[default]: dispatch complete` |
| 错误数量 | ✅ 完成 | 实时统计 ERROR 日志数量 |
| 实时日志流 | ✅ 完成 | 中文转译，支持飞书消息解析 |
| 任务队列状态 | ✅ 完成 | 等待任务/累计任务/平均等待/活跃通道 |
| 最近会话 | ✅ 完成 | 显示最近会话列表 |
| 会话关系图 | ✅ 完成 | 显示会话关系节点 |
| 后端 API | ✅ 完成 | `/api/tokens` 和 `/api/sessions/full` 代码已写好 |

---

## ❌ 待完成的功能

### 1. Token 图表连接真实 API
**问题**: API 路径解析错误
- `__dirname` = `/Users/jo/.openclaw/workspace/skills/openclaw-live-monitor/src`
- 实际路径 = `/Users/jo/.openclaw/agents/main/sessions/sessions.json`
- 解析结果 = `/Users/jo/.openclaw/workspace/agents/main/sessions/sessions.json` ❌ 多了 `workspace`

**解决方案**:
```javascript
// 方案 A: 使用绝对路径（当前方案）
const sessionsFile = '/Users/jo/.openclaw/agents/main/sessions/sessions.json';

// 方案 B: 从环境变量读取
const sessionsFile = process.env.OPENCLAW_HOME + '/agents/main/sessions/sessions.json';

// 方案 C: 向上查找直到找到文件
function findSessionsFile() {
  let dir = __dirname;
  while (dir !== '/') {
    const testPath = path.join(dir, '../../agents/main/sessions/sessions.json');
    if (fs.existsSync(testPath)) return testPath;
    dir = path.dirname(dir);
  }
  return null;
}
```

**待修改位置**: `src/server.js` 第 437 行和第 468 行

---

### 2. 日期筛选功能
**需求**: 添加日期选择器，可以查看历史 token 消耗数据
**待实现**:
- 前端添加日期选择器 UI
- 后端 API 支持日期参数 `?date=2026-03-05`
- 数据持久化（LocalStorage 或 IndexedDB）

---

### 3. 会话地图实时更新
**问题**: 当前显示静态示例数据
**待实现**:
- 前端连接 `/api/sessions/full` API
- WebSocket 实时更新会话数据
- 会话卡片点击查看详情

---

## 📂 相关文件

| 文件 | 路径 | 状态 |
|------|------|------|
| 后端主文件 | `/Users/jo/.openclaw/workspace/skills/openclaw-live-monitor/src/server.js` | ✅ 已修改，待测试 |
| 前端主文件 | `/Users/jo/.openclaw/workspace/skills/openclaw-live-monitor/public/index.html` | ✅ 已修改 |
| 样式文件 | `/Users/jo/.openclaw/workspace/skills/openclaw-live-monitor/styles/main.css` | ⏳ 待修改 |
| 数据源 | `/Users/jo/.openclaw/agents/main/sessions/sessions.json` | ✅ 存在，有数据 |

---

## 🔑 关键代码片段

### Token API（待修复路径）
```javascript
app.get('/api/tokens', (req, res) => {
  try {
    const fs = require('fs');
    const sessionsFile = '/Users/jo/.openclaw/agents/main/sessions/sessions.json'; // 绝对路径
    const sessionsData = JSON.parse(fs.readFileSync(sessionsFile, 'utf-8'));
    
    const tokensBySession = Object.entries(sessionsData).map(([key, data]) => ({
      session: key.split(':').slice(-1)[0],
      input: data.inputTokens || 0,
      output: data.outputTokens || 0,
      total: data.totalTokens || 0,
      updatedAt: data.updatedAt || 0
    }));
    
    res.json({
      sessions: tokensBySession,
      summary: {
        input: tokensBySession.reduce((sum, s) => sum + s.input, 0),
        output: tokensBySession.reduce((sum, s) => sum + s.output, 0),
        total: tokensBySession.reduce((sum, s) => sum + s.total, 0)
      }
    });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});
```

---

## 🎯 下次继续的步骤

1. **修复 API 路径** - 用绝对路径替换 `path.resolve`
2. **重启服务测试** - `pkill -9 node && node src/server.js`
3. **验证 API 返回** - `curl http://localhost:18790/api/tokens`
4. **修改前端连接 API** - Token 图表和会话地图
5. **添加日期筛选** - UI 和 API 支持

---

## 💡 用户反馈

> "你还没有真正的完成"
> "Token 消耗应该接入 openclaw 的 token 消耗统计"
> "要有日期搜索的选择，而不是每次一刷新就刷新了"
> "会话地图这个窗口现在是加载的什么逻辑的，数据一直是固定住的"

---

## 📌 备注

- 用户准备升级技能包，等任务完成后进行
- 用户支持度很高，要有信心完成
- 这是展示能力的机会，要做成标杆项目

---

*最后更新：2026-03-05 23:28*
