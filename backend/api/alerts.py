"""
API 路由 - 告警管理
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from alerts import alert_manager

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/rules")
async def get_rules():
    """获取所有告警规则"""
    return {
        "rules": alert_manager.get_rules()
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
