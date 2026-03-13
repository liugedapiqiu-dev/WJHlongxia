import sqlite3
import json
import time
import subprocess
import os

# 设置 PATH 环境变量（cron 环境中需要）
os.environ["PATH"] = "/usr/local/bin:/opt/homebrew/bin:/Users/jo/.npm-global/bin:" + os.environ.get("PATH", "")


# 配置区
DB_PATH = os.path.expanduser("~/.vectorbrain/opportunity/opportunities.db")
# 使用 openclaw message 工具发送飞书消息
FEISHU_NOTIFY_CMD = '''/Users/jo/.npm-global/bin/openclaw message send --channel feishu --message "{msg}"'''

def get_pending_opportunities():
    """获取所有高优先级的待处理机会/风险"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # 严格筛选：状态为待处理，且严重程度为高
        cursor.execute("""
        SELECT opportunity_id, type, title, description, suggested_action 
        FROM opportunities 
        WHERE status = 'pending' AND severity = 'high'
        ORDER BY detected_at DESC LIMIT 5
        """)
        results = cursor.fetchall()
        conn.close()
        return results
    except Exception as e:
        print(f"❌ 读取数据库失败：{e}")
        return []

def mark_as_notified(opp_id):
    """将机会状态更新为已通知，防止重复轰炸"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # 将 status 从 pending 改为 notified
        cursor.execute("UPDATE opportunities SET status = 'notified' WHERE opportunity_id = ?", (opp_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ 更新状态失败：{e}")
        return False

def send_feishu_alert(title, description, suggested_action):
    """发送飞书消息警报"""
    # 构造更友好的文案
    msg_content = f"🚨 发现系统风险/机会\n\n📌 标题：{title}\n📄 描述：{description}\n💡 建议：{suggested_action}"
    
    # 写入通知日志文件（供其他系统读取发送）
    log_file = os.path.expanduser("~/.vectorbrain/state/pending_notifications.json")
    try:
        # 读取现有通知队列
        notifications_data = None
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                notifications_data = json.load(f)
        
        # 兼容旧格式：如果是列表，转换为字典格式
        if isinstance(notifications_data, list):
            old_list = notifications_data
            notifications_data = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "count": len(old_list),
                "opportunities": [],
                "message": "历史通知",
                "status": "pending",
                "notifications": old_list
            }
        elif notifications_data is None:
            notifications_data = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "count": 0,
                "opportunities": [],
                "message": "",
                "status": "pending",
                "notifications": []
            }
        
        # 确保 notifications 字段存在且是列表
        if "notifications" not in notifications_data:
            notifications_data["notifications"] = []
        elif not isinstance(notifications_data["notifications"], list):
            notifications_data["notifications"] = []
        
        # 添加新通知
        notifications_data["notifications"].append({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "type": "risk_alert",
            "title": title,
            "description": description,
            "suggested_action": suggested_action,
            "message": msg_content
        })
        
        # 更新计数
        notifications_data["count"] = len(notifications_data["notifications"])
        notifications_data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # 写回文件
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(notifications_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 通知已写入日志：{log_file}")
        
        # 同时发送飞书消息（带 Target ID）
        FEISHU_TARGET = "user:ou_cd2f520717fd4035c6ef3db89a53b748"
        safe_msg = msg_content.replace('"', '\\"').replace('\n', '\\n')
        feishu_cmd = f'/Users/jo/.npm-global/bin/openclaw message send --channel feishu -t "{FEISHU_TARGET}" -m "{safe_msg}"'
        
        try:
            result = subprocess.run(feishu_cmd, shell=True, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print(f"✅ 飞书消息已发送")
            else:
                print(f"⚠️ 飞书发送返回警告：{result.stderr[:200] if result.stderr else 'N/A'}")
        except Exception as e:
            print(f"⚠️ 飞书发送异常（通知仍已记录到日志）: {e}")
        
        return True
    except Exception as e:
        print(f"❌ 写入日志失败：{e}")
        import traceback
        traceback.print_exc()
        return False

def radar_sweep():
    print("📡 [雷达扫描] 开始检测高优未处理机会...")
    opportunities = get_pending_opportunities()
    
    if not opportunities:
        print("✅ 当前无高危警报。")
        return

    print(f"⚠️ 发现 {len(opportunities)} 个高危事项，准备通知指挥官！")
    
    for opp in opportunities:
        opp_id, opp_type, title, desc, action = opp
        
        # 1. 发送飞书
        success = send_feishu_alert(title, desc, action)
        
        # 2. 如果发送成功，立刻更新数据库状态闭环
        if success:
            mark_as_notified(opp_id)
            print(f"🔔 已通知并标记：{opp_id} ({title})")
        else:
            print(f"⛔ 通知失败，保留 pending 状态：{opp_id}")
        
        # 防止频率过高触发飞书流控
        time.sleep(1)

if __name__ == "__main__":
    radar_sweep()
