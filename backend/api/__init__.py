"""API 模块"""
from .metrics import router as metrics_router
from .websocket import router as websocket_router
from .config import router as config_router

__all__ = ["metrics_router", "websocket_router", "config_router"]
