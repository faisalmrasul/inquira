"""Hash-chained ledger for compliance events (Art. 12, 19)."""

from __future__ import annotations

import hashlib
import json
import os
from typing import Any, Dict, Optional

from src.config import DEFAULT_LEDGER_PATH, OUTPUT_SUMMARY_MAX, utcnow


class HashChainedLedger:
    GENESIS = "0" * 64

    def __init__(self, path: str = DEFAULT_LEDGER_PATH):
        self.path = path

    def _last_hash(self) -> str:
        if not os.path.exists(self.path) or os.path.getsize(self.path) == 0:
            return self.GENESIS
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            return json.loads(lines[-1])["hash"] if lines else self.GENESIS
        except Exception:
            return self.GENESIS

    def log(
        self,
        system_id: str,
        segment: str,
        action: str,
        input_text: str,
        output_summary: str,
        approved_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        body = {
            "ts": utcnow().isoformat(),
            "system_id": system_id,
            "segment": segment,
            "action": action,
            "actor": approved_by or "system",
            "input_hash": hashlib.sha256(input_text.encode("utf-8")).hexdigest()[:16],
            "output_summary": output_summary[:OUTPUT_SUMMARY_MAX],
            "prev_hash": self._last_hash(),
        }
        body["hash"] = hashlib.sha256(
            json.dumps(body, sort_keys=True).encode("utf-8")
        ).hexdigest()
        try:
            os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(body) + "\n")
        except Exception:
            pass
        return body
