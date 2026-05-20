"""
后台任务模块
定时采集并存储监控数据
"""
import asyncio
import os
import platform
from datetime import datetime

# 采集间隔（秒）
COLLECTION_INTERVAL = 5  # 每 5 秒存储一次

# 后台任务引用
_collection_task = None
_publish_task = None


def get_collector():
    """延迟导入避免循环依赖"""
    # WSL + Windows Agent 模式：优先使用 wsl_windows_client
    import os
    is_wsl = "microsoft" in platform.release().lower() if hasattr(platform, "release") else False
    use_agent = os.environ.get("USE_WINDOWS_AGENT", "true").lower() == "true"

    if is_wsl and use_agent:
        from monitor import wsl_windows_client as collector
        print(f"[Collector] WSL + Agent 模式: {collector.WINDOWS_AGENT_HOST}")
        return collector

    from monitor import collector
    return collector


def get_db():
    """延迟导入避免循环依赖"""
    from db import save_alerts, save_metrics
    return save_metrics, save_alerts


def get_alert_manager():
    """延迟导入避免循环依赖"""
    from alerts import alert_manager
    return alert_manager


def get_manager():
    """延迟导入避免循环依赖"""
    from api.websocket import manager
    return manager


async def collect_and_save():
    """采集并保存数据"""
    try:
        collector = get_collector()
        save_metrics, save_alerts = get_db()
        alert_manager = get_alert_manager()
        
        metrics = collector.get_all_metrics()
        save_metrics(metrics)
        alerts = alert_manager.check(metrics)
        save_alerts(alerts)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 数据已存储: CPU {metrics['cpu']['percent']}%")
    except Exception as e:
        print(f"数据采集/存储失败: {e}")


async def publish_metrics():
    """发布实时指标（供 WebSocket 使用）"""
    manager = get_manager()
    collector = get_collector()
    
    while True:
        try:
            metrics = collector.get_all_metrics()
            await manager.broadcast(metrics)
        except Exception as e:
            print(f"指标发布失败: {e}")
        await asyncio.sleep(1)


def start_background_tasks():
    """启动后台任务"""
    global _collection_task, _publish_task
    
    import asyncio
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    _collection_task = loop.create_task(_collection_loop())
    _publish_task = loop.create_task(publish_metrics())
    print("后台任务已启动")


def stop_background_tasks():
    """停止后台任务"""
    global _collection_task, _publish_task
    
    if _collection_task:
        _collection_task.cancel()
    if _publish_task:
        _publish_task.cancel()
    print("后台任务已停止")


async def _collection_loop():
    """定时采集循环"""
    while True:
        await collect_and_save()
        await asyncio.sleep(COLLECTION_INTERVAL)
