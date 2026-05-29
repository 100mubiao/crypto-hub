import datetime
import json
import logging
import uuid

import httpx
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


# ─── PayPal ────────────────────────────────────────────────────────────────

PAYPAL_API_BASE_SANDBOX = "https://api-m.sandbox.paypal.com"
PAYPAL_API_BASE_LIVE = "https://api-m.paypal.com"


def _paypal_base() -> str:
    return PAYPAL_API_BASE_SANDBOX if settings.paypal_sandbox else PAYPAL_API_BASE_LIVE


async def _paypal_get_access_token() -> str:
    if not settings.paypal_client_id or not settings.paypal_client_secret:
        raise HTTPException(status_code=500, detail="PayPal not configured")
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{_paypal_base()}/v1/oauth2/token",
            headers={"Accept": "application/json"},
            data={"grant_type": "client_credentials"},
            auth=(settings.paypal_client_id, settings.paypal_client_secret),
            timeout=15,
        )
    if resp.status_code != 200:
        logger.error("PayPal OAuth error: %s", resp.text)
        raise HTTPException(status_code=502, detail="PayPal auth failed")
    return resp.json()["access_token"]


def _paypal_product_name(plan: str) -> str:
    info = PRICING.get(plan)
    return f"CryptoHub {info['label']}" if info else "CryptoHub Premium"


@router.get("/paypal/client-id")
def paypal_client_id():
    return {"client_id": settings.paypal_client_id or ""}


@router.post("/paypal/create-order")
async def paypal_create_order(
    body: dict,
    user: User = Depends(get_current_user),
):
    plan = body.get("plan")
    if plan not in PRICING:
        raise HTTPException(status_code=400, detail="Invalid plan")

    info = PRICING[plan]
    amount = f"{info['amount_cents'] / 100:.2f}"

    token = await _paypal_get_access_token()
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{_paypal_base()}/v2/checkout/orders",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
                "PayPal-Request-Id": str(uuid.uuid4()),
            },
            json={
                "intent": "CAPTURE",
                "purchase_units": [{
                    "reference_id": plan,
                    "description": _paypal_product_name(plan),
                    "amount": {"currency_code": "USD", "value": amount},
                    "custom_id": f"{user.email}:{plan}",
                }],
                "payment_source": {
                    "paypal": {
                        "experience_context": {
                            "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED",
                            "landing_page": "LOGIN",
                            "user_action": "PAY_NOW",
                            "return_url": f"{settings.frontend_url}/checkout/{plan.replace('_', ' ').title()}?paypal=success",
                            "cancel_url": f"{settings.frontend_url}/checkout/{plan.replace('_', ' ').title()}?canceled=true",
                        }
                    }
                },
            },
            timeout=15,
        )
    if resp.status_code not in (200, 201):
        logger.error("PayPal create-order error: %s", resp.text)
        raise HTTPException(status_code=502, detail="PayPal order creation failed")

    data = resp.json()
    return {
        "order_id": data["id"],
        "status": data["status"],
    }


@router.post("/paypal/capture-order")
async def paypal_capture_order(
    body: dict,
    user: User = Depends(get_current_user),
):
    order_id = body.get("order_id")
    if not order_id:
        raise HTTPException(status_code=400, detail="Missing order_id")

    token = await _paypal_get_access_token()
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{_paypal_base()}/v2/checkout/orders/{order_id}/capture",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
            timeout=15,
        )
    if resp.status_code not in (200, 201):
        logger.error("PayPal capture-order error: %s", resp.text)
        raise HTTPException(status_code=502, detail="PayPal capture failed")

    data = resp.json()
    if data.get("status") != "COMPLETED":
        logger.warning("PayPal capture not completed: %s", data.get("status"))
        raise HTTPException(status_code=400, detail="Payment not completed")

    custom_id = ""
    for unit in data.get("purchase_units", []):
        custom_id = unit.get("custom_id", "")
        break

    parts = custom_id.split(":")
    paypal_email = parts[0] if len(parts) == 2 else ""
    plan = parts[1] if len(parts) == 2 else "premium_monthly"

    if paypal_email and paypal_email != user.email:
        raise HTTPException(status_code=403, detail="Payment email mismatch")

    db = next(get_db())
    try:
        db_user = db.query(User).filter(User.email == user.email).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        if plan == "premium_monthly":
            db_user.membership = "premium"
            db_user.membership_expiry = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30)
        elif plan == "lifetime":
            db_user.membership = "lifetime"
            db_user.membership_expiry = datetime.datetime(2099, 12, 31, tzinfo=datetime.timezone.utc)
        else:
            raise HTTPException(status_code=400, detail="Invalid plan")
        db.commit()
        logger.info("User %s upgraded to %s via PayPal (order %s)", user.email, plan, order_id)
    finally:
        db.close()

    return {
        "membership": db_user.membership,
        "membership_expiry": db_user.membership_expiry.isoformat() if db_user.membership_expiry else None,
    }


@router.post("/paypal/webhook")
async def paypal_webhook(request: Request):
    if not settings.paypal_webhook_id:
        logger.warning("PayPal webhook ID not configured")
        raise HTTPException(status_code=500, detail="Webhook not configured")

    payload = await request.body()
    headers_dict = dict(request.headers)
    transmission_id = headers_dict.get("paypal-transmission-id", "")
    transmission_sig = headers_dict.get("paypal-transmission-sig", "")
    cert_url = headers_dict.get("paypal-cert-url", "")
    auth_algo = headers_dict.get("paypal-auth-algo", "")
    webhook_id = settings.paypal_webhook_id

    token = await _paypal_get_access_token()
    async with httpx.AsyncClient() as client:
        verify_resp = await client.post(
            f"{_paypal_base()}/v1/notifications/verify-webhook-signature",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
            json={
                "auth_algo": auth_algo,
                "cert_url": cert_url,
                "transmission_id": transmission_id,
                "transmission_sig": transmission_sig,
                "webhook_id": webhook_id,
                "webhook_event": json.loads(payload.decode()),
            },
            timeout=15,
        )
    if verify_resp.status_code != 200:
        logger.error("PayPal webhook verification failed: %s", verify_resp.text)
        raise HTTPException(status_code=400, detail="Webhook verification failed")

    verification_status = verify_resp.json().get("verification_status")
    if verification_status != "SUCCESS":
        logger.warning("PayPal webhook verification status: %s", verification_status)
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    event = json.loads(payload.decode())
    event_type = event.get("event_type", "")

    if event_type == "CHECKOUT.ORDER.APPROVED":
        logger.info("PayPal order approved: %s", event.get("resource", {}).get("id"))
    elif event_type == "PAYMENT.CAPTURE.COMPLETED":
        resource = event.get("resource", {})
        custom_id = resource.get("custom_id", "")
        parts = custom_id.split(":")
        email = parts[0] if len(parts) == 2 else ""
        plan = parts[1] if len(parts) == 2 else "premium_monthly"
        if email and plan in PRICING:
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
                    logger.info("User %s upgraded to %s via PayPal webhook", email, plan)
            finally:
                db.close()

    return {"status": "ok"}
