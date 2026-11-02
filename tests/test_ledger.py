"""Tests for the hash-chained ledger (Art. 12, 19)."""

import json
import os

from src.ledger.hash_chain import HashChainedLedger


def test_genesis_hash_for_empty_ledger(tmp_path):
    path = tmp_path / "events.jsonl"
    ledger = HashChainedLedger(str(path))
    assert ledger._last_hash() == HashChainedLedger.GENESIS


def test_chain_links_events(tmp_path):
    path = tmp_path / "events.jsonl"
    ledger = HashChainedLedger(str(path))

    e1 = ledger.log("sys.a", "Seg", "act", "input1", "out1")
    e2 = ledger.log("sys.a", "Seg", "act", "input2", "out2")

    assert e1["prev_hash"] == HashChainedLedger.GENESIS
    assert e2["prev_hash"] == e1["hash"]

    with open(path, "r", encoding="utf-8") as f:
        lines = [json.loads(l) for l in f if l.strip()]
    assert len(lines) == 2
    assert lines[0]["hash"] == e1["hash"]
    assert lines[1]["hash"] == e2["hash"]


def test_input_hash_is_deterministic(tmp_path):
    path = tmp_path / "events.jsonl"
    ledger = HashChainedLedger(str(path))
    e1 = ledger.log("sys", "Seg", "act", "same", "out")
    e2 = ledger.log("sys", "Seg", "act", "same", "out")
    assert e1["input_hash"] == e2["input_hash"]


def test_output_summary_truncated(tmp_path):
    path = tmp_path / "events.jsonl"
    ledger = HashChainedLedger(str(path))
    entry = ledger.log("sys", "Seg", "act", "in", "x" * 500)
    assert len(entry["output_summary"]) <= 300
