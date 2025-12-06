"""
WebSocket Manager for real-time notifications
Handles broadcasting motion alerts to all connected clients
"""

from fastapi import WebSocket
from typing import Dict, Set
from datetime import datetime
import json
import asyncio


class WebSocketManager:
    """Manages WebSocket connections and broadcasts alerts"""
    
    def __init__(self):
        # Store active connections: {user_id: set of websockets}
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # All connections for broadcast
        self.all_connections: Set[WebSocket] = set()
        # Lock for thread-safe operations
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        async with self._lock:
            # Add to all connections
            self.all_connections.add(websocket)
            
            # Add to user-specific connections
            if user_id not in self.active_connections:
                self.active_connections[user_id] = set()
            self.active_connections[user_id].add(websocket)
        
        print(f"🔌 WebSocket connected: user_id={user_id} (total: {len(self.all_connections)})")
    
    async def disconnect(self, websocket: WebSocket, user_id: int):
        """Remove a WebSocket connection"""
        async with self._lock:
            # Remove from all connections
            self.all_connections.discard(websocket)
            
            # Remove from user-specific connections
            if user_id in self.active_connections:
                self.active_connections[user_id].discard(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
        
        print(f"🔌 WebSocket disconnected: user_id={user_id} (total: {len(self.all_connections)})")
    
    async def broadcast(self, message: dict):
        """Broadcast message to ALL connected clients"""
        if not self.all_connections:
            print("⚠️ No WebSocket clients connected, alert not sent")
            return
        
        message_json = json.dumps(message)
        disconnected = set()
        
        for connection in self.all_connections.copy():
            try:
                await connection.send_text(message_json)
            except Exception as e:
                print(f"⚠️ WebSocket send failed: {e}")
                disconnected.add(connection)
        
        # Clean up dead connections
        if disconnected:
            async with self._lock:
                self.all_connections -= disconnected
    
    async def send_to_user(self, user_id: int, message: dict):
        """Send message to a specific user's connections"""
        if user_id not in self.active_connections:
            return
        
        message_json = json.dumps(message)
        disconnected = set()
        
        for connection in self.active_connections[user_id].copy():
            try:
                await connection.send_text(message_json)
            except Exception:
                disconnected.add(connection)
        
        # Clean up dead connections
        if disconnected:
            async with self._lock:
                self.active_connections[user_id] -= disconnected
    
    async def send_motion_alert(self):
        """Send motion detection alert to all clients"""
        alert = {
            "type": "motion_alert",
            "title": "🚨 Intruder Detected!",
            "message": "Motion sensor triggered. Would you like to view the camera?",
            "timestamp": datetime.now().isoformat(),
            "camera_available": True
        }
        await self.broadcast(alert)
        print(f"📢 Motion alert broadcast to {len(self.all_connections)} client(s)")
    
    async def send_motion_cleared(self):
        """Send motion cleared notification"""
        alert = {
            "type": "motion_cleared",
            "title": "✅ All Clear",
            "message": "No motion detected",
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast(alert)
    
    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.all_connections)


# Global WebSocket manager instance
ws_manager = WebSocketManager()
