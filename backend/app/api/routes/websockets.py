import json
import logging
from typing import Dict, List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)
router = APIRouter()

class ConnectionManager:
    def __init__(self):
        # Maps document_id to a list of active websocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, document_id: str):
        await websocket.accept()
        if document_id not in self.active_connections:
            self.active_connections[document_id] = []
        self.active_connections[document_id].append(websocket)
        logger.info(f"WebSocket connected for document {document_id}")

    def disconnect(self, websocket: WebSocket, document_id: str):
        if document_id in self.active_connections:
            self.active_connections[document_id].remove(websocket)
            if not self.active_connections[document_id]:
                del self.active_connections[document_id]
        logger.info(f"WebSocket disconnected for document {document_id}")

    async def broadcast_to_document(self, document_id: str, message: dict):
        if document_id in self.active_connections:
            # We must await each send separately, but asyncio.gather is better
            # For simplicity, sequential works fine here unless huge amount of clients
            disconnected = []
            for connection in self.active_connections[document_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error sending message to client: {e}")
                    disconnected.append(connection)
            
            for d in disconnected:
                self.disconnect(d, document_id)


manager = ConnectionManager()

@router.websocket("/ws/{document_id}")
async def websocket_endpoint(websocket: WebSocket, document_id: str):
    await manager.connect(websocket, document_id)
    try:
        while True:
            # We simply keep the connection open.
            # Client can ping, but typically they just receive updates.
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, document_id)
