"""
WSL + Windows 双环境采集客户端
当运行在 WSL 环境时，通过 HTTP 调用 Windows 侧的 Agent 获取真实硬件数据
当运行在 Windows/Linux 原生环境时，直接使用 psutil

用法: tasks/__init__.py 导入本模块而不是直接导入 collector
"""
import os
import platform
import subprocess
import requests
import time
import json

from . import collector

# ========================
# 环境检测
# ========================

def _detect_wsl():
    """检测是否在 WSL 环境"""
    try:
        release = platform.release().lower()
        # WSL2 detection: platform.release() like "5.15.153.1-microsoft-standard-WSL2"
        if "microsoft" in release or "wsl" in release:
            # Double-check by running uname
            result = subprocess.run(
                ["uname", "-r"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and ("microsoft" in result.stdout.lower() or "wsl" in result.stdout.lower()):
                return True
    except Exception:
        pass
    return False

IS_WSL = _detect_wsl()
USE_AGENT = os.environ.get("USE_WINDOWS_AGENT", "true").lower() == "true"

def _get_windows_host_ip():
    """从 WSL 自动检测 Windows 宿主机 IP"""
    try:
        # WSL 通过 route table 找默认网关（即 Windows 宿主机 IP）
        result = subprocess.run(
            ["sh", "-c", "ip route show | grep default | awk '{print $3}'"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            ip = result.stdout.strip()
            print(f"[Agent] 检测到 Windows 宿主机 IP: {ip}")
            return ip
    except Exception as e:
        print(f"[Agent] 检测 Windows IP 失败: {e}")
    return "172.21.144.1"  # fallback


# Windows Agent 地址 (Windows 侧监听端口)
_WINDOWS_IP = _get_windows_host_ip()
WINDOWS_AGENT_HOST = os.environ.get("WINDOWS_AGENT_HOST", f"http://{_WINDOWS_IP}:8001")

# Agent 请求超时
AGENT_TIMEOUT = 5


def _get_from_agent(path):
    """从 Windows Agent 获取数据"""
    try:
        resp = requests.get(f"{WINDOWS_AGENT_HOST}{path}", timeout=AGENT_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"[Agent] 请求失败 {path}: {e}")
        return None


def _post_to_agent(path, json_data):
    """向 Windows Agent 发送数据"""
    try:
        resp = requests.post(f"{WINDOWS_AGENT_HOST}{path}", json=json_data, timeout=AGENT_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"[Agent] POST 失败 {path}: {e}")
        return None


def _agent_available():
    """检查 Agent 是否可用"""
    try:
        resp = requests.get(f"{WINDOWS_AGENT_HOST}/health", timeout=3)
        return resp.status_code == 200
    except:
        return False


# ========================
# 指标采集函数（与 collector.py 接口一致）
# ========================

def get_cpu():
    """获取 CPU 使用率"""
    if IS_WSL and USE_AGENT:
        data = _get_from_agent("/metrics/cpu")
        if data:
            return data
        # Agent 不可用时降级到本地 psutil
        print("[Agent] CPU 降级到本地 psutil")
    return collector.get_cpu()


def get_memory():
    """获取内存使用情况"""
    if IS_WSL and USE_AGENT:
        data = _get_from_agent("/metrics/memory")
        if data:
            return data
        print("[Agent] 内存 降级到本地 psutil")
    return collector.get_memory()


def get_disk():
    """获取磁盘 I/O 统计"""
    if IS_WSL and USE_AGENT:
        data = _get_from_agent("/metrics/disk")
        if data:
            return data
        print("[Agent] 磁盘 降级到本地 psutil")
    return collector.get_disk()


def get_network():
    """获取网络 I/O 统计"""
    if IS_WSL and USE_AGENT:
        data = _get_from_agent("/metrics/network")
        if data:
            return data
        print("[Agent] 网络 降级到本地 psutil")
    return collector.get_network()


def get_all_metrics():
    """获取所有监控指标（组合模式：WSL通过Agent获取，Windows/Linux直接采集）"""
    if IS_WSL and USE_AGENT:
        data = _get_from_agent("/metrics/all")
        if data:
            return data
        print("[Agent] 全量指标 降级到本地 psutil")

    # 降级：组合各指标（与 collector.py 保持一致）
    disk = get_disk()
    disk.update(collector.get_disk_rate())

    network = get_network()
    network.update(collector.get_network_rate())

    return {
        "cpu": get_cpu(),
        "memory": get_memory(),
        "disk": disk,
        "network": network,
        "timestamp": int(time.time() * 1000)
    }


def get_system_info():
    """获取系统硬件信息"""
    if IS_WSL and USE_AGENT:
        data = _get_from_agent("/metrics/system/info")
        if data:
            return data
        print("[Agent] 系统信息 降级到本地")
    return collector.get_system_info()


def get_processes(top_n: int = 10):
    """获取进程列表（按 CPU 占用排序）"""
    if IS_WSL and USE_AGENT:
        data = _get_from_agent(f"/processes/?top={top_n}&sort=cpu")
        if data:
            return data
        print("[Agent] 进程 降级到本地")
    return collector.get_processes(top_n)


def get_top_processes_by_cpu(top_n: int = 10):
    """获取 CPU 占用最高的进程"""
    if IS_WSL and USE_AGENT:
        data = _get_from_agent(f"/processes/top/cpu?top={top_n}")
        if data:
            return data
    return collector.get_top_processes_by_cpu(top_n)


def get_top_processes_by_memory(top_n: int = 10):
    """获取内存占用最高的进程"""
    if IS_WSL and USE_AGENT:
        data = _get_from_agent(f"/processes/top/memory?top={top_n}")
        if data:
            return data
    return collector.get_top_processes_by_memory(top_n)


# ========================
# 内部工具函数（保持与 collector.py 一致）
# ========================

def get_disk_rate():
    """获取磁盘 I/O 速率"""
    return collector.get_disk_rate()


def get_network_rate():
    """获取网络 I/O 速率"""
    return collector.get_network_rate()


def _warmup():
    """预热"""
    return collector._warmup()


def local_compare_metrics():
    """本地 psutil 对照（用于测试图生成时对比）"""
    try:
        return collector.local_compare_metrics()
    except AttributeError:
        return {"cpu_percent": 0, "memory_percent": 0, "disk_rate_mb": 0, "network_rate_kb": 0}


# ========================
# 导出（与 collector.py 一致）
# ========================

__all__ = [
    "get_cpu",
    "get_memory",
    "get_disk",
    "get_network",
    "get_all_metrics",
    "get_system_info",
    "get_disk_rate",
    "get_network_rate",
    "get_processes",
    "get_top_processes_by_cpu",
    "get_top_processes_by_memory",
    "IS_WSL",
    "USE_AGENT",
]