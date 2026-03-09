"""
WebSocket 实时推送
"""
import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Dict, Set
import time

from monitor import collector

router = APIRouter()


class ConnectionManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        # 活跃连接: {client_id: websocket}
        self.active_connections: Dict[str, WebSocket] = {}
        # 订阅信息: {client_id: {metrics: [...], interval: int}}
        self.subscriptions: Dict[str, Dict] = {}
        # 心跳任务
        self._heartbeat_task = None
    
    async def connect(self, client_id: str, websocket: WebSocket):
        """接受新的 WebSocket 连接"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.subscriptions[client_id] = {
            "metrics": ["cpu", "memory", "disk", "network"],
            "interval": 1
        }
        print(f"WebSocket 连接: {client_id}, 当前连接数: {len(self.active_connections)}")
    
    def disconnect(self, client_id: str):
        """断开连接"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.subscriptions:
            del self.subscriptions[client_id]
        print(f"WebSocket 断开: {client_id}, 当前连接数: {len(self.active_connections)}")
    
    async def send_data(self, client_id: str, data: dict):
        """发送数据到指定客户端"""
        if client_id in self.active_connections:
            try:
                websocket = self.active_connections[client_id]
                await websocket.send_json(data)
            except Exception as e:
                print(f"发送数据失败: {e}")
                self.disconnect(client_id)
    
    async def broadcast(self, data: dict):
        """广播数据到所有客户端"""
        for client_id in list(self.active_connections.keys()):
            await self.send_data(client_id, data)
    
    async def send_ping(self):
        """定时发送 ping 保持连接"""
        while True:
            try:
                for client_id in list(self.active_connections.keys()):
                    if client_id in self.active_connections:
                        try:
                            await self.active_connections[client_id].send_json({
                                "type": "ping",
                                "timestamp": int(time.time() * 1000)
                            })
                        except:
                            self.disconnect(client_id)
            except:
                pass
            await asyncio.sleep(30)  # 每 30 秒发送一次 ping


# 全局连接管理器
manager = ConnectionManager()


# 启动心跳任务
async def start_heartbeat():
    """启动心跳任务"""
    asyncio.create_task(manager.send_ping())


@router.websocket("/ws/metrics")
async def websocket_metrics(websocket: WebSocket, client_id: str = Query(default=None)):
    """
    WebSocket 端点：/ws/metrics
    
    客户端连接时可指定 client_id 参数
    
    消息格式:
    - 客户端发送 (订阅):
      {"action": "subscribe", "metrics": ["cpu", "memory"], "interval": 1}
    - 客户端发送 (心跳):
      {"action": "ping"}
    - 客户端发送 (取消订阅):
      {"action": "unsubscribe"}
    - 服务端推送:
      {"type": "data", "cpu": {...}, "memory": {...}, ...}
    - 服务端心跳:
      {"type": "ping", "timestamp": ...}
    """
    # 生成客户端 ID
    if not client_id:
        client_id = f"client_{int(time.time() * 1000)}"
    
    await manager.connect(client_id, websocket)
    
    # 启动心跳任务（如果还没启动）
    if not hasattr(websocket.app.state, '_heartbeat_started'):
        asyncio.create_task(manager.send_ping())
        websocket.app.state._heartbeat_started = True
    
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                action = message.get("action")
                
                if action == "subscribe":
                    # 订阅/更新订阅
                    metrics = message.get("metrics", ["cpu", "memory", "disk", "network"])
                    interval = message.get("interval", 1)
                    manager.subscriptions[client_id] = {
                        "metrics": metrics,
                        "interval": interval
                    }
                    await websocket.send_json({
                        "type": "subscribed",
                        "metrics": metrics,
                        "interval": interval
                    })
                
                elif action == "unsubscribe":
                    # 取消订阅
                    manager.subscriptions[client_id] = {
                        "metrics": [],
                        "interval": 1
                    }
                    await websocket.send_json({
                        "type": "unsubscribed"
                    })
                
                elif action == "ping" or action == "pong":
                    # 心跳响应
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": int(time.time() * 1000)
                    })
                
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "invalid JSON"
                })
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        print(f"WebSocket 错误: {e}")
        manager.disconnect(client_id)
