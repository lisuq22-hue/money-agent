"""赚钱模块基类 — 所有赚钱渠道的抽象接口"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class RevenueReport:
    """收入报告"""
    platform: str
    period: str
    gross_income: float
    net_income: float
    details: dict


class RevenuePlugin(ABC):
    """赚钱模块基类"""

    def __init__(self, name: str, config: dict):
        self.name = name
        self.config = config
        self._enabled = True

    @property
    def enabled(self) -> bool:
        return self._enabled

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False

    @abstractmethod
    def check_credentials(self) -> bool:
        """验证凭证是否有效"""
        ...

    @abstractmethod
    def get_revenue_report(self) -> RevenueReport:
        """获取收入报告"""
        ...

    @abstractmethod
    def do_work(self) -> dict:
        """执行赚钱任务"""
        ...

    @abstractmethod
    def get_status(self) -> dict:
        """获取模块状态"""
        ...

    def __repr__(self):
        return f"RevenuePlugin({self.name}, enabled={self._enabled})"
