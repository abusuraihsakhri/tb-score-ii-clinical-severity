"""Security and API regressions for the published-score service."""
import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from agents.api import ScoreRequest, api_score, api_audit_logs
from agents.base import AuditTrail


def test_api_matches_published_score():
    data = ScoreRequest(cough=True, dyspnea=False, chest_pain=True, anemia=False,
                        bmi=15.9, muac_mm=199)
    assert api_score(data)["score"] == 6
    assert api_score(data)["severity_class"] == "III"


@pytest.mark.parametrize("invalid", [float("nan"), float("inf"), -1.0, 0.0])
def test_api_rejects_invalid_bmi(invalid):
    with pytest.raises(ValidationError):
        ScoreRequest(cough=False, dyspnea=False, chest_pain=False, anemia=False,
                     bmi=invalid, muac_mm=220)


def test_audit_hmac_detects_record_changes():
    trail = AuditTrail(secret_key="regression-test-key")
    trail.log("tester", "operator", "CASE", {"count": 1})
    trail.log("tester", "operator", "NEXT", {"count": 2})
    assert trail.verify_integrity()
    copy = trail.get_trail()
    copy[0]["event_type"] = "TAMPERED"
    assert trail.verify_integrity()  # immutable snapshot
    original = trail.logs[0]["event_type"]
    trail.logs[0]["event_type"] = "TAMPERED"
    assert not trail.verify_integrity()
    trail.logs[0]["event_type"] = original
    assert trail.verify_integrity()


def test_audit_api_denies_anonymous_or_unconfigured(monkeypatch):
    monkeypatch.delenv("AUDIT_READ_TOKEN", raising=False)
    with pytest.raises(HTTPException) as exc:
        api_audit_logs(x_audit_token=None)
    assert exc.value.status_code == 403
    monkeypatch.setenv("AUDIT_READ_TOKEN", "example-only-token")
    with pytest.raises(HTTPException):
        api_audit_logs(x_audit_token="wrong")
    assert isinstance(api_audit_logs(x_audit_token="example-only-token")["audit_trail"], list)
