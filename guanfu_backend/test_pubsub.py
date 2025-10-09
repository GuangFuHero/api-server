#!/usr/bin/env python3
"""
Test script for pubsub functionality.
This script can be used to test the pubsub mechanism independently.
"""

import asyncio
import json
import logging
import os
from src.pubsub import pubsub_service
from src.background_processor import log_processor

# 設定本地資料庫連接（用於測試）
os.environ['DATABASE_URL'] = 'postgresql://guangfu_user:guangfu_dev_pass_2024@localhost:5432/guangfu'
os.environ['ENVIRONMENT'] = 'local'
os.environ['DB_USER'] = 'guangfu_user'
os.environ['DB_PASS'] = 'guangfu_dev_pass_2024'
os.environ['DB_NAME'] = 'guangfu'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_pubsub():
    """Test the pubsub functionality."""
    logger.info("Starting pubsub test...")
    
    # Start the background processor
    await log_processor.start()
    
    # Wait a moment for the processor to start
    await asyncio.sleep(2)
    
    # Test data
    test_log_data = {
        'method': 'GET',
        'path': '/test-endpoint',
        'query': 'param=value',
        'ip': '127.0.0.1',
        'headers': {'User-Agent': 'test-agent'},
        'status_code': 200,
        'error': None,
        'duration_ms': 150,
        'request_body': {'test': 'data'},
        'result_data': {'success': True},
        'resource_id': 'test-resource-123'
    }
    
    # Publish test message
    logger.info("Publishing test message...")
    success = await pubsub_service.publish_request_log(test_log_data)
    
    if success:
        logger.info("Message published successfully")
    else:
        logger.error("Failed to publish message")
    
    # Wait for processing
    await asyncio.sleep(3)
    
    # Stop the processor
    await log_processor.stop()
    logger.info("Test completed")


if __name__ == "__main__":
    asyncio.run(test_pubsub())
