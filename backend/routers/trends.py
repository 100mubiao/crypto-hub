from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Trend
from backend.schemas import TrendOut

router = APIRouter(prefix="/api/v1", tags=["trends"])


@router.get("/trends", response_model=list[TrendOut])
def list_trends(
    type: str | None = Query(None),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    q = db.query(Trend)
    if type:
        q = q.filter(Trend.trend_type == type)
    return q.order_by(Trend.score.desc()).limit(limit).all()
