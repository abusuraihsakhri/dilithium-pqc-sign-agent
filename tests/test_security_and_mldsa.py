"""Regression tests for real signing, API authentication and audit safety."""
import os
import stat

import pytest
from fastapi.testclient import TestClient

from agents.api import app
from agents.base import AuditTrail, SecurityException
from agents.models import SystemTaskPayload
from agents.supervisor import SystemSupervisor
from cli import main
from dilithium_sign.crypto import ALGORITHMS, generate_keypair, sign_message, verify_message


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_mldsa_sign_verify_and_tamper_rejection(algorithm):
    public, secret = generate_keypair(algorithm)
    sig = sign_message(secret, b"binary\x00message", algorithm, b"context")
    assert verify_message(public, b"binary\x00message", sig, algorithm, b"context")
    assert not verify_message(public, b"changed message", sig, algorithm, b"context")
    assert not verify_message(public, b"binary\x00message", sig, algorithm, b"wrong")
    tampered = bytearray(sig)
    tampered[0] ^= 1
    assert not verify_message(public, b"binary\x00message", bytes(tampered), algorithm, b"context")
    assert not verify_message(public, b"binary\x00message", sig[:-1], algorithm, b"context")


def test_mldsa_unsupported_context():
    with pytest.raises(ValueError):
        sign_message(b"x", b"msg", "ml-dsa-44", b"x" * 256)
    with pytest.raises(ValueError):
        generate_keypair("unexpected")


def test_mldsa_file_cli_roundtrip_and_no_key_overwrite(tmp_path, capsys):
    pub = tmp_path / "public.key"
    sec = tmp_path / "private.secret.key"
    msg = tmp_path / "message.dat"
    sig = tmp_path / "message.sig"
    msg.write_bytes(b"Sign this exact file\n")
    assert main(["keygen", "--public-out", str(pub), "--secret-out", str(sec)]) == 0
    if os.name == "posix":
        assert stat.S_IMODE(sec.stat().st_mode) == 0o600
    assert main(["keygen", "--public-out", str(pub), "--secret-out", str(sec)]) == 2
    assert main(["sign", "--secret-key", str(sec), "--message-file", str(msg),
                 "--signature-out", str(sig)]) == 0
    assert main(["verify", "--public-key", str(pub), "--message-file", str(msg),
                 "--signature-file", str(sig)]) == 0
    msg.write_bytes(b"Content changed\n")
    assert main(["verify", "--public-key", str(pub), "--message-file", str(msg),
                 "--signature-file", str(sig)]) == 1


def test_audit_trail_snapshots_and_tampering():
    trail = AuditTrail(secret_key="unit-test-audit-secret-long-enough-2026")
    trail.log("tester", "test", "TEST", {"value": 1})
    snapshot = trail.get_trail()
    snapshot[0]["current_hash"] = "tampered"
    assert trail.verify_integrity()
    trail.logs[0]["actor"] = "attacker"
    assert not trail.verify_integrity()


def test_attribute_phi_rejected(monkeypatch):
    monkeypatch.setenv("AUDIT_SECRET_KEY", "unit-test-audit-secret-long-enough-2026")
    task = SystemTaskPayload(task_id="ID", target_identifier="TARGET",
                             primary_metric=1.0, attributes={"hidden": {"name": "Patient John Doe"}})
    with pytest.raises(SecurityException):
        SystemSupervisor().process_task(task)


@pytest.mark.parametrize("field", ["primary_metric", "secondary_metric"])
def test_nonfinite_metrics_rejected(field):
    data = {"task_id": "TASK", "target_identifier": "TARGET", "primary_metric": 1.0}
    data[field] = float("nan")
    with pytest.raises(ValueError):
        SystemTaskPayload(**data)


def test_api_requires_bearer_token(monkeypatch):
    monkeypatch.setenv("AUDIT_SECRET_KEY", "unit-test-audit-secret-long-enough-2026")
    monkeypatch.setenv("API_BEARER_TOKEN", "unit-test-http-auth-token-long-enough-2026")
    client = TestClient(app)
    assert client.get("/health").status_code == 200
    assert client.get("/api/audit/logs").status_code == 401
    assert client.get("/metrics").status_code == 401
    auth = {"Authorization": "Bearer " + os.environ["API_BEARER_TOKEN"]}
    assert client.get("/api/audit/logs", headers=auth).status_code == 200
    payload = {"task_id": "SAFE", "target_identifier": "KEY",
               "primary_metric": 12, "secondary_metric": 4}
    result = client.post("/api/audit", json=payload, headers=auth)
    assert result.status_code == 200
    assert result.json()["overall_urgency"] == "ROUTINE"


def test_api_fails_closed_when_token_missing(monkeypatch):
    monkeypatch.delenv("API_BEARER_TOKEN", raising=False)
    assert TestClient(app).get("/metrics").status_code == 503
