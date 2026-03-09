"""
配置管理模块
"""
from pydantic import BaseModel
from typing import Optional


class CollectorConfig(BaseModel):
    """采集配置"""
    collection_interval: int = 5  # 采集间隔（秒）
    publish_interval: int = 1      # 发布间隔（秒）
    max_history: int = 1000       # 最大历史记录数


# 全局配置
config = CollectorConfig()


def get_config() -> dict:
    """获取当前配置"""
    return config.model_dump()


def update_config(new_config: dict) -> dict:
    """更新配置"""
    global config
    for key, value in new_config.items():
        if hasattr(config, key):
            setattr(config, key, value)
    return get_config()
