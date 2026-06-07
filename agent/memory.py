"""记忆系统 — 短期/中期/长期记忆"""
import json
import os
import time
from dataclasses import dataclass, field


@dataclass
class Memory:
    """Agent的三级记忆系统"""
    data_dir: str

    _short_term: list = field(default_factory=list)  # 当前会话
    _medium_term: list = field(default_factory=list)  # 最近7天
    _long_term_path: str = ""

    def __post_init__(self):
        self._long_term_path = os.path.join(self.data_dir, "memory.json")
        os.makedirs(self.data_dir, exist_ok=True)
        self._load_long_term()

    def remember(self, content: str, importance: int = 1):
        """记录一条记忆"""
        entry = {
            "time": time.time(),
            "content": content,
            "importance": importance,
        }
        self._short_term.append(entry)
        self._medium_term.append(entry)
        if importance >= 7:
            self._long_term.append(entry)
            self._save_long_term()

    def recall_recent(self, limit: int = 10) -> list:
        """回忆最近的记忆"""
        return self._medium_term[-limit:]

    def recall_important(self, min_importance: int = 5) -> list:
        """回忆重要记忆"""
        return [m for m in self._long_term if m["importance"] >= min_importance]

    def summarize_session(self) -> str:
        """总结当前会话"""
        if not self._short_term:
            return "本会话无记录"
        items = [m["content"] for m in self._short_term[-20:]]
        return "本会话记忆:\n" + "\n".join(f"  · {item}" for item in items)

    def clear_session(self):
        """清空短期记忆，保留中长期"""
        self._short_term.clear()

    def consolidate(self):
        """记忆整合：把重要短期记忆归档到长期"""
        for entry in self._short_term:
            if entry["importance"] >= 5:
                self._long_term.append(entry)
        self._short_term.clear()
        self._medium_term = self._medium_term[-100:]
        self._save_long_term()

    def _load_long_term(self):
        if os.path.exists(self._long_term_path):
            with open(self._long_term_path, "r", encoding="utf-8") as f:
                self._long_term = json.load(f)
        else:
            self._long_term = []

    def _save_long_term(self):
        with open(self._long_term_path, "w", encoding="utf-8") as f:
            json.dump(self._long_term[-500:], f, ensure_ascii=False, indent=2)
