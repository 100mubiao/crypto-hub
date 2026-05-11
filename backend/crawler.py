import asyncio
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
    "cardano", "polkadot", "near", "aptos", "sui",
    "internet-computer", "filecoin", "stellar", "arbitrum", "optimism",
]

COIN_META: dict[str, dict[str, Any]] = {
    "bitcoin": {"symbol": "BTC", "name": "Bitcoin", "chain": "Bitcoin"},
    "ethereum": {"symbol": "ETH", "name": "Ethereum", "chain": "Ethereum"},
    "solana": {"symbol": "SOL", "name": "Solana", "chain": "Solana"},
    "avalanche-2": {"symbol": "AVAX", "name": "Avalanche", "chain": "Avalanche"},
    "chainlink": {"symbol": "LINK", "name": "Chainlink", "chain": "Ethereum"},
    "dogwifcoin": {"symbol": "WIF", "name": "dogwifhat", "chain": "Solana"},
    "pepe": {"symbol": "PEPE", "name": "Pepe", "chain": "Ethereum"},
    "bonk": {"symbol": "BONK", "name": "Bonk", "chain": "Solana"},
    "render-token": {"symbol": "RENDER", "name": "Render", "chain": "Solana"},
    "mantra-dao": {"symbol": "OM", "name": "MANTRA", "chain": "Ethereum"},
    "cardano": {"symbol": "ADA", "name": "Cardano", "chain": "Cardano"},
    "polkadot": {"symbol": "DOT", "name": "Polkadot", "chain": "Polkadot"},
    "near": {"symbol": "NEAR", "name": "NEAR Protocol", "chain": "Near"},
    "aptos": {"symbol": "APT", "name": "Aptos", "chain": "Aptos"},
    "sui": {"symbol": "SUI", "name": "Sui", "chain": "Sui"},
    "internet-computer": {"symbol": "ICP", "name": "Internet Computer", "chain": "ICP"},
    "filecoin": {"symbol": "FIL", "name": "Filecoin", "chain": "Filecoin"},
    "stellar": {"symbol": "XLM", "name": "Stellar", "chain": "Stellar"},
    "arbitrum": {"symbol": "ARB", "name": "Arbitrum", "chain": "Arbitrum"},
    "optimism": {"symbol": "OP", "name": "Optimism", "chain": "Optimism"},
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

MAX_RETRIES = 3 if settings.coingecko_api_key else 1


async def fetch_json(url: str, retries: int = MAX_RETRIES) -> dict | list | None:
    last_error = None
    for attempt in range(retries):
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(url, headers=COINGECKO_HEADERS)
                if resp.status_code == 429:
                    retry_after = int(resp.headers.get("retry-after", "60"))
                    if attempt < retries - 1:
                        wait = min(retry_after * (attempt + 1), 30)
                        logger.warning("Rate limited (429). Retry %d/%d after %ss", attempt + 1, retries, wait)
                        await asyncio.sleep(wait)
                        continue
                    else:
                        logger.warning("Rate limited (429), exhausted retries. Skipping.")
                        return None
                resp.raise_for_status()
                return resp.json()
        except httpx.TimeoutException:
            logger.warning("Timeout fetching %s (attempt %d/%d)", url, attempt + 1, retries)
            if attempt < retries - 1:
                await asyncio.sleep(2 ** attempt)
            last_error = "timeout"
        except Exception as e:
            logger.warning("HTTP error fetching %s: %s (attempt %d/%d)", url, e, attempt + 1, retries)
            if attempt < retries - 1:
                await asyncio.sleep(2 ** attempt)
            last_error = str(e)
    logger.warning("All %d retries exhausted for %s: %s", retries, url, last_error)
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
        symbol = (meta.get("symbol") or item.get("symbol", "")).upper()
        name = meta.get("name") or item.get("name", "")
        chain = meta.get("chain") or CHAIN_PLATFORM_MAP.get(cid) or "Other"

        price = item.get("current_price") or 0.0
        change = item.get("price_change_percentage_24h") or 0.0
        volume = item.get("total_volume") or 0.0
        mcap = item.get("market_cap") or 0.0
        image = item.get("image") or ""

        is_new = False
        listing_dt = now
        atl_date = item.get("atl_date")
        if atl_date:
            try:
                listing_dt = datetime.datetime.fromisoformat(atl_date.replace("Z", "+00:00"))
                is_new = listing_dt > day_ago
            except (ValueError, TypeError):
                pass

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
    updated = 0
    created = 0
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
                updated += 1
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
                created += 1
        db.commit()
        logger.info("Market crawl done: %d updated, %d created (total %d)", updated, created, len(enriched))
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
                coin_symbol=(item.get("symbol", "") or "").upper(),
                coin_name=item.get("name", ""),
                coin_image=item.get("large") or item.get("thumb") or "",
                trend_type="heat" if i < 5 else "community",
                title=f"{item.get('name', 'Unknown')} trending #{i + 1}",
                score=round(score, 1),
                change=round(item.get("data", {}).get("price_change_percentage_24h", {}).get("usd", 0), 2),
                source="CoinGecko",
                keywords=item.get("data", {}).get("content", "")[:100].split() if item.get("data", {}).get("content") else [],
                timestamp=now,
            )
            db.add(trend)
        db.commit()
        logger.info("Trending crawl done: %d trends saved", min(len(coins_data), 15))
    finally:
        db.close()


def seed_initial_data():
    db = SessionLocal()
    try:
        if db.query(Coin).count() > 0:
            return
        now = datetime.datetime.now(datetime.timezone.utc)
        coins = [
            Coin(
                id=cid,
                symbol=meta["symbol"], name=meta["name"], image="",
                rank=i + 1, price=0.0, change_24h=0.0, volume=0.0, market_cap=0.0,
                turnover_rate=0.0, on_chain_activity=0.0, social_heat=0,
                listing_time=now, is_new=False, heat_score=0.0,
                risk_level="medium", chain=meta["chain"], holders=0,
                top_holder_percent=0.0, updated_at=now,
            )
            for i, (cid, meta) in enumerate(COIN_META.items())
        ]
        for c in coins:
            db.add(c)
        db.commit()
        logger.info("Seeded %d initial coins", len(coins))
    finally:
        db.close()


def seed_alerts():
    db = SessionLocal()
    try:
        if db.query(Alert).count() > 0:
            return
        now = datetime.datetime.now(datetime.timezone.utc)
        alerts = [
            Alert(
                id=str(uuid.uuid4()),
                coin_id="bitcoin", coin_symbol="BTC", coin_name="Bitcoin",
                event_type="policy", title="Bitcoin ETF Inflows Surge Past $500M",
                severity="high", description="Spot Bitcoin ETF recorded $520M in net inflows.",
                timestamp=now,
            ),
            Alert(
                id=str(uuid.uuid4()),
                coin_id="ethereum", coin_symbol="ETH", coin_name="Ethereum",
                event_type="upgrade", title="Ethereum Pectra Upgrade Successfully Deployed",
                severity="medium",
                description="The Pectra upgrade is now live on mainnet, introducing key scalability improvements.",
                timestamp=now,
            ),
            Alert(
                id=str(uuid.uuid4()),
                coin_id="solana", coin_symbol="SOL", coin_name="Solana",
                event_type="listing", title="Solana DeFi TVL Reaches New ATH",
                severity="medium", description="Solana DeFi total value locked surpasses $12B.",
                timestamp=now,
            ),
        ]
        for a in alerts:
            db.add(a)
        db.commit()
        logger.info("Seeded %d initial alerts", len(alerts))
    finally:
        db.close()
