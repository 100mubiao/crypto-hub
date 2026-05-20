import datetime
import time
import uuid
from threading import Lock

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db
from backend.models import User, PasswordReset
from backend.schemas import UserRegister, UserLogin, TokenOut, UserOut, ThemeUpdate, PurchaseRequest, ForgotPasswordRequest, ResetPasswordRequest
from backend.email_utils import send_reset_email

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer = HTTPBearer()

JWT_ALGO = "HS256"

PRICING = {
    "premium_monthly": 0.99,
    "lifetime": 9.9,
}

# --- In-memory rate limiter ---
_rate_limit_store: dict[str, list[float]] = {}
_rate_limit_lock = Lock()


def _check_rate_limit(key: str, max_per_minute: int) -> None:
    now = time.time()
    window = 60.0
    with _rate_limit_lock:
        timestamps = _rate_limit_store.get(key, [])
        timestamps = [t for t in timestamps if now - t < window]
        if len(timestamps) >= max_per_minute:
            raise HTTPException(status_code=429, detail="Too many requests. Try again later.")
        timestamps.append(now)
        _rate_limit_store[key] = timestamps


def _get_jwt_secret() -> str:
    secret = settings.jwt_secret
    if not secret:
        raise RuntimeError("JWT_SECRET environment variable is not set")
    if secret == "cryptohub-dev-secret-key-change-in-prod":
        raise RuntimeError("JWT_SECRET must be changed from the default value")
    return secret


def _validate_password(password: str) -> None:
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if not any(c.isupper() for c in password):
        raise HTTPException(status_code=400, detail="Password must contain an uppercase letter")
    if not any(c.islower() for c in password):
        raise HTTPException(status_code=400, detail="Password must contain a lowercase letter")
    if not any(c.isdigit() for c in password):
        raise HTTPException(status_code=400, detail="Password must contain a digit")


def make_access_token(email: str, token_version: int) -> str:
    secret = _get_jwt_secret()
    payload = {
        "sub": email,
        "ver": token_version,
        "type": "access",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(payload, secret, algorithm=JWT_ALGO)


def make_refresh_token(email: str, token_version: int) -> str:
    secret = _get_jwt_secret()
    payload = {
        "sub": email,
        "ver": token_version,
        "type": "refresh",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=settings.refresh_token_expire_days),
    }
    return jwt.encode(payload, secret, algorithm=JWT_ALGO)


def get_current_user(
    cred: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    secret = _get_jwt_secret()
    try:
        payload = jwt.decode(cred.credentials, secret, algorithms=[JWT_ALGO])
        email = payload.get("sub")
        token_type = payload.get("type")
        token_ver = payload.get("ver")
        if not email or token_type != "access":
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if user.token_version != token_ver:
        raise HTTPException(status_code=401, detail="Token revoked. Please log in again.")
    return user


@router.post("/register", response_model=TokenOut)
def register(body: UserRegister, request: Request, db: Session = Depends(get_db)):
    _check_rate_limit(f"register:{request.client.host}", settings.login_rate_limit_per_minute)
    _validate_password(body.password)

    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        id=str(uuid.uuid4()),
        email=body.email,
        name=body.name,
        password_hash=pwd.hash(body.password, rounds=settings.bcrypt_rounds),
        membership="free",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    access_token = make_access_token(user.email, user.token_version)
    refresh_token = make_refresh_token(user.email, user.token_version)
    return TokenOut(
        access_token=access_token,
        refresh_token=refresh_token,
        email=user.email,
        name=user.name,
        membership=user.membership,
    )


@router.post("/login", response_model=TokenOut)
def login(body: UserLogin, request: Request, db: Session = Depends(get_db)):
    _check_rate_limit(f"login:{request.client.host}", settings.login_rate_limit_per_minute)

    user = db.query(User).filter(User.email == body.email).first()
    if not user or not pwd.verify(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = make_access_token(user.email, user.token_version)
    refresh_token = make_refresh_token(user.email, user.token_version)
    return TokenOut(
        access_token=access_token,
        refresh_token=refresh_token,
        email=user.email,
        name=user.name,
        membership=user.membership,
    )


@router.post("/refresh")
def refresh_token(cred: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    secret = _get_jwt_secret()
    try:
        payload = jwt.decode(cred.credentials, secret, algorithms=[JWT_ALGO])
        email = payload.get("sub")
        token_type = payload.get("type")
        token_ver = payload.get("ver")
        if not email or token_type != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = db.query(User).filter(User.email == email).first()
    if not user or user.token_version != token_ver:
        raise HTTPException(status_code=401, detail="Token revoked")

    access_token = make_access_token(user.email, user.token_version)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/forgot-password")
async def forgot_password(body: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user:
        return {"message": "If that email is registered, a reset link has been sent"}

    db.query(PasswordReset).filter(PasswordReset.email == body.email, PasswordReset.used == False).update({"used": True})
    db.commit()

    token = str(uuid.uuid4())
    expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    reset = PasswordReset(
        id=str(uuid.uuid4()),
        email=body.email,
        token=token,
        expires_at=expires,
    )
    db.add(reset)
    db.commit()

    reset_link = f"{settings.app_url}/reset-password?token={token}"
    await send_reset_email(body.email, reset_link)
    return {"message": "If that email is registered, a reset link has been sent"}


@router.post("/reset-password")
def reset_password(body: ResetPasswordRequest, db: Session = Depends(get_db)):
    _validate_password(body.password)
    now = datetime.datetime.now(datetime.timezone.utc)

    reset = (
        db.query(PasswordReset)
        .filter(
            PasswordReset.token == body.token,
            PasswordReset.used == False,
            PasswordReset.expires_at > now,
        )
        .first()
    )
    if not reset:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user = db.query(User).filter(User.email == reset.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    user.password_hash = pwd.hash(body.password, rounds=settings.bcrypt_rounds)
    user.token_version += 1
    reset.used = True
    db.commit()

    return {"message": "Password reset successful"}


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@router.post("/purchase")
def purchase(body: PurchaseRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plan = body.plan
    if plan not in PRICING:
        raise HTTPException(status_code=400, detail="Invalid plan")
    if plan == "premium_monthly":
        user.membership = "premium"
        user.membership_expiry = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30)
    elif plan == "lifetime":
        user.membership = "lifetime"
        user.membership_expiry = None
    db.commit()
    return {"message": "Purchase successful", "membership": user.membership}


@router.put("/theme")
def update_theme(body: ThemeUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.membership not in ("premium", "lifetime"):
        raise HTTPException(status_code=403, detail="Premium membership required")
    user.theme = body.theme
    db.commit()
    return {"theme": user.theme}
