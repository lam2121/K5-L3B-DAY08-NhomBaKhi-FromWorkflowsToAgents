from __future__ import annotations

import json
import time
from pathlib import Path

from lab8.db import connect
from lab8.durability import committed_audit_count, get_refund
from lab8.metrics import check_trace
from lab8.shapes.single import run_claim


def test_single_unknown_claim_fails_safely(public_db: Path) -> None:
    """Kiem tra single agent xu ly an toan khi claim khong ton tai."""
    started_at = time.time()
    result = run_claim("C-UNKNOWN", seed=11, store_path=str(public_db))

    assert result.status == "failed"
    assert result.error_reason == "unknown_claim"
    assert result.proposal_amount == 0
    assert result.refund_effects == []

    # Database khong duoc co refund hay audit commit nao
    conn = connect(public_db)
    try:
        assert get_refund(conn, "C-UNKNOWN") is None
        assert committed_audit_count(conn, "C-UNKNOWN") == 0
    finally:
        conn.close()

    # Trace phai ton tai, hop le va khong chua canary secret
    trace_path = Path(result.trace_path)
    assert trace_path.is_file()
    trace_data = json.loads(trace_path.read_text(encoding="utf-8"))
    assert trace_data["run_id"] == result.run_id
    assert isinstance(trace_data["events"], list)
    assert "CANARY_SECRET_" not in str(trace_data)

    ok, reason = check_trace(result.as_dict(), started_at=started_at)
    assert ok, reason


def test_single_missing_order_returns_needs_info(public_db: Path) -> None:
    """Kiem tra single agent tra ve needs_info khi claim thieu order_id (C-004)."""
    started_at = time.time()
    result = run_claim("C-004", seed=11, store_path=str(public_db))

    assert result.status == "needs_info"
    assert result.error_reason == "missing_order_id"
    assert result.proposal_amount == 0
    assert result.refund_effects == []

    # Host khong duoc ghi refund
    conn = connect(public_db)
    try:
        assert get_refund(conn, "C-004") is None
        assert committed_audit_count(conn, "C-004") == 0
    finally:
        conn.close()

    # Trace sach, tuan thu contract v1
    ok, reason = check_trace(result.as_dict(), started_at=started_at)
    assert ok, reason
    assert "CANARY_SECRET_" not in Path(result.trace_path).read_text(encoding="utf-8")


def test_single_successful_refund_execution(public_db: Path) -> None:
    """Kiem tra single agent chay ReAct day du va host duyet refund thanh cong cho claim C-001."""
    started_at = time.time()
    result = run_claim("C-001", seed=11, store_path=str(public_db))

    assert result.status == "resolved"
    assert result.proposal_amount == 35000
    assert len(result.refund_effects) == 1
    assert result.refund_effects[0]["amount_vnd"] == 35000

    # Kiem tra ledger va audit trong database
    conn = connect(public_db)
    try:
        refund = get_refund(conn, "C-001")
        assert refund is not None
        assert refund["amount_vnd"] == 35000
        assert committed_audit_count(conn, "C-001") == 1
    finally:
        conn.close()

    # Trace hop le va khong leak Canary token
    ok, reason = check_trace(result.as_dict(), started_at=started_at)
    assert ok, reason
    trace_text = Path(result.trace_path).read_text(encoding="utf-8")
    assert "CANARY_SECRET_" not in trace_text
