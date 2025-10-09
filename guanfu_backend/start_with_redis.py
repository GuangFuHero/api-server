#!/usr/bin/env python3
"""
啟動腳本，包含 Redis 連接檢查和應用程式啟動
"""

import asyncio
import logging
import sys
from src.pubsub import pubsub_service
from src.background_processor import log_processor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def check_redis_connection():
    """檢查 Redis 連接是否正常"""
    try:
        await pubsub_service.connect()
        if pubsub_service.is_connected:
            logger.info("✅ Redis 連接成功")
            await pubsub_service.disconnect()
            return True
        else:
            logger.error("❌ Redis 連接失敗")
            return False
    except Exception as e:
        logger.error(f"❌ Redis 連接錯誤: {e}")
        return False


async def main():
    """主函數"""
    logger.info("🚀 啟動光復主站 API 服務...")
    
    # 檢查 Redis 連接
    logger.info("🔍 檢查 Redis 連接...")
    if not await check_redis_connection():
        logger.error("❌ Redis 服務不可用，請確保 Redis 正在運行")
        logger.info("💡 提示: 執行 'docker-compose up -d redis' 啟動 Redis")
        sys.exit(1)
    
    logger.info("✅ 所有服務檢查完成，可以啟動應用程式")
    logger.info("💡 執行 'uvicorn src.main:app --reload' 啟動 API 服務")


if __name__ == "__main__":
    asyncio.run(main())
