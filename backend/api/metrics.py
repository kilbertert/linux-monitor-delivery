"""
API 路由 - 监控指标
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from datetime import datetime
import time

from monitor import collector
from db import get_history_metrics

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/current")
async def get_current_metrics():
    """获取当前最新指标"""
    return collector.get_all_metrics()


@router.get("/cpu")
async def get_cpu_metrics():
    """获取 CPU 指标"""
    return collector.get_cpu()


@router.get("/memory")
async def get_memory_metrics():
    """获取内存指标"""
    return collector.get_memory()


@router.get("/disk")
async def get_disk_metrics():
    """获取磁盘 I/O 指标"""
    return collector.get_disk()


@router.get("/network")
async def get_network_metrics():
    """获取网络 I/O 指标"""
    return collector.get_network()


@router.get("/history")
async def get_history(
    metric_type: str = Query(..., description="指标类型: cpu, memory, disk, network"),
    start_time: Optional[int] = Query(None, description="开始时间戳 (毫秒)"),
    end_time: Optional[int] = Query(None, description="结束时间戳 (毫秒)"),
    limit: int = Query(100, ge=1, le=1000, description="返回条数限制")
):
    """获取历史指标"""
    valid_types = ["cpu", "memory", "disk", "network"]
    if metric_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"无效的指标类型: {metric_type}")
    
    # 默认时间范围：最近 1 小时
    now = int(time.time() * 1000)
    if start_time is None:
        start_time = now - 3600 * 1000  # 1 小时前
    if end_time is None:
        end_time = now
    
    if start_time >= end_time:
        raise HTTPException(status_code=400, detail="start_time 必须小于 end_time")
    
    data = get_history_metrics(metric_type, start_time, end_time, limit)
    return {
        "metric_type": metric_type,
        "start_time": start_time,
        "end_time": end_time,
        "count": len(data),
        "data": data
    }


@router.get("/system/info")
async def get_system_info():
    """获取系统硬件信息"""
    return collector.get_system_info()
