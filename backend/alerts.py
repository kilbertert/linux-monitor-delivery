"""
告警管理模块
"""
from typing import Dict, List, Callable
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AlertRule:
    """告警规则"""
    name: str
    metric: str  # cpu, memory, disk, network
    threshold: float
    operator: str  # >, <, >=
    enabled: bool = True


# 默认告警规则
DEFAULT_RULES = [
    AlertRule("CPU 高负载", "cpu", 80, ">="),
    AlertRule("内存高占用", "memory", 85, ">="),
    AlertRule("磁盘读取高", "disk_read", 100, ">="),
    AlertRule("磁盘写入高", "disk_write", 100, ">="),
    AlertRule("网络接收高", "network_recv", 10000, ">="),
    AlertRule("网络发送高", "network_send", 10000, ">="),
]


class AlertManager:
    """告警管理器"""
    
    def __init__(self):
        self.rules: List[AlertRule] = DEFAULT_RULES.copy()
        self.handlers: List[Callable] = []  # 告警回调
    
    def add_handler(self, handler: Callable):
        """添加告警处理器"""
        self.handlers.append(handler)
    
    def check(self, metrics: dict) -> List[dict]:
        """检查指标，触发告警"""
        alerts = []
        
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            value = self._get_metric_value(metrics, rule.metric)
            if value is None:
                continue
            
            triggered = self._compare(value, rule.threshold, rule.operator)
            
            if triggered:
                alert = {
                    "rule": rule.name,
                    "metric": rule.metric,
                    "value": value,
                    "threshold": rule.threshold,
                    "operator": rule.operator,
                    "timestamp": datetime.now().isoformat()
                }
                alerts.append(alert)
                
                # 调用告警处理器
                for handler in self.handlers:
                    try:
                        handler(alert)
                    except Exception as e:
                        print(f"告警处理失败: {e}")
        
        return alerts
    
    def _get_metric_value(self, metrics: dict, metric: str):
        """获取指标值"""
        if metric == "cpu":
            return metrics.get("cpu", {}).get("percent")
        elif metric == "memory":
            return metrics.get("memory", {}).get("percent")
        elif metric == "disk_read":
            return metrics.get("disk", {}).get("read_rate")
        elif metric == "disk_write":
            return metrics.get("disk", {}).get("write_rate")
        elif metric == "network_recv":
            return metrics.get("network", {}).get("recv_rate")
        elif metric == "network_send":
            return metrics.get("network", {}).get("send_rate")
        return None
    
    def _compare(self, value: float, threshold: float, operator: str) -> bool:
        """比较值"""
        if operator == ">":
            return value > threshold
        elif operator == "<":
            return value < threshold
        elif operator == ">=":
            return value >= threshold
        elif operator == "<=":
            return value <= threshold
        elif operator == "==":
            return value == threshold
        return False
    
    def get_rules(self) -> List[dict]:
        """获取所有规则"""
        return [
            {
                "name": r.name,
                "metric": r.metric,
                "threshold": r.threshold,
                "operator": r.operator,
                "enabled": r.enabled
            }
            for r in self.rules
        ]
    
    def update_rule(self, name: str, **kwargs):
        """更新规则"""
        for rule in self.rules:
            if rule.name == name:
                for key, value in kwargs.items():
                    if hasattr(rule, key):
                        setattr(rule, key, value)
                return True
        return False


# 全局告警管理器
alert_manager = AlertManager()
