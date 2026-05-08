import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.database import get_db
from backend.models import Coin
from backend.schemas import CoinOut, MarketOverview

router = APIRouter(prefix="/api/v1", tags=["coins"])


@router.get("/coins", response_model=list[CoinOut])
def list_coins(
    symbol: str | None = Query(None),
    chain: str | None = Query(None),
    sort_by: str = Query("rank"),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(Coin)
    if symbol:
        q = q.filter(Coin.symbol.ilike(f"%{symbol}%"))
    if chain:
        q = q.filter(Coin.chain.ilike(f"%{chain}%"))

    sort_map = {
        "rank": Coin.rank,
        "price": Coin.price,
        "volume": Coin.volume,
        "change": Coin.change_24h,
        "heat": Coin.heat_score,
    }
    order_col = sort_map.get(sort_by, Coin.rank)
    q = q.order_by(order_col).limit(limit)

    return q.all()


@router.get("/coins/{coin_id}", response_model=CoinOut)
def get_coin(coin_id: str, db: Session = Depends(get_db)):
    coin = db.query(Coin).filter(Coin.id == coin_id).first()
    if not coin:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Coin not found")
    return coin


@router.get("/market/overview", response_model=MarketOverview)
def market_overview(db: Session = Depends(get_db)):
    coins = db.query(Coin).all()
    total_mcap = sum(c.market_cap for c in coins)
    total_vol = sum(c.volume for c in coins)
    btc = db.query(Coin).filter(Coin.id == "bitcoin").first()
    btc_dom = (btc.market_cap / total_mcap * 100) if btc and total_mcap > 0 else 0

    day_ago = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)
    new_count = db.query(Coin).filter(Coin.listing_time > day_ago).count()

    return MarketOverview(
        total_market_cap=total_mcap,
        total_volume_24h=total_vol,
        btc_dominance=round(btc_dom, 1),
        new_coins_24h=new_count,
        updated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    )


@router.get("/new-coins", response_model=list[CoinOut])
def new_coins(db: Session = Depends(get_db)):
    day_ago = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)
    return (
        db.query(Coin)
        .filter(Coin.listing_time > day_ago)
        .order_by(Coin.listing_time.desc())
        .all()
    )
