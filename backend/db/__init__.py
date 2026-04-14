"""数据库模块"""
from .database import (
    get_alert_history,
    get_connection,
    get_history_metrics,
    init_db,
    save_alert,
    save_alerts,
    save_metrics,
)

__all__ = [
    "init_db",
    "save_metrics",
    "get_history_metrics",
    "get_connection",
    "save_alert",
    "save_alerts",
    "get_alert_history",
]
