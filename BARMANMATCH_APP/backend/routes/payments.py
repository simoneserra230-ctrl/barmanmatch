"""BarmanMatch — Onboarding pagamenti worker (Stripe Connect) + webhook."""
from datetime import datetime
from fastapi import APIRouter, Depends, Request, HTTPException
from database import get_db
from auth_middleware import require_uid
import payments

router = APIRouter()


@router.get("/connect/status")
def connect_status(uid: str = Depends(require_uid)):
    if not payments.enabled():
        return {"enabled": False, "ready": False}
    db = get_db()
    w = db.table("worker_profiles").select("stripe_account_id").eq("id", uid).single().execute().data or {}
    acct = w.get("stripe_account_id")
    return {"enabled": True, "account": acct, "ready": bool(acct) and payments.account_ready(acct)}


@router.post("/connect/onboard")
def connect_onboard(uid: str = Depends(require_uid)):
    if not payments.enabled():
        raise HTTPException(400, "Pagamenti non ancora attivi (Stripe non configurato)")
    db = get_db()
    acct = payments.ensure_account(db, uid)
    return {"url": payments.onboarding_link(acct)}


@router.post("/webhook")
async def webhook(request: Request):
    if not payments.enabled():
        return {"ok": False, "reason": "stripe disabled"}
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    try:
        event = payments.parse_webhook(payload, sig)
    except Exception as e:
        raise HTTPException(400, f"Webhook non valido: {e}")
    if event.get("type") == "checkout.session.completed":
        obj = event["data"]["object"]
        cid = (obj.get("metadata") or {}).get("contract_id")
        if cid:
            get_db().table("contracts").update({
                "payment_status": "held",
                "payment_funded_at": datetime.utcnow().isoformat(),
                "stripe_payment_intent_id": obj.get("payment_intent"),
            }).eq("id", cid).execute()
    return {"ok": True}
