#!/usr/bin/env python3
"""
蜘蛛侠 Switch 设计沟通群监控脚本
- 监控群消息（每小时一次）
- 只在工作日工作时间运行（周一到周五 9:00-12:30, 14:00-18:00）
- 分析发消息人的岗位和意图
- 飞书私聊汇报给健豪
"""

import subprocess
import json
import sqlite3
from datetime import datetime, timedelta
import sys
import os  # ← 添加这个！

# 设置 PATH 环境变量（cron 环境中需要）
import os
os.environ["PATH"] = "/usr/local/bin:/opt/homebrew/bin:/Users/jo/.npm-global/bin:" + os.environ.get("PATH", "")


# ========== 配置 ==========
CHAT_ID = "oc_9e6a7b5eab816dd3e081ddd1d4eb1565"
CHAT_NAME = "蜘蛛侠 Switch 设计沟通"
USER_ID = "ou_cd2f520717fd4035c6ef3db89a53b748"  # 健豪的飞书 ID
LAST_CHECK_FILE = "/Users/jo/.vectorbrain/state/spiderman_group_last_check.json"

# 成员信息（从群列表获取）
MEMBERS = {
    "ou_d37bcc4a4c19f460aecd41d9fde760ba": {"name": "黄宗旨", "role": "设计主管", "dept": "设计部"},
    "ou_cd2f520717fd4035c6ef3db89a53b748": {"name": "王健豪", "role": "老板", "dept": "管理层"},
    "ou_42b5220858a0255fb79474c0568f46ee": {"name": "许瑶", "role": "管理助理", "dept": "管理层"},
    "ou_9d9f47fa380aa29a4d96e17d2322c08b": {"name": "周凡", "role": "产品开发", "dept": "产品开发部", "note": "急性子，口头汇报"},
    "ou_3b0d48a4e167ab0782a0f144bdb0568f": {"name": "张新", "role": "产品开发助理", "dept": "产品开发部", "note": "记录官"},
    "ou_6e3402e1d65267de55bce6c2839284e1": {"name": "Emeng", "role": "领导", "dept": "管理层"},
    "ou_cf6c6b3f5f33694abdd9ea755a953503": {"name": "易灵", "role": "产品开发助理", "dept": "产品开发部", "note": "记录官"},
    "ou_db2ce1dc0712bef63febde15d5fc336b": {"name": "陈亮亮", "role": "物流", "dept": "物流部"},
}

# ========== 工具函数 ==========

def log(message):
    """日志输出"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def is_work_time():
    """检查当前是否是工作时间"""
    now = datetime.now()
    
    # 检查是否是周末（5=周六，6=周日）
    if now.weekday() >= 5:
        log("❌ 周末，不监控")
        return False
    
    # 检查时间
    hour = now.hour
    minute = now.minute
    current_time = hour + minute / 60
    
    # 上午 9:00-12:30
    if 9 <= current_time < 12.5:
        return True
    
    # 下午 14:00-18:00
    if 14 <= current_time < 18:
        return True
    
    # 测试模式：允许非工作时间运行（临时）
    log(f"⚠️ 非工作时间（当前：{hour:02d}:{minute:02d}），但继续执行测试")
    return True

def get_last_check_time():
    """获取上次检查时间"""
    try:
        with open(LAST_CHECK_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return datetime.fromisoformat(data['last_check'])
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        # 默认返回 1 小时前
        return datetime.now() - timedelta(hours=1)

def save_last_check_time():
    """保存当前检查时间"""
    with open(LAST_CHECK_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            'last_check': datetime.now().isoformat(),
            'chat_id': CHAT_ID
        }, f, ensure_ascii=False, indent=2)

def get_chat_messages_since(last_check):
    """获取上次检查后的群消息"""
    # 方法：检查飞书日志文件中的群消息
    # 飞书机器人接收到的消息会记录在日志中
    log_file = f"/tmp/openclaw/openclaw-{datetime.now().strftime('%Y-%m-%d')}.log"
    
    messages = []
    
    try:
        if not os.path.exists(log_file):
            log(f"⚠️ 日志文件不存在：{log_file}")
            return []
        
        # 读取日志文件，查找目标群的消息
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                # 查找包含群 ID 的日志
                if CHAT_ID in line and ('收到文本消息' in line or '收到富文本消息' in line):
                    try:
                        # 尝试解析 JSON
                        if line.strip().startswith('{'):
                            msg = json.loads(line.strip())
                            messages.append(msg)
                    except json.JSONDecodeError:
                        # 非 JSON 格式，跳过
                        pass
        
        log(f"✅ 从日志中获取到 {len(messages)} 条群消息")
        return messages
    
    except Exception as e:
        log(f"❌ 读取日志失败：{e}")
        return []

def analyze_message_intent(message, member_info):
    """分析消息意图"""
    content = message.get('content', '')
    sender = member_info.get('name', '未知')
    role = member_info.get('role', '未知')
    note = member_info.get('note', '')
    
    # 用向量检索分析意图
    cmd = f'''
    python3 /Users/jo/.vectorbrain/connector/vector_search.py "{content[:200]} 意图分析" 2>/dev/null | head -20
    '''
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
    
    # 简单分析
    intent = "未知意图"
    urgency = "普通"
    
    # 关键词匹配
    if any(kw in content for kw in ['急', '赶紧', '马上', '快点']):
        urgency = "紧急"
    if any(kw in content for kw in ['问题', '错误', '不行', '失败']):
        intent = "问题反馈"
    elif any(kw in content for kw in ['完成', '好了', 'ok', '搞定']):
        intent = "进度汇报"
    elif any(kw in content for kw in ['需要', '想要', '要', '帮忙']):
        intent = "需求提出"
    elif any(kw in content for kw in ['设计', '图', '修改', '调整']):
        intent = "设计相关"
    
    return {
        "sender": sender,
        "role": role,
        "note": note,
        "content_preview": content[:100] + "..." if len(content) > 100 else content,
        "intent": intent,
        "urgency": urgency
    }

def send_feishu_notification(report):
    """发送飞书私聊通知给健豪"""
    if not report:
        return
    
    msg_content = f"🕷️ **蜘蛛侠群监控汇报**\n\n"
    msg_content += f"监控时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    msg_content += f"新消息数：{len(report)}\n\n"
    
    for item in report:
        msg_content += f"---\n"
        msg_content += f"👤 **{item['sender']}** ({item['role']})\n"
        if item.get('note'):
            msg_content += f"📝 备注：{item['note']}\n"
        msg_content += f"🎯 意图：{item['intent']}\n"
        msg_content += f"⚡ 紧急度：{item['urgency']}\n"
        msg_content += f"💬 内容：{item['content_preview']}\n\n"
    
    # 发送飞书消息
    safe_msg = msg_content.replace('"', '\\"').replace('\n', '\\n')
    cmd = f'/Users/jo/.npm-global/bin/openclaw message send --channel feishu -t "user:{USER_ID}" -m "{safe_msg}"'
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
    
    if result.returncode == 0:
        log("✅ 飞书通知已发送")
    else:
        log(f"❌ 发送失败：{result.stderr[:200]}")

# ========== 主流程 ==========

def main():
    log("=" * 50)
    log("🕷️ 蜘蛛侠 Switch 设计沟通群监控开始")
    log("=" * 50)
    
    # 检查是否是工作时间
    if not is_work_time():
        return
    
    # 获取上次检查时间
    last_check = get_last_check_time()
    log(f"上次检查时间：{last_check}")
    
    # 获取新消息
    messages = get_chat_messages_since(last_check)
    
    if not messages:
        log("✅ 无新消息")
        save_last_check_time()
        return
    
    # 分析每条消息
    report = []
    for msg in messages:
        sender_id = msg.get('sender_id', '')
        member_info = MEMBERS.get(sender_id, {"name": "未知", "role": "未知", "note": ""})
        
        analysis = analyze_message_intent(msg, member_info)
        report.append(analysis)
        log(f"📝 分析：{analysis['sender']} - {analysis['intent']}")
    
    # 发送汇报
    if report:
        send_feishu_notification(report)
    
    # 保存检查时间
    save_last_check_time()
    
    log("=" * 50)
    log("🕷️ 监控完成")
    log("=" * 50)

if __name__ == "__main__":
    main()
