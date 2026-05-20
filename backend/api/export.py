"""
API 路由 - 数据导出
"""
import csv
import io
from datetime import datetime
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from db import get_history_metrics


def _fmt(ts):
    """将毫秒时间戳转为本地可读时间字符串"""
    if ts:
        try:
            return datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            return str(ts)
    return '-'

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/csv")
async def export_csv(
    metric_type: str = Query(..., description="指标类型: cpu, memory, disk, network"),
    start_time: int = Query(..., description="开始时间戳 (毫秒)"),
    end_time: int = Query(..., description="结束时间戳 (毫秒)"),
    limit: int = Query(1000, ge=1, le=10000)
):
    """导出 CSV 格式的历史数据"""
    data = get_history_metrics(metric_type, start_time, end_time, limit)
    
    # 生成 CSV
    output = io.StringIO()
    
    if metric_type == "cpu":
        writer = csv.DictWriter(output, fieldnames=["time", "cpu_percent"])
        writer.writeheader()
        for row in data:
            writer.writerow({
                "time": _fmt(row.get("timestamp")),
                "cpu_percent": row.get("cpu_percent")
            })
    
    elif metric_type == "memory":
        writer = csv.DictWriter(output, fieldnames=["time", "total", "available", "percent", "used"])
        writer.writeheader()
        for row in data:
            writer.writerow({
                "time": _fmt(row.get("timestamp")),
                "total": row.get("total"),
                "available": row.get("available"),
                "percent": row.get("percent"),
                "used": row.get("used")
            })
    
    elif metric_type == "disk":
        writer = csv.DictWriter(output, fieldnames=["time", "read_count", "write_count", "read_bytes", "write_bytes"])
        writer.writeheader()
        for row in data:
            writer.writerow({
                "time": _fmt(row.get("timestamp")),
                "read_count": row.get("read_count"),
                "write_count": row.get("write_count"),
                "read_bytes": row.get("read_bytes"),
                "write_bytes": row.get("write_bytes")
            })
    
    elif metric_type == "network":
        writer = csv.DictWriter(output, fieldnames=["time", "bytes_sent", "bytes_recv", "pack_sent", "pack_recv"])
        writer.writeheader()
        for row in data:
            writer.writerow({
                "time": _fmt(row.get("timestamp")),
                "bytes_sent": row.get("bytes_sent"),
                "bytes_recv": row.get("bytes_recv"),
                "pack_sent": row.get("pack_sent"),
                "pack_recv": row.get("pack_recv")
            })
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={metric_type}_export.csv"}
    )
