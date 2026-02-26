"""Módulo de logging centralizado para o PyRPA."""

import logging
from datetime import datetime
from pathlib import Path


class RPALogger:
    """Logger centralizado que grava em arquivo e mantém histórico em memória."""

    def __init__(self, log_file: str = "pyrpa.log"):
        self.entries: list[dict] = []
        self.log_file = log_file

        self._logger = logging.getLogger("PyRPA")
        if not self._logger.handlers:
            self._logger.setLevel(logging.DEBUG)
            fh = logging.FileHandler(log_file, encoding="utf-8")
            fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
            self._logger.addHandler(fh)

    def log(self, message: str, level: str = "INFO"):
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "level": level.upper(),
            "message": message,
        }
        self.entries.insert(0, entry)

        lvl = getattr(logging, level.upper(), logging.INFO)
        self._logger.log(lvl, message)

    def get_entries(self, level: str | None = None, limit: int = 100) -> list[dict]:
        entries = self.entries
        if level:
            entries = [e for e in entries if e["level"] == level.upper()]
        return entries[:limit]

    def clear(self):
        self.entries.clear()
