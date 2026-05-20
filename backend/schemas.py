import datetime
from pydantic import BaseModel, field_serializer, Field


class CoinOut(BaseModel):
    id: str
    symbol: str
    name: str
    image: str
    rank: int
    price: float
    change_24h: float
    volume: float
    market_cap: float
    turnover_rate: float
    on_chain_activity: float
    social_heat: float
    listing_time: datetime.datetime
    is_new: bool
    heat_score: float
    risk_level: str
    chain: str
    holders: int
    top_holder_percent: float
    description: str

    @field_serializer("listing_time")
    def serialize_dt(self, v: datetime.datetime) -> str:
        return v.isoformat()

    class Config:
        from_attributes = True


class TrendOut(BaseModel):
    id: str
    coin_id: str
    coin_symbol: str
    coin_name: str
    coin_image: str
    type: str = Field(validation_alias="trend_type")
    title: str
    score: float
    change: float
    source: str
    keywords: list[str]
    timestamp: datetime.datetime

    @field_serializer("timestamp")
    def serialize_dt(self, v: datetime.datetime) -> str:
        return v.isoformat()

    class Config:
        from_attributes = True
        populate_by_name = True


class AlertOut(BaseModel):
    id: str
    coin_id: str
    coin_symbol: str
    coin_name: str
    type: str = Field(validation_alias="event_type")
    title: str
    severity: str
    description: str
    timestamp: datetime.datetime

    @field_serializer("timestamp")
    def serialize_dt(self, v: datetime.datetime) -> str:
        return v.isoformat()

    class Config:
        from_attributes = True
        populate_by_name = True


class OhlcPoint(BaseModel):
    time: float  # unix seconds
    open: float
    high: float
    low: float
    close: float


class MarketOverview(BaseModel):
    total_market_cap: float
    total_volume_24h: float
    btc_dominance: float
    new_coins_24h: int
    updated_at: str


class UserRegister(BaseModel):
    email: str
    name: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    email: str
    name: str
    membership: str


class UserOut(BaseModel):
    id: str
    email: str
    name: str
    membership: str
    membership_expiry: datetime.datetime | None = None
    theme: str = "default"

    class Config:
        from_attributes = True


class ThemeUpdate(BaseModel):
    theme: str


class PurchaseRequest(BaseModel):
    plan: str
