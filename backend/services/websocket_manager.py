import asyncio
import json
import logging
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections for real-time streaming updates"""
    
    def __init__(self):
        # Dictionary to store active connections by processing_id
        self.active_connections: Dict[str, WebSocket] = {}
        # Set to track which processing_ids have active connections
        self.active_processing_ids: Set[str] = set()
    
    async def connect(self, websocket: WebSocket, processing_id: str):
        """Accept a WebSocket connection and store it"""
        await websocket.accept()
        self.active_connections[processing_id] = websocket
        self.active_processing_ids.add(processing_id)
        logger.info(f"WebSocket connected for processing_id: {processing_id}")
    
    def disconnect(self, processing_id: str):
        """Remove a WebSocket connection"""
        if processing_id in self.active_connections:
            del self.active_connections[processing_id]
        self.active_processing_ids.discard(processing_id)
        logger.info(f"WebSocket disconnected for processing_id: {processing_id}")
    
    async def send_progress_update(self, processing_id: str, data: dict):
        """Send progress update to a specific client"""
        if processing_id in self.active_connections:
            try:
                websocket = self.active_connections[processing_id]
                await websocket.send_text(json.dumps(data))
                print(f"✅ WebSocket message sent to {processing_id}: {data.get('type', 'unknown')}")
                logger.debug(f"Sent progress update to {processing_id}: {data.get('type', 'unknown')}")
            except Exception as e:
                print(f"❌ WebSocket send error to {processing_id}: {e}")
                logger.error(f"Error sending WebSocket message to {processing_id}: {e}")
                # Remove the connection if it's broken
                self.disconnect(processing_id)
        else:
            print(f"⚠️ No WebSocket connection found for {processing_id}")
    
    async def send_line_completed(self, processing_id: str, line_number: int, issues: list, progress: int, processed_lines: int, total_lines: int, total_issues: int, skipped_sentences: int):
        """Send line completion update"""
        data = {
            'type': 'line_completed',
            'line_number': line_number,
            'issues': [issue.dict() for issue in issues],
            'progress': progress,
            'processed_lines': processed_lines,
            'total_lines': total_lines,
            'total_issues': total_issues,
            'skipped_sentences': skipped_sentences,
            'timestamp': asyncio.get_event_loop().time()
        }
        await self.send_progress_update(processing_id, data)
    
    async def send_processing_complete(self, processing_id: str, total_issues: int, processed_lines: int, skipped_sentences: int):
        """Send processing completion update"""
        data = {
            'type': 'processing_complete',
            'total_issues': total_issues,
            'processed_lines': processed_lines,
            'skipped_sentences': skipped_sentences,
            'progress': 100,
            'timestamp': asyncio.get_event_loop().time()
        }
        await self.send_progress_update(processing_id, data)
    
    async def send_error(self, processing_id: str, error_message: str):
        """Send error update"""
        data = {
            'type': 'error',
            'error': error_message,
            'timestamp': asyncio.get_event_loop().time()
        }
        await self.send_progress_update(processing_id, data)
    
    async def send_status_update(self, processing_id: str, status: str, message: str, progress: int = None):
        """Send general status update"""
        data = {
            'type': 'status_update',
            'status': status,
            'message': message,
            'progress': progress,
            'timestamp': asyncio.get_event_loop().time()
        }
        await self.send_progress_update(processing_id, data)
    
    def has_connection(self, processing_id: str) -> bool:
        """Check if there's an active connection for a processing_id"""
        return processing_id in self.active_connections
    
    def get_connection_count(self) -> int:
        """Get the number of active connections"""
        return len(self.active_connections)

# Global WebSocket manager instance
websocket_manager = WebSocketManager()
