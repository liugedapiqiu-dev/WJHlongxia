#!/usr/bin/env python3
"""
VectorBrain Gateway API Server
为 OpenClaw 提供常驻记忆存取服务
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import json
from datetime import datetime
import uvicorn
import os

app = FastAPI(title="VectorBrain Gateway")

# 确保数据库路径正确
VECBRAIN_HOME = os.path.expanduser("~/.vectorbrain")
EPISODIC_DB = f"{VECBRAIN_HOME}/memory/episodic_memory.db"
KNOWLEDGE_DB = f"{VECBRAIN_HOME}/memory/knowledge_memory.db"


class MemoryEvent(BaseModel):
    role: str
    content: str
    metadata: dict = {}


@app.post("/memory/save")
async def save_memory(event: MemoryEvent):
    """保存事件到情景记忆"""
    try:
        conn = sqlite3.connect(EPISODIC_DB)
        cursor = conn.cursor()
        timestamp = datetime.now().isoformat()
        
        # 插入事件记录
        cursor.execute("""
            INSERT INTO episodes (timestamp, worker_id, event_type, content, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (
            timestamp,
            "global_gateway",
            f"message_{event.role}",
            event.content,
            json.dumps(event.metadata, ensure_ascii=False)
        ))
        
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "msg": "记忆已写入海绵体",
            "timestamp": timestamp
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memory/load")
async def load_memory(limit: int = 5):
    """获取最近的记忆上下文"""
    try:
        conn = sqlite3.connect(EPISODIC_DB)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT event_type, content, metadata, timestamp
            FROM episodes
            WHERE worker_id = 'global_gateway'
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        context = [
            {
                "type": r[0],
                "content": r[1],
                "metadata": json.loads(r[2] if r[2] else "{}"),
                "timestamp": r[3]
            }
            for r in reversed(rows)
        ]
        
        return {
            "status": "success",
            "data": context
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "VectorBrain Gateway",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/")
async def root():
    """API 根路径"""
    return {
        "service": "VectorBrain Gateway",
        "version": "1.0.0",
        "endpoints": [
            "POST /memory/save",
            "GET /memory/load",
            "GET /health"
        ]
    }


if __name__ == "__main__":
    # 启动服务，监听 8999 端口
    print("=" * 60)
    print("🧠 VectorBrain Gateway API Server")
    print("=" * 60)
    print(f"  🌐 监听地址：http://127.0.0.1:8999")
    print(f"  📚 数据库：{EPISODIC_DB}")
    print(f"  🚀 启动中...")
    print("=" * 60)
    
    uvicorn.run(app, host="127.0.0.1", port=8999)
