"""资源监控器 — 防止Agent把服务器跑崩"""
import enum
import time
from dataclasses import dataclass, field


class ResourceStatus(enum.Enum):
    OK = "ok"
    WARNING = "warning"  # 暂停新任务
    CRITICAL = "critical"  # 停止所有Agent进程


@dataclass
class ResourceMonitor:
    cpu_warning: float = 70.0
    cpu_critical: float = 90.0
    memory_warning_mb: float = 1200.0
    memory_critical_mb: float = 1600.0
    disk_warning_gb: float = 30.0
    disk_critical_gb: float = 35.0
    bandwidth_limit_mbps: float = 50.0

    _last_cpu: float = 0.0
    _last_memory: float = 0.0
    _last_disk: float = 0.0
    _last_check_time: float = 0.0
    _history: list = field(default_factory=list)

    def check(self, cpu_percent: float, memory_mb: float, disk_gb: float) -> ResourceStatus:
        """检查资源状态并返回"""
        self._last_cpu = cpu_percent
        self._last_memory = memory_mb
        self._last_disk = disk_gb
        self._last_check_time = time.time()

        # 熔断优先
        if (cpu_percent >= self.cpu_critical or
                memory_mb >= self.memory_critical_mb or
                disk_gb >= self.disk_critical_gb):
            status = ResourceStatus.CRITICAL
        elif (cpu_percent >= self.cpu_warning or
              memory_mb >= self.memory_warning_mb or
              disk_gb >= self.disk_warning_gb):
            status = ResourceStatus.WARNING
        else:
            status = ResourceStatus.OK

        self._history.append({
            "time": self._last_check_time,
            "cpu": cpu_percent,
            "memory_mb": memory_mb,
            "disk_gb": disk_gb,
            "status": status.value,
        })

        if len(self._history) > 100:
            self._history = self._history[-100:]

        return status

    def get_report(self) -> str:
        """生成资源报告"""
        return (
            f"资源状态报告:\n"
            f"  CPU: {self._last_cpu:.1f}% (警戒:{self.cpu_warning}% 熔断:{self.cpu_critical}%)\n"
            f"  内存: {self._last_memory:.0f}MB (警戒:{self.memory_warning_mb}MB 熔断:{self.memory_critical_mb}MB)\n"
            f"  磁盘: {self._last_disk:.1f}GB (警戒:{self.disk_warning_gb}GB 熔断:{self.disk_critical_gb}GB)\n"
            f"  带宽限速: {self.bandwidth_limit_mbps}Mbps"
        )

    def should_throttle(self) -> bool:
        """是否需要限流"""
        return self._last_cpu >= self.cpu_warning or self._last_memory >= self.memory_warning_mb
