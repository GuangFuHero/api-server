import asyncio
import json
import logging
from typing import Dict, Any, Optional
import redis.asyncio as redis
from .config import settings


class PubSubService:
    """PubSub service using Redis for asynchronous message processing."""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.channel_name = "request_logs"
        self.is_connected = False
    
    async def connect(self):
        """Connect to Redis."""
        try:
            # 使用預設的 Redis 連接設定，可以根據需要調整
            self.redis_client = redis.Redis(
                host='localhost',
                port=6379,
                db=0,
                decode_responses=True
            )
            await self.redis_client.ping()
            self.is_connected = True
            logging.info("Connected to Redis for pubsub")
        except Exception as e:
            logging.error(f"Failed to connect to Redis: {e}")
            self.is_connected = False
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
            self.is_connected = False
            logging.info("Disconnected from Redis")
    
    async def publish_request_log(self, log_data: Dict[str, Any]) -> bool:
        """
        Publish request log data to the pubsub channel.
        
        Args:
            log_data: Dictionary containing request log information
            
        Returns:
            bool: True if published successfully, False otherwise
        """
        if not self.is_connected or not self.redis_client:
            logging.error("Redis not connected, cannot publish message")
            return False
        
        try:
            # 序列化資料
            message = json.dumps(log_data, default=str)
            
            # 發送到 Redis pubsub channel
            await self.redis_client.publish(self.channel_name, message)
            logging.debug(f"Published request log to channel {self.channel_name}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to publish request log: {e}")
            return False
    
    async def subscribe_to_logs(self, callback):
        """
        Subscribe to request logs and process them with the provided callback.
        
        Args:
            callback: Async function to process received log data
        """
        if not self.is_connected or not self.redis_client:
            logging.error("Redis not connected, cannot subscribe")
            return
        
        try:
            pubsub = self.redis_client.pubsub()
            await pubsub.subscribe(self.channel_name)
            
            logging.info(f"Subscribed to channel {self.channel_name}")
            
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        # 反序列化資料
                        log_data = json.loads(message['data'])
                        await callback(log_data)
                    except Exception as e:
                        logging.error(f"Error processing message: {e}")
                        
        except Exception as e:
            logging.error(f"Failed to subscribe to logs: {e}")
        finally:
            if 'pubsub' in locals():
                await pubsub.close()


# 全域 pubsub 服務實例
pubsub_service = PubSubService()
