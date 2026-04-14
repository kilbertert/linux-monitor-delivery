"""
API 路由 - 告警管理
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from alerts import alert_manager
from db import get_alert_history

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/rules")
async def get_rules():
    """获取所有告警规则"""
    return {
        "rules": alert_manager.get_rules()
    }


@router.get("/history")
async def get_alert_logs(
    start_time: Optional[int] = Query(None, description="开始时间戳 (毫秒)"),
    end_time: Optional[int] = Query(None, description="结束时间戳 (毫秒)"),
    limit: int = Query(100, ge=1, le=1000, description="返回条数限制"),
    metric: Optional[str] = Query(None, description="按指标筛选"),
    rule_name: Optional[str] = Query(None, description="按规则名称筛选"),
):
    """获取告警历史记录"""
    logs = get_alert_history(
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        metric=metric,
        rule_name=rule_name,
    )
    return {
        "count": len(logs),
        "data": logs,
    }


class RuleUpdate(BaseModel):
    enabled: Optional[bool] = None
    threshold: Optional[float] = None


@router.post("/rules/{rule_name}")
async def update_alert_rule(rule_name: str, update: RuleUpdate):
    """更新告警规则"""
    update_dict = update.model_dump(exclude_unset=True)
    if not update_dict:
        raise HTTPException(status_code=400, detail="没有提供有效的更新项")
    
    success = alert_manager.update_rule(rule_name, **update_dict)
    if not success:
        raise HTTPException(status_code=404, detail=f"规则 {rule_name} 不存在")
    
    return {
        "message": "规则更新成功",
        "rules": alert_manager.get_rules()
    }


@router.post("/rules/{rule_name}/toggle")
async def toggle_alert_rule(rule_name: str):
    """切换告警规则状态"""
    for rule in alert_manager.rules:
        if rule.name == rule_name:
            rule.enabled = not rule.enabled
            return {
                "message": f"规则 {'启用' if rule.enabled else '禁用'}",
                "enabled": rule.enabled
            }
    raise HTTPException(status_code=404, detail=f"规则 {rule_name} 不存在")
