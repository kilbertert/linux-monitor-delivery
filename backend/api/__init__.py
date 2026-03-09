"""API 模块"""
from .metrics import router as metrics_router
from .websocket import router as websocket_router
from .config import router as config_router
from .alerts import router as alerts_router
from .processes import router as processes_router
from .export import router as export_router

__all__ = [
    "metrics_router",
    "websocket_router",
    "config_router",
    "alerts_router",
    "processes_router",
    "export_router"
]
