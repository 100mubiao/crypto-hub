from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Alert
from backend.schemas import AlertOut

router = APIRouter(prefix="/api/v1", tags=["alerts"])


@router.get("/alerts", response_model=list[AlertOut])
def list_alerts(
    severity: str | None = Query(None),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    q = db.query(Alert)
    if severity:
        q = q.filter(Alert.severity == severity)
    return q.order_by(Alert.timestamp.desc()).limit(limit).all()
