"""
FastAPI REST API Server for Dilithium Pqc Sign Agent.
"""
import os
import hmac
from typing import Dict, Any, List

from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from .base import AuditLogger, PHIGuard, SecurityException
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Dilithium Pqc Sign Agent API",
    description="Enterprise Distributed Component Platform (Post-Quantum Cryptography & Hardware Security)",
    version="3.0.0-ENTERPRISE",
)


class ChatRequest(BaseModel):
    query: str


def require_auth(authorization: str | None = Header(default=None)):
    """Fail closed when the server has no configured bearer credential."""
    token = os.environ.get("API_BEARER_TOKEN", "")
    if len(token) < 32:
        raise HTTPException(status_code=503, detail="API authentication is not configured")
    if not authorization or not hmac.compare_digest(authorization, f"Bearer {token}"):
        raise HTTPException(status_code=401, detail="Invalid bearer token", headers={"WWW-Authenticate": "Bearer"})


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "dilithium-pqc-sign-agent", "domain": "Post-Quantum Cryptography & Hardware Security", "standard": "NIST FIPS 203/204/205 / ISO/IEC 17825 Standards", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics", dependencies=[Depends(require_auth)])
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL_OPTIMAL"
    }


@app.post("/api/audit", dependencies=[Depends(require_auth)])
def api_audit(payload: SystemTaskPayload):
    try:
        dossier = supervisor.process_task(payload)
    except SecurityException:
        raise HTTPException(status_code=422, detail="Sensitive data was rejected") from None
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None
    return dossier.to_dict()


@app.post("/api/chat", dependencies=[Depends(require_auth)])
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except SecurityException:
        raise HTTPException(status_code=422, detail="Sensitive data was rejected") from None


@app.get("/api/audit/logs", dependencies=[Depends(require_auth)])
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
