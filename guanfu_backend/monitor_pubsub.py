#!/usr/bin/env python3
"""
監控 PubSub 狀態的腳本
"""

import asyncio
import json
import logging
import redis.asyncio as redis
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def monitor_pubsub():
    """監控 PubSub 狀態"""
    try:
        # 連接 Redis
        redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        await redis_client.ping()
        logger.info("✅ 成功連接到 Redis")
        
        # 訂閱 request_logs 頻道
        pubsub = redis_client.pubsub()
        await pubsub.subscribe('request_logs')
        
        logger.info("📡 開始監控 request_logs 頻道...")
        logger.info("💡 發送一些 HTTP 請求到 API 來查看日誌")
        
        message_count = 0
        
        async for message in pubsub.listen():
            if message['type'] == 'message':
                message_count += 1
                try:
                    log_data = json.loads(message['data'])
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    logger.info(f"📨 [{timestamp}] 收到訊息 #{message_count}")
                    logger.info(f"   Method: {log_data.get('method')}")
                    logger.info(f"   Path: {log_data.get('path')}")
                    logger.info(f"   Status: {log_data.get('status_code')}")
                    logger.info(f"   Duration: {log_data.get('duration_ms')}ms")
                    logger.info("---")
                except json.JSONDecodeError as e:
                    logger.error(f"❌ 解析訊息失敗: {e}")
                except Exception as e:
                    logger.error(f"❌ 處理訊息時發生錯誤: {e}")
                    
    except Exception as e:
        logger.error(f"❌ 監控過程中發生錯誤: {e}")
    finally:
        if 'pubsub' in locals():
            await pubsub.close()
        if 'redis_client' in locals():
            await redis_client.close()


if __name__ == "__main__":
    print("🔍 PubSub 監控工具")
    print("按 Ctrl+C 停止監控")
    try:
        asyncio.run(monitor_pubsub())
    except KeyboardInterrupt:
        print("\n👋 監控已停止")
