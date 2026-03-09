"""
数据库模块
使用 SQLite 存储监控数据
"""
import sqlite3
import json
import time
from typing import Dict, Any, List, Optional
from pathlib import Path


DB_PATH = Path(__file__).parent.parent / "monitor.db"


def get_connection() -> sqlite3.Connection:
    """获取数据库连接"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库表"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # CPU 统计表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cpu_stat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER NOT NULL,
            cpu_percent REAL NOT NULL,
            cpu_per_core TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 内存统计表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory_stat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER NOT NULL,
            total REAL NOT NULL,
            available REAL NOT NULL,
            percent REAL NOT NULL,
            used REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 网络统计表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS net_stat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER NOT NULL,
            bytes_sent INTEGER NOT NULL,
            bytes_recv INTEGER NOT NULL,
            pack_sent INTEGER NOT NULL,
            pack_recv INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 磁盘 I/O 统计表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS disk_stat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER NOT NULL,
            read_count INTEGER NOT NULL,
            write_count INTEGER NOT NULL,
            read_bytes INTEGER NOT NULL,
            write_bytes INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 创建索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cpu_timestamp ON cpu_stat(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_memory_timestamp ON memory_stat(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_net_timestamp ON net_stat(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_disk_timestamp ON disk_stat(timestamp)")
    
    conn.commit()
    conn.close()
    print(f"数据库初始化完成: {DB_PATH}")


def save_metrics(metrics: Dict[str, Any]):
    """保存监控指标到数据库"""
    conn = get_connection()
    cursor = conn.cursor()
    timestamp = int(time.time() * 1000)  # 毫秒时间戳
    
    try:
        # 保存 CPU 数据
        cursor.execute(
            "INSERT INTO cpu_stat (timestamp, cpu_percent, cpu_per_core) VALUES (?, ?, ?)",
            (timestamp, metrics["cpu"]["percent"], json.dumps(metrics["cpu"]["per_core"]))
        )
        
        # 保存内存数据
        mem = metrics["memory"]
        cursor.execute(
            "INSERT INTO memory_stat (timestamp, total, available, percent, used) VALUES (?, ?, ?, ?, ?)",
            (timestamp, mem["total"], mem["available"], mem["percent"], mem["used"])
        )
        
        # 保存网络数据
        net = metrics["network"]
        cursor.execute(
            "INSERT INTO net_stat (timestamp, bytes_sent, bytes_recv, pack_sent, pack_recv) VALUES (?, ?, ?, ?, ?)",
            (timestamp, net["bytes_sent"], net["bytes_recv"], net["pack_sent"], net["pack_recv"])
        )
        
        # 保存磁盘数据
        disk = metrics["disk"]
        cursor.execute(
            "INSERT INTO disk_stat (timestamp, read_count, write_count, read_bytes, write_bytes) VALUES (?, ?, ?, ?, ?)",
            (timestamp, disk["read_count"], disk["write_count"], disk["read_bytes"], disk["write_bytes"])
        )
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"保存数据失败: {e}")
    finally:
        conn.close()


def get_history_metrics(
    metric_type: str,
    start_time: int,
    end_time: int,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    获取历史指标
    
    Args:
        metric_type: cpu, memory, disk, network
        start_time: 开始时间戳 (毫秒)
        end_time: 结束时间戳 (毫秒)
        limit: 返回条数限制
    
    Returns:
        指标列表
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    table_map = {
        "cpu": "cpu_stat",
        "memory": "memory_stat",
        "disk": "disk_stat",
        "network": "net_stat"
    }
    
    table = table_map.get(metric_type)
    if not table:
        return []
    
    # 构建查询
    query = f"SELECT * FROM {table} WHERE timestamp >= ? AND timestamp <= ? ORDER BY timestamp DESC LIMIT ?"
    cursor.execute(query, (start_time, end_time, limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        result = dict(row)
        if metric_type == "cpu" and result.get("cpu_per_core"):
            result["cpu_per_core"] = json.loads(result["cpu_per_core"])
        results.append(result)
    
    return results


if __name__ == "__main__":
    init_db()
