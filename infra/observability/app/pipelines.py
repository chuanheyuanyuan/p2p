import json
from pathlib import Path
from typing import Any, Dict

from .config import Settings


class KafkaEmitter:
    def __init__(self, settings: Settings) -> None:
        self.enabled = settings.kafka_enabled
        self.log_path = Path(settings.kafka_log_path)
        self.topic = settings.kafka_topic

    def emit(self, payload: Dict[str, Any]) -> None:
        if not self.enabled:
            return
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        record = {'topic': self.topic, 'payload': payload}
        with self.log_path.open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(record, default=str) + '\n')


class ClickHouseWriter:
    def __init__(self, settings: Settings) -> None:
        self.enabled = settings.clickhouse_enabled
        self.log_path = Path(settings.clickhouse_log_path)

    def write(self, payload: Dict[str, Any]) -> None:
        if not self.enabled:
            return
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(payload, default=str) + '\n')
