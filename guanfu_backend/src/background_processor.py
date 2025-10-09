import asyncio
import logging
from typing import Dict, Any
from sqlalchemy.orm import Session
from . import database, models
from .pubsub import pubsub_service


class RequestLogProcessor:
    """Background processor for handling request logs from pubsub."""
    
    def __init__(self):
        self.is_running = False
        self.task = None
    
    async def start(self):
        """Start the background processor."""
        if self.is_running:
            logging.warning("Request log processor is already running")
            return
        
        self.is_running = True
        self.task = asyncio.create_task(self._process_logs())
        logging.info("Started request log background processor")
    
    async def stop(self):
        """Stop the background processor."""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logging.info("Stopped request log background processor")
    
    async def _process_logs(self):
        """Main processing loop for request logs."""
        await pubsub_service.connect()
        
        try:
            await pubsub_service.subscribe_to_logs(self._handle_log_message)
        except Exception as e:
            logging.error(f"Error in log processing loop: {e}")
        finally:
            await pubsub_service.disconnect()
    
    async def _handle_log_message(self, log_data: Dict[str, Any]):
        """
        Handle a single request log message from pubsub.
        
        Args:
            log_data: Dictionary containing request log information
        """
        try:
            # 建立資料庫 session
            db = database.SessionLocal()
            try:
                # 建立 RequestLog 物件
                request_log = models.RequestLog(
                    method=log_data.get('method'),
                    path=log_data.get('path'),
                    query=log_data.get('query'),
                    ip=log_data.get('ip'),
                    headers=log_data.get('headers'),
                    status_code=log_data.get('status_code'),
                    error=log_data.get('error'),
                    duration_ms=log_data.get('duration_ms'),
                    request_body=log_data.get('request_body'),
                    result_data=log_data.get('result_data'),
                    resource_id=log_data.get('resource_id')
                )
                
                # 儲存到資料庫
                db.add(request_log)
                db.commit()
                
                logging.debug(f"Processed request log for {log_data.get('method')} {log_data.get('path')}")
                
            except Exception as e:
                db.rollback()
                logging.error(f"Failed to save request log to database: {e}")
            finally:
                db.close()
                
        except Exception as e:
            logging.error(f"Error handling log message: {e}")


# 全域處理器實例
log_processor = RequestLogProcessor()
