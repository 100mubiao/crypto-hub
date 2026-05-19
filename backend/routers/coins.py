import datetime
import logging

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.config import settings
from backend.database import get_db
from backend.models import Coin
from backend.schemas import CoinOut, MarketOverview, OhlcPoint

logger = logging.getLogger("coins")

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


@router.get("/coins/{coin_id}/chart", response_model=list[OhlcPoint])
async def get_coin_chart(coin_id: str, days: int = Query(7, ge=1, le=365)):
    url = (
        f"{settings.coingecko_base_url}/coins/{coin_id}/ohlc"
        f"?vs_currency=usd&days={days}"
    )
    headers = {}
    if settings.coingecko_api_key:
        headers["x-cg-demo-api-key"] = settings.coingecko_api_key

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 429:
                logger.warning("CoinGecko rate limited on chart data for %s", coin_id)
                raise HTTPException(429, "Rate limited. Try again later.")
            if resp.status_code == 404:
                raise HTTPException(404, f"Coin '{coin_id}' not found on CoinGecko")
            resp.raise_for_status()
            data: list = resp.json()
    except httpx.TimeoutException:
        raise HTTPException(504, "CoinGecko timeout")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Chart fetch error for %s: %s", coin_id, e)
        raise HTTPException(502, "Failed to fetch chart data")

    if not data or not isinstance(data, list):
        return []

    return [
        OhlcPoint(
            time=pt[0] // 1000,  # CoinGecko returns ms, convert to seconds
            open=pt[1],
            high=pt[2],
            low=pt[3],
            close=pt[4],
        )
        for pt in data
    ]
