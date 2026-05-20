import datetime
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db
from backend.models import User
from backend.schemas import UserRegister, UserLogin, TokenOut, UserOut, ThemeUpdate, PurchaseRequest

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer = HTTPBearer()

JWT_SECRET = getattr(settings, "jwt_secret", "cryptohub-dev-secret-key-change-in-prod")
JWT_ALGO = "HS256"
JWT_EXPIRE_DAYS = 30

PRICING = {
    "premium_monthly": 0.99,
    "lifetime": 9.9,
}


def make_token(email: str) -> str:
    payload = {
        "sub": email,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=JWT_EXPIRE_DAYS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


def get_current_user(
    cred: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(cred.credentials, JWT_SECRET, algorithms=[JWT_ALGO])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.post("/register", response_model=TokenOut)
def register(body: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        id=str(uuid.uuid4()),
        email=body.email,
        name=body.name,
        password_hash=pwd.hash(body.password),
        membership="free",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = make_token(user.email)
    return TokenOut(access_token=token, email=user.email, name=user.name, membership=user.membership)


@router.post("/login", response_model=TokenOut)
def login(body: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not pwd.verify(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = make_token(user.email)
    return TokenOut(access_token=token, email=user.email, name=user.name, membership=user.membership)


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
