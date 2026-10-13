"""
FastAPI REST API Server for ML-DSA / CRYSTALS-Dilithium Post-Quantum Digital Signature Verification Agent.
"""
from typing import Dict, Any
import hmac
import os
from .models import FrontierPayload
from .agents import PQCSignatureCoordinator

coordinator = PQCSignatureCoordinator()


def create_app():
    try:
        from fastapi import FastAPI, HTTPException, Header, Depends
        from pydantic import BaseModel

        app = FastAPI(
            title="ML-DSA / CRYSTALS-Dilithium Post-Quantum Digital Signature Verification Agent",
            description="Legacy numeric rule-based audit demonstration. Does not generate or verify ML-DSA signatures.",
            version="2.0.0-FRONTIER",
        )

        class TaskRequest(BaseModel):
            task_id: str = "TASK-2026-001"
            target_identifier: str = "TARGET-BIO-KEY"
            primary_metric: float = 28.5
            secondary_metric: float = 14.2
            status_descriptor: str = "DISCORDANT_ANOMALY"
            is_critical_flag: bool = True
            attributes: Dict[str, Any] = {}

        class ChatRequest(BaseModel):
            query: str

        def require_auth(authorization: str | None = Header(default=None)):
            token = os.getenv("API_BEARER_TOKEN", "")
            if len(token) < 32:
                raise HTTPException(status_code=503, detail="API authentication is not configured")
            if not authorization or not hmac.compare_digest(authorization, f"Bearer {token}"):
                raise HTTPException(status_code=401, detail="Invalid bearer token", headers={"WWW-Authenticate": "Bearer"})

        @app.get("/health")
        def health():
            return {"status": "HEALTHY", "system": "dilithium-pqc-sign-agent", "domain": "Post-Quantum Cryptography & Zero-Knowledge", "version": "2.0.0-FRONTIER"}

        @app.post("/api/audit", dependencies=[Depends(require_auth)])
        def api_audit(req: TaskRequest):
            payload = FrontierPayload(
                task_id=req.task_id,
                target_identifier=req.target_identifier,
                primary_metric=req.primary_metric,
                secondary_metric=req.secondary_metric,
                status_descriptor=req.status_descriptor,
                is_critical_flag=req.is_critical_flag,
                attributes=req.attributes,
            )
            return coordinator.process(payload)

        @app.post("/api/chat", dependencies=[Depends(require_auth)])
        def api_chat(req: ChatRequest):
            return {"response": coordinator.query_supervisory_chat(req.query)}

        return app
    except ImportError:
        return None
