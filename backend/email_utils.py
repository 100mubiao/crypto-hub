import logging
import httpx

from backend.config import settings

logger = logging.getLogger("email")

RESEND_API = "https://api.resend.com"
FROM_ADDRESS = "CryptoHub <noreply@cryptohub.dpdns.org>"


async def send_reset_email(to_email: str, reset_link: str) -> bool:
    if not settings.resend_api_key:
        logger.warning("RESEND_API_KEY not set, skipping email to %s", to_email)
        return False

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{RESEND_API}/emails",
                headers={
                    "Authorization": f"Bearer {settings.resend_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": FROM_ADDRESS,
                    "to": [to_email],
                    "subject": "Reset your CryptoHub password",
                    "html": f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#0f0f1a;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:40px 16px">
<table width="480" cellpadding="0" cellspacing="0" style="background:#1a1a2e;border-radius:12px;overflow:hidden">
<tr><td style="padding:32px">
<div style="text-align:center;margin-bottom:24px">
<div style="width:48px;height:48px;background:#00c897;border-radius:12px;display:inline-flex;align-items:center;justify-content:center;font-size:20px;font-weight:bold;color:#0f0f1a">C</div>
<h1 style="color:#00c897;font-size:22px;margin:12px 0 4px">CryptoHub</h1>
<p style="color:#6c6ca0;font-size:13px;margin:0">Password Reset Request</p>
</div>
<p style="color:#e0e0e8;font-size:14px;line-height:1.6;margin:0 0 20px">We received a request to reset your CryptoHub password. Click the button below to choose a new password. This link expires in 1 hour.</p>
<a href="{reset_link}" style="display:inline-block;background:#00c897;color:#0f0f1a;font-weight:600;padding:12px 32px;border-radius:8px;text-decoration:none;font-size:14px">Reset Password</a>
<p style="color:#6c6ca0;font-size:12px;line-height:1.5;margin:20px 0 0">If you didn't request this, you can safely ignore this email. Your password won't change unless you click the link above.</p>
</td></tr>
<tr><td style="background:#252542;padding:16px 32px;text-align:center">
<p style="color:#6c6ca0;font-size:11px;margin:0">CryptoHub &bull; Real-time Crypto Data Aggregation</p>
</td></tr>
</table>
</td></tr></table>
</body>
</html>""",
                },
            )
            if resp.is_success:
                logger.info("Reset email sent to %s (id=%s)", to_email, resp.json().get("id"))
                return True
            logger.error("Resend API error for %s: %s %s", to_email, resp.status_code, resp.text)
            return False
    except Exception as e:
        logger.error("Failed to send reset email to %s: %s", to_email, e)
        return False
