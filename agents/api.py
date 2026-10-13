"""FastAPI endpoints for TBscore II and the optional legacy audit demonstration."""
import hmac
import os
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from tb_score_ii import calculate_metrics
from .base import AuditLogger, SecurityException
from .models import SystemTaskPayload
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")
app = FastAPI(
    title="TBscore II Clinical Severity API",
    description="Published clinical score plus a separate legacy demo agent endpoint.",
    version="4.0.0",
)


class ScoreRequest(BaseModel):
    cough: bool
    dyspnea: bool
    chest_pain: bool
    anemia: bool
    bmi: float = Field(gt=0, le=100, allow_inf_nan=False)
    muac_mm: float = Field(gt=0, le=1000, allow_inf_nan=False)


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "ok", "service": "tb-score-ii-clinical-severity", "version": "4.0.0"}


@app.post("/api/score")
def api_score(payload: ScoreRequest):
    """Deterministic published 0–8 TBscore II; no identifiers are accepted."""
    return calculate_metrics(**payload.model_dump())


@app.get("/metrics")
def metrics():
    return {"dossiers_processed_total": len(supervisor.dossier_registry),
            "audit_blocks_total": len(AuditLogger.get_trail())}


@app.post("/api/audit", deprecated=True)
def api_audit(payload: SystemTaskPayload):
    """Legacy demonstration; generic metrics are not TBscore II inputs."""
    try:
        return supervisor.process_task(payload).to_dict()
    except SecurityException as exc:
        raise HTTPException(status_code=422, detail="Identifier rejected by input filter") from exc


@app.post("/api/chat", deprecated=True)
def api_chat(req: ChatRequest):
    try:
        return {"response": supervisor.query_supervisory_chat(req.query)}
    except SecurityException as exc:
        raise HTTPException(status_code=422, detail="Input rejected by identifier filter") from exc


@app.get("/api/audit/logs")
def api_audit_logs(x_audit_token: str | None = Header(default=None)):
    """Audit metadata requires a configured token; it contains no case payloads."""
    expected = os.environ.get("AUDIT_READ_TOKEN")
    if not expected or not x_audit_token or not hmac.compare_digest(x_audit_token, expected):
        raise HTTPException(status_code=403, detail="Audit access disabled or unauthorized")
    return {"audit_trail": AuditLogger.get_trail(),
            "verified": AuditLogger.verify_integrity()}


# The same local-only browser UI works from FastAPI and from GitHub Pages.
app.mount("/", StaticFiles(directory=Path(__file__).resolve().parent.parent / "web",
                           html=True), name="web")
