"""
API 路由 - 配置管理
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from config import get_config, update_config

router = APIRouter(prefix="/config", tags=["config"])


class ConfigUpdate(BaseModel):
    collection_interval: Optional[int] = None
    publish_interval: Optional[int] = None
    max_history: Optional[int] = None


@router.get("")
async def get_settings():
    """获取当前配置"""
    return get_config()


@router.post("")
async def update_settings(config_update: ConfigUpdate):
    """更新配置"""
    update_dict = config_update.model_dump(exclude_unset=True)
    if not update_dict:
        raise HTTPException(status_code=400, detail="没有提供有效的配置项")
    
    # 验证参数
    if update_dict.get("collection_interval"):
        interval = update_dict["collection_interval"]
        if interval < 1 or interval > 3600:
            raise HTTPException(status_code=400, detail="collection_interval 必须在 1-3600 之间")
    
    if update_dict.get("publish_interval"):
        interval = update_dict["publish_interval"]
        if interval < 1 or interval > 60:
            raise HTTPException(status_code=400, detail="publish_interval 必须在 1-60 之间")
    
    new_config = update_config(update_dict)
    return {
        "message": "配置更新成功",
        "config": new_config
    }


@router.post("/reset")
async def reset_settings():
    """重置为默认配置"""
    from config import CollectorConfig
    global config
    config = CollectorConfig()
    return {
        "message": "配置已重置",
        "config": get_config()
    }
