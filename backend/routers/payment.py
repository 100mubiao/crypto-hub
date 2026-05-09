import datetime
import logging

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db
from backend.models import User

logger = logging.getLogger("payment")
bearer = HTTPBearer()

PRICING = {
    "premium_monthly": {"amount_cents": 99, "label": "Premium Monthly"},
    "lifetime": {"amount_cents": 990, "label": "Lifetime"},
}

router = APIRouter(prefix="/api/v1/payment", tags=["payment"])


def get_current_user(
    cred: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    from jose import jwt, JWTError
    JWT_SECRET = getattr(settings, "jwt_secret", "cryptohub-dev-secret-key-change-in-prod")
    try:
        payload = jwt.decode(cred.credentials, JWT_SECRET, algorithms=["HS256"])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.post("/create-checkout-session")
def create_checkout_session(
    body: dict,
    user: User = Depends(get_current_user),
):
    plan = body.get("plan")
    if plan not in PRICING:
        raise HTTPException(status_code=400, detail="Invalid plan")

    if not settings.stripe_secret_key:
        raise HTTPException(status_code=500, detail="Stripe not configured")

    stripe.api_key = settings.stripe_secret_key
    plan_info = PRICING[plan]

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": f"CryptoHub {plan_info['label']}"},
                    "unit_amount": plan_info["amount_cents"],
                },
                "quantity": 1,
            }],
            metadata={
                "user_email": user.email,
                "plan": plan,
            },
            success_url=f"{settings.frontend_url}/checkout/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.frontend_url}/checkout/{plan}?canceled=true",
        )
        return {"url": session.url}
    except stripe.StripeError as e:
        logger.error("Stripe error: %s", e)
        raise HTTPException(status_code=500, detail="Payment service error")


@router.post("/webhook")
async def stripe_webhook(request: Request):
    if not settings.stripe_webhook_secret:
        logger.warning("Stripe webhook secret not configured")
        raise HTTPException(status_code=500, detail="Webhook not configured")

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing stripe-signature")

    stripe.api_key = settings.stripe_secret_key
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_secret)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        email = session.get("metadata", {}).get("user_email")
        plan = session.get("metadata", {}).get("plan")
        if email and plan:
            db = next(get_db())
            try:
                user = db.query(User).filter(User.email == email).first()
                if user:
                    if plan == "premium_monthly":
                        user.membership = "premium"
                        user.membership_expiry = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30)
                    elif plan == "lifetime":
                        user.membership = "lifetime"
                        user.membership_expiry = datetime.datetime(2099, 12, 31, tzinfo=datetime.timezone.utc)
                    db.commit()
                    logger.info("User %s upgraded to %s via Stripe", email, plan)
            finally:
                db.close()

    return {"status": "ok"}


@router.get("/success")
def payment_success(session_id: str, user: User = Depends(get_current_user)):
    db = next(get_db())
    try:
        db_user = db.query(User).filter(User.email == user.email).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "membership": db_user.membership,
            "membership_expiry": db_user.membership_expiry.isoformat() if db_user.membership_expiry else None,
        }
    finally:
        db.close()
