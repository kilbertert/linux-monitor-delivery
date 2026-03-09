"""
API 路由 - 进程监控
"""
from fastapi import APIRouter, Query
from typing import Optional

from monitor import get_processes, get_top_processes_by_cpu, get_top_processes_by_memory

router = APIRouter(prefix="/processes", tags=["processes"])


@router.get("/")
async def get_process_list(
    top: int = Query(10, ge=1, le=100, description="返回进程数"),
    sort: str = Query("cpu", description="排序方式: cpu, memory")
):
    """获取进程列表"""
    if sort == "cpu":
        processes = get_top_processes_by_cpu(top_n=top)
    elif sort == "memory":
        processes = get_top_processes_by_memory(top_n=top)
    else:
        processes = get_processes(top_n=top)
    
    return {
        "count": len(processes),
        "processes": processes
    }


@router.get("/top/cpu")
async def get_top_cpu_processes(top: int = Query(10, ge=1, le=100)):
    """获取 CPU 占用最高的进程"""
    processes = get_top_processes_by_cpu(top_n=top)
    return {
        "count": len(processes),
        "processes": processes
    }


@router.get("/top/memory")
async def get_top_memory_processes(top: int = Query(10, ge=1, le=100)):
    """获取内存占用最高的进程"""
    processes = get_top_processes_by_memory(top_n=top)
    return {
        "count": len(processes),
        "processes": processes
    }
