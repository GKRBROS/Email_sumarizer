import json
import os
from typing import Set


class StateStore:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._processed_ids: Set[str] = set()
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self.file_path):
            self._processed_ids = set()
            return
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            items = data.get("processed_ids", [])
            self._processed_ids = set(str(item) for item in items)
        except Exception:
            self._processed_ids = set()

    def _save(self) -> None:
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump({"processed_ids": sorted(self._processed_ids)}, file, ensure_ascii=False, indent=2)

    def has(self, message_id: str) -> bool:
        return message_id in self._processed_ids

    def add(self, message_id: str) -> None:
        self._processed_ids.add(message_id)
        self._save()
