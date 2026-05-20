import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, JSON
from backend.database import Base


class Coin(Base):
    __tablename__ = "coins"

    id = Column(String, primary_key=True)
    symbol = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    image = Column(Text, default="")
    rank = Column(Integer, default=0)
    price = Column(Float, default=0.0)
    change_24h = Column(Float, default=0.0)
    volume = Column(Float, default=0.0)
    market_cap = Column(Float, default=0.0)
    turnover_rate = Column(Float, default=0.0)
    on_chain_activity = Column(Float, default=0.0)
    social_heat = Column(Float, default=0.0)
    listing_time = Column(DateTime, default=datetime.datetime.utcnow)
    is_new = Column(Boolean, default=False)
    heat_score = Column(Float, default=0.0)
    risk_level = Column(String, default="medium")
    chain = Column(String, default="")
    holders = Column(Integer, default=0)
    top_holder_percent = Column(Float, default=0.0)
    description = Column(Text, default="")
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class Trend(Base):
    __tablename__ = "trends"

    id = Column(String, primary_key=True)
    coin_id = Column(String, nullable=False, index=True)
    coin_symbol = Column(String, nullable=False)
    coin_name = Column(String, nullable=False)
    coin_image = Column(Text, default="")
    trend_type = Column(String, nullable=False)  # heat, media, community, event
    title = Column(Text, nullable=False)
    score = Column(Float, default=0.0)
    change = Column(Float, default=0.0)
    source = Column(String, default="")
    keywords = Column(JSON, default=list)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True)
    coin_id = Column(String, nullable=False, index=True)
    coin_symbol = Column(String, nullable=False)
    coin_name = Column(String, nullable=False)
    event_type = Column(String, nullable=False)  # listing, funding, upgrade, celebrity, policy
    title = Column(Text, nullable=False)
    severity = Column(String, default="medium")
    description = Column(Text, default="")
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    membership = Column(String, default="free")
    membership_expiry = Column(DateTime, nullable=True)
    theme = Column(String, default="default")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
