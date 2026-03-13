#!/usr/bin/env python3
"""
🛡️ 阿豪智能模型路由代理 (Ahao Smart Proxy)
实现无缝断网降级：云端超时自动切换本地 Ollama
"""

import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
import uvicorn

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - 🛡️ SmartProxy - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Ahao Smart Proxy")

# --- 配置区 ---
# 云端 API 配置
CLOUD_API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
CLOUD_MODEL = "qwen3.5-plus"

# 本地 Ollama 配置
LOCAL_API_URL = "http://127.0.0.1:11434/v1/chat/completions"
LOCAL_MODEL = "qwen2.5:14b"

# 断路器超时设置
CLOUD_TIMEOUT = 3.0      # 云端 3 秒无响应即判定断网/超时
LOCAL_TIMEOUT = 120.0    # 本地推理给予充分时间


@app.post("/v1/chat/completions")
async def proxy_chat(request: Request):
    """
    代理聊天请求
    优先使用云端，超时自动降级到本地
    """
    try:
        # 获取请求数据
        payload = await request.json()
        auth_header = request.headers.get("Authorization", "")
        
        # ========== 1. 尝试请求云端模型 ==========
        cloud_payload = payload.copy()
        cloud_payload["model"] = CLOUD_MODEL
        headers = {
            "Authorization": auth_header,
            "Content-Type": "application/json"
        }
        
        try:
            logger.info(f"🌐 尝试连接云端 [{CLOUD_MODEL}]...")
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    CLOUD_API_URL,
                    json=cloud_payload,
                    headers=headers,
                    timeout=CLOUD_TIMEOUT
                )
                response.raise_for_status()
                logger.info("✅ 云端请求成功！")
                return JSONResponse(
                    content=response.json(),
                    status_code=response.status_code
                )
        
        except (httpx.TimeoutException, httpx.ConnectError) as e:
            logger.warning(f"⚠️ 云端无响应 (超时/断网): {e}。触发降级机制...")
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ 云端返回错误状态码：{e.response.status_code}。触发降级机制...")
        
        # ========== 2. 断路器打开，降级到本地 Ollama ==========
        local_payload = payload.copy()
        local_payload["model"] = LOCAL_MODEL
        
        try:
            logger.info(f"🏠 启动本地备用模型 [{LOCAL_MODEL}]...")
            async with httpx.AsyncClient() as client:
                # Ollama 本地调用通常不需要强校验 Auth
                response = await client.post(
                    LOCAL_API_URL,
                    json=local_payload,
                    timeout=LOCAL_TIMEOUT
                )
                response.raise_for_status()
                logger.info("✅ 本地模型接管成功！")
                return JSONResponse(
                    content=response.json(),
                    status_code=response.status_code
                )
        
        except Exception as e:
            logger.critical(f"🚨 本地模型也失败了：{e}")
            raise HTTPException(
                status_code=500,
                detail="Fatal: Both Cloud and Local models failed."
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"🚨 未知错误：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "Ahao Smart Proxy",
        "cloud_model": CLOUD_MODEL,
        "local_model": LOCAL_MODEL
    }


@app.get("/")
async def root():
    """根路径信息"""
    return {
        "service": "Ahao Smart Proxy",
        "version": "1.0.0",
        "description": "智能模型路由代理 - 云端超时自动降级本地",
        "endpoints": {
            "chat": "POST /v1/chat/completions",
            "health": "GET /health"
        }
    }


if __name__ == "__main__":
    # 监听本地 8000 端口
    logger.info("=" * 60)
    logger.info("🛡️ 阿豪智能模型路由代理启动")
    logger.info("=" * 60)
    logger.info(f"🌐 监听地址：http://127.0.0.1:8000")
    logger.info(f"☁️ 云端模型：{CLOUD_MODEL}")
    logger.info(f"🏠 本地模型：{LOCAL_MODEL}")
    logger.info(f"⏱️ 超时阈值：{CLOUD_TIMEOUT}秒")
    logger.info("=" * 60)
    logger.info("🚀 启动中...")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )
