from fastapi import APIRouter

from cards import audit
from cards.api.deps import SessionDep
from cards.schemas import AuditEventOut

router = APIRouter(prefix="/audit-events", tags=["audit"])


@router.get("", response_model=list[AuditEventOut])
def list_audit_events(
    session: SessionDep, entity_id: str | None = None, action: str | None = None
) -> list[AuditEventOut]:
    events = audit.list_events(session, entity_id=entity_id, action=action)
    return [AuditEventOut.model_validate(event) for event in events]
