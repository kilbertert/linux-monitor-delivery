"""
监控数据采集模块
使用 psutil 采集系统指标
"""
import psutil
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import json


# 预热标志
_warmed = False


def _warmup():
    """预热 psutil，丢弃首次调用结果"""
    global _warmed
    if not _warmed:
        psutil.cpu_percent(interval=None)
        psutil.cpu_percent(interval=0.1)
        psutil.cpu_percent(interval=None)
        time.sleep(0.1)
        _warmed = True


def get_cpu() -> Dict[str, Any]:
    """
    获取 CPU 使用率
    返回: {
        "percent": float,  # 总 CPU 使用率
        "per_core": List[dict],  # 每核心使用率
        "count": int  # CPU 核心数
    }
    """
    _warmup()
    
    per_core = psutil.cpu_percent(interval=0.1, percpu=True)
    total = psutil.cpu_percent(interval=0.1)
    
    return {
        "percent": round(total, 2),
        "per_core": [{"core": i, "percent": round(p, 2)} for i, p in enumerate(per_core)],
        "count": psutil.cpu_count()
    }


def get_memory() -> Dict[str, Any]:
    """
    获取内存使用情况
    返回: {
        "total": float,  # 总内存 (GB)
        "available": float,  # 可用内存 (GB)
        "used": float,  # 已用内存 (GB)
        "percent": float  # 使用率
    }
    """
    mem = psutil.virtual_memory()
    
    return {
        "total": round(mem.total / (1024**3), 2),
        "available": round(mem.available / (1024**3), 2),
        "used": round(mem.used / (1024**3), 2),
        "percent": round(mem.percent, 2)
    }


def get_disk() -> Dict[str, Any]:
    """
    获取磁盘 I/O 统计
    返回: {
        "read_count": int,
        "write_count": int,
        "read_bytes": int,
        "write_bytes": int,
        "read_rate": float,  # MB/s
        "write_rate": float  # MB/s
    }
    """
    disk_io = psutil.disk_io_counters()
    
    return {
        "read_count": disk_io.read_count,
        "write_count": disk_io.write_count,
        "read_bytes": disk_io.read_bytes,
        "write_bytes": disk_io.write_bytes,
        "read_rate": round(disk_io.read_bytes / (1024**2), 2),  # MB
        "write_rate": round(disk_io.write_bytes / (1024**2), 2)  # MB
    }


def get_network() -> Dict[str, Any]:
    """
    获取网络 I/O 统计
    返回: {
        "bytes_sent": int,
        "bytes_recv": int,
        "pack_sent": int,
        "pack_recv": int,
        "send_rate": float,  # KB/s
        "recv_rate": float  # KB/s
    }
    """
    net_io = psutil.net_io_counters()
    
    return {
        "bytes_sent": net_io.bytes_sent,
        "bytes_recv": net_io.bytes_recv,
        "pack_sent": net_io.packets_sent,
        "pack_recv": net_io.packets_recv,
        "send_rate": round(net_io.bytes_sent / (1024), 2),  # KB
        "recv_rate": round(net_io.bytes_recv / (1024), 2)  # KB
    }


def get_all_metrics() -> Dict[str, Any]:
    """获取所有监控指标"""
    return {
        "cpu": get_cpu(),
        "memory": get_memory(),
        "disk": get_disk(),
        "network": get_network(),
        "timestamp": int(time.time() * 1000)
    }


def get_system_info() -> Dict[str, Any]:
    """获取系统硬件信息"""
    import platform
    
    # CPU 信息
    cpu_info = {}
    try:
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if 'model name' in line:
                    cpu_info['model'] = line.split(':')[1].strip()
                    break
    except:
        cpu_info['model'] = platform.processor() or 'Unknown'
    
    cpu_info['count'] = psutil.cpu_count()
    
    # 内存信息
    mem = psutil.virtual_memory()
    cpu_info['memory_total'] = round(mem.total / (1024**3), 2)
    
    # 磁盘信息
    disk = psutil.disk_usage('/')
    cpu_info['disk_total'] = round(disk.total / (1024**3), 2)
    
    # 系统信息
    cpu_info['platform'] = platform.platform()
    cpu_info['hostname'] = platform.node()
    cpu_info['uptime'] = psutil.boot_time()
    
    return cpu_info


# 用于差分计算的上一次数据
_last_disk_io = None
_last_net_io = None
_last_time = None


def get_disk_rate() -> Dict[str, float]:
    """获取磁盘 I/O 速率（需要两次调用计算差值）"""
    global _last_disk_io, _last_time
    
    current = psutil.disk_io_counters()
    current_time = time.time()
    
    if _last_disk_io is None:
        _last_disk_io = current
        _last_time = current_time
        return {"read_rate": 0, "write_rate": 0}
    
    time_diff = current_time - _last_time
    if time_diff == 0:
        return {"read_rate": 0, "write_rate": 0}
    
    read_rate = (current.read_bytes - _last_disk_io.read_bytes) / time_diff / (1024**2)
    write_rate = (current.write_bytes - _last_disk_io.write_bytes) / time_diff / (1024**2)
    
    _last_disk_io = current
    _last_time = current_time
    
    return {
        "read_rate": round(read_rate, 2),
        "write_rate": round(write_rate, 2)
    }


def get_network_rate() -> Dict[str, float]:
    """获取网络 I/O 速率（需要两次调用计算差值）"""
    global _last_net_io, _last_time
    
    current = psutil.net_io_counters()
    current_time = time.time()
    
    if _last_net_io is None:
        _last_net_io = current
        _last_time = current_time
        return {"send_rate": 0, "recv_rate": 0}
    
    time_diff = current_time - _last_time
    if time_diff == 0:
        return {"send_rate": 0, "recv_rate": 0}
    
    send_rate = (current.bytes_sent - _last_net_io.bytes_sent) / time_diff / 1024
    recv_rate = (current.bytes_recv - _last_net_io.bytes_recv) / time_diff / 1024
    
    _last_net_io = current
    _last_time = current_time
    
    return {
        "send_rate": round(send_rate, 2),
        "recv_rate": round(recv_rate, 2)
    }


if __name__ == "__main__":
    # 测试
    print("CPU:", json.dumps(get_cpu(), indent=2))
    print("Memory:", json.dumps(get_memory(), indent=2))
    print("Disk:", json.dumps(get_disk(), indent=2))
    print("Network:", json.dumps(get_network(), indent=2))
    print("System Info:", json.dumps(get_system_info(), indent=2))


def get_processes(top_n: int = 10) -> List[Dict[str, Any]]:
    """
    获取进程列表（按 CPU 占用排序）
    返回: [{pid, name, cpu_percent, memory_percent, status}, ...]
    """
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
        try:
            info = proc.info
            if info['cpu_percent'] is None:
                info['cpu_percent'] = 0
            if info['memory_percent'] is None:
                info['memory_percent'] = 0
            processes.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    # 按 CPU 占用排序
    processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
    return processes[:top_n]


def get_top_processes_by_cpu(top_n: int = 10) -> List[Dict[str, Any]]:
    """获取 CPU 占用最高的进程"""
    return get_processes(top_n)


def get_top_processes_by_memory(top_n: int = 10) -> List[Dict[str, Any]]:
    """获取内存占用最高的进程"""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
        try:
            info = proc.info
            if info['cpu_percent'] is None:
                info['cpu_percent'] = 0
            if info['memory_percent'] is None:
                info['memory_percent'] = 0
            processes.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    processes.sort(key=lambda x: x['memory_percent'], reverse=True)
    return processes[:top_n]
