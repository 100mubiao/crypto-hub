import datetime
import logging
import uuid
from typing import Any

import httpx

from backend.config import settings
from backend.database import SessionLocal
from backend.models import Coin, Trend, Alert

logger = logging.getLogger("crawler")

COINGECKO_HEADERS = {}
if settings.coingecko_api_key:
    COINGECKO_HEADERS["x-cg-demo-api-key"] = settings.coingecko_api_key

TOP_COINS = [
    "bitcoin", "ethereum", "solana", "avalanche-2", "chainlink",
    "dogwifcoin", "pepe", "bonk", "render-token", "mantra-dao",
]

COIN_META: dict[str, dict[str, Any]] = {
    "bitcoin": {"symbol": "BTC", "name": "Bitcoin", "chain": "Bitcoin", "listing": "2010-07-17T00:00:00Z"},
    "ethereum": {"symbol": "ETH", "name": "Ethereum", "chain": "Ethereum", "listing": "2015-07-30T00:00:00Z"},
    "solana": {"symbol": "SOL", "name": "Solana", "chain": "Solana", "listing": "2020-03-16T00:00:00Z"},
    "avalanche-2": {"symbol": "AVAX", "name": "Avalanche", "chain": "Avalanche", "listing": "2020-09-22T00:00:00Z"},
    "chainlink": {"symbol": "LINK", "name": "Chainlink", "chain": "Ethereum", "listing": "2017-09-21T00:00:00Z"},
    "dogwifcoin": {"symbol": "WIF", "name": "dogwifhat", "chain": "Solana", "listing": "2024-08-15T00:00:00Z"},
    "pepe": {"symbol": "PEPE", "name": "Pepe", "chain": "Ethereum", "listing": "2024-11-01T00:00:00Z"},
    "bonk": {"symbol": "BONK", "name": "Bonk", "chain": "Solana", "listing": "2024-06-20T00:00:00Z"},
    "render-token": {"symbol": "RENDER", "name": "Render", "chain": "Solana", "listing": "2022-03-15T00:00:00Z"},
    "mantra-dao": {"symbol": "OM", "name": "MANTRA", "chain": "Ethereum", "listing": "2021-06-10T00:00:00Z"},
}

CHAIN_PLATFORM_MAP = {
    "ethereum": "Ethereum",
    "solana": "Solana",
    "avalanche-2": "Avalanche",
    "binance-smart-chain": "BSC",
    "arbitrum": "Arbitrum",
    "polygon-pos": "Polygon",
    "base": "Base",
}


async def fetch_json(url: str) -> dict | list | None:
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, headers=COINGECKO_HEADERS)
            if resp.status_code == 429:
                retry_after = resp.headers.get("retry-after", "60")
                logger.warning("Rate limited (429). Retry after %ss. Skipping this cycle.", retry_after)
                return None
            resp.raise_for_status()
            return resp.json()
    except httpx.TimeoutException:
        logger.warning("Timeout fetching %s", url)
        return None
    except Exception as e:
        logger.warning("HTTP error fetching %s: %s", url, e)
        return None


def compute_risk_level(price_change: float, market_cap: float, is_new: bool) -> str:
    if is_new:
        return "high"
    if market_cap < 50_000_000:
        return "high"
    if abs(price_change) > 30:
        return "high"
    if market_cap < 1_000_000_000:
        return "medium"
    return "low"


def compute_heat_score(price_change: float, volume: float, market_cap: float) -> float:
    score = 5.0
    if abs(price_change) > 5:
        score += 1.5
    if abs(price_change) > 15:
        score += 1.0
    if market_cap > 0 and volume / market_cap > 0.3:
        score += 1.5
    if volume > 1_000_000_000:
        score += 1.0
    return min(10.0, max(0.0, score))


async def crawl_market_data():
    logger.info("Crawling market data from CoinGecko...")
    url = (
        f"{settings.coingecko_base_url}/coins/markets"
        f"?vs_currency=usd&order=market_cap_desc&per_page=50&page=1"
        f"&sparkline=false&price_change_percentage=24h"
    )
    data = await fetch_json(url)
    if not data or not isinstance(data, list):
        logger.warning("No market data received")
        return

    now = datetime.datetime.now(datetime.timezone.utc)
    day_ago = now - datetime.timedelta(days=1)

    enriched = []
    for item in data:
        cid: str = item.get("id", "")
        meta = COIN_META.get(cid, {})
        symbol = meta.get("symbol", item.get("symbol", "")).upper()
        name = meta.get("name", item.get("name", ""))
        chain = meta.get("chain", "Unknown")

        price = item.get("current_price") or 0.0
        change = item.get("price_change_percentage_24h") or 0.0
        volume = item.get("total_volume") or 0.0
        mcap = item.get("market_cap") or 0.0
        image = item.get("image") or ""

        is_new = False
        listing_str = meta.get("listing", "")
        if listing_str:
            listing_dt = datetime.datetime.fromisoformat(listing_str.replace("Z", "+00:00"))
            is_new = listing_dt > day_ago
        else:
            listing_dt = now

        holders = int(volume * 0.0001) if volume > 0 else 0

        heat = compute_heat_score(change, volume, mcap)
        risk = compute_risk_level(change, mcap, is_new)
        on_chain = volume * 0.04 if mcap > 0 else 0
        turnover = (volume / mcap * 100) if mcap > 0 else 0

        enriched.append({
            "id": cid, "symbol": symbol, "name": name, "image": image,
            "rank": item.get("market_cap_rank", 0),
            "price": price, "change_24h": round(change, 2),
            "volume": volume, "market_cap": mcap,
            "turnover_rate": round(turnover, 1),
            "on_chain_activity": round(on_chain),
            "social_heat": min(100, max(0, int(heat * 10))),
            "listing_time": listing_dt, "is_new": is_new,
            "heat_score": round(heat, 1), "risk_level": risk,
            "chain": chain, "holders": holders,
        })

    db = SessionLocal()
    try:
        for e in enriched:
            coin = db.query(Coin).filter(Coin.id == e["id"]).first()
            if coin:
                coin.price = e["price"]
                coin.change_24h = e["change_24h"]
                coin.volume = e["volume"]
                coin.market_cap = e["market_cap"]
                coin.turnover_rate = e["turnover_rate"]
                coin.on_chain_activity = e["on_chain_activity"]
                coin.social_heat = e["social_heat"]
                coin.is_new = e["is_new"]
                coin.heat_score = e["heat_score"]
                coin.risk_level = e["risk_level"]
                coin.holders = e["holders"]
                coin.updated_at = now
            else:
                coin = Coin(
                    id=e["id"], symbol=e["symbol"], name=e["name"],
                    image=e["image"], rank=e["rank"],
                    price=e["price"], change_24h=e["change_24h"],
                    volume=e["volume"], market_cap=e["market_cap"],
                    turnover_rate=e["turnover_rate"],
                    on_chain_activity=e["on_chain_activity"],
                    social_heat=e["social_heat"],
                    listing_time=e["listing_time"], is_new=e["is_new"],
                    heat_score=e["heat_score"], risk_level=e["risk_level"],
                    chain=e["chain"], holders=e["holders"],
                    top_holder_percent=0.0, updated_at=now,
                )
                db.add(coin)
        db.commit()
        logger.info("Saved %d coins", len(enriched))
    finally:
        db.close()


async def crawl_trending():
    logger.info("Crawling trending data...")
    url = f"{settings.coingecko_base_url}/search/trending"
    data = await fetch_json(url)
    if not data or not isinstance(data, dict):
        return

    coins_data = data.get("coins", [])
    db = SessionLocal()
    try:
        now = datetime.datetime.now(datetime.timezone.utc)
        db.query(Trend).delete()
        for i, entry in enumerate(coins_data[:15]):
            item = entry.get("item", {})
            cid = item.get("id", "")
            score = max(0, 10 - i * 0.6)
            trend = Trend(
                id=str(uuid.uuid4()),
                coin_id=cid,
                coin_symbol=item.get("symbol", "").upper(),
                coin_name=item.get("name", ""),
                coin_image=item.get("large", item.get("thumb", "")),
                trend_type="heat",
                title=f"{item.get('name', '')} trending on CoinGecko",
                score=round(score, 1),
                change=round((i % 5) * 3 - 2, 1),
                source="CoinGecko",
                keywords=["trending"],
                timestamp=now,
            )
            db.add(trend)
        db.commit()
        logger.info("Saved %d trending items", len(coins_data[:15]))
    finally:
        db.close()


def seed_alerts():
    db = SessionLocal()
    try:
        if db.query(Alert).count() > 0:
            return
        now = datetime.datetime.now(datetime.timezone.utc)
        alerts_data = [
            Alert(id=str(uuid.uuid4()), coin_id="pepe", coin_symbol="PEPE", coin_name="Pepe",
                   event_type="celebrity", title="Increased social mentions for PEPE",
                   severity="high", timestamp=now),
            Alert(id=str(uuid.uuid4()), coin_id="bitcoin", coin_symbol="BTC", coin_name="Bitcoin",
                   event_type="policy", title="BTC ETF inflows reach new monthly high",
                   severity="medium", timestamp=now),
            Alert(id=str(uuid.uuid4()), coin_id="solana", coin_symbol="SOL", coin_name="Solana",
                   event_type="upgrade", title="Solana network upgrade completed successfully",
                   severity="medium", timestamp=now),
            Alert(id=str(uuid.uuid4()), coin_id="ethereum", coin_symbol="ETH", coin_name="Ethereum",
                   event_type="funding", title="Ethereum L2 ecosystem TVL surpasses $50B",
                   severity="high", timestamp=now),
        ]
        for a in alerts_data:
            db.add(a)
        db.commit()
        logger.info("Seeded %d alerts", len(alerts_data))
    finally:
        db.close()


def seed_initial_data():
    """Populate DB with demo data so API serves results even without CoinGecko access."""
    db = SessionLocal()
    try:
        if db.query(Coin).count() > 0:
            return
        from backend.data_seed import DEMO_COINS, DEMO_TRENDS
        now = datetime.datetime.now(datetime.timezone.utc)
        for item in DEMO_COINS:
            coin = Coin(
                id=item["id"], symbol=item["symbol"], name=item["name"],
                image=item.get("image", ""), rank=item.get("rank", 0),
                price=item.get("price", 0.0), change_24h=item.get("change_24h", 0.0),
                volume=item.get("volume", 0.0), market_cap=item.get("market_cap", 0.0),
                turnover_rate=item.get("turnover_rate", 0.0),
                on_chain_activity=item.get("on_chain_activity", 0.0),
                social_heat=item.get("social_heat", 0.0),
                listing_time=now - datetime.timedelta(days=item.get("days_ago", 365)),
                is_new=item.get("is_new", False),
                heat_score=item.get("heat_score", 5.0),
                risk_level=item.get("risk_level", "medium"),
                chain=item.get("chain", "Unknown"),
                holders=item.get("holders", 0),
                top_holder_percent=item.get("top_holder_percent", 0.0),
            )
            db.add(coin)

        for item in DEMO_TRENDS:
            trend = Trend(
                id=str(uuid.uuid4()), coin_id=item["coin_id"],
                coin_symbol=item["coin_symbol"], coin_name=item["coin_name"],
                coin_image="", trend_type=item.get("type", "heat"),
                title=item.get("title", ""), score=item.get("score", 5.0),
                change=item.get("change", 0.0), source=item.get("source", ""),
                keywords=item.get("keywords", []), timestamp=now,
            )
            db.add(trend)

        db.commit()
        logger.info("Seeded %d coins and %d trends", len(DEMO_COINS), len(DEMO_TRENDS))
    finally:
        db.close()
