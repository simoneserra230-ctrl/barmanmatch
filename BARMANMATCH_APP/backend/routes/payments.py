"""BarmanMatch — Onboarding pagamenti worker (Stripe Connect) + webhook."""
from datetime import datetime
from fastapi import APIRouter, Depends, Request, HTTPException
from database import get_db
from auth_middleware import require_uid
import payments
import entitlement

router = APIRouter()


@router.get("/connect/status")
def connect_status(uid: str = Depends(require_uid)):
    if not payments.enabled():
        return {"enabled": False, "ready": False}
    db = get_db()
    w = db.table("worker_profiles").select("stripe_account_id").eq("id", uid).single().execute().data or {}
    acct = w.get("stripe_account_id")
    ready = bool(acct) and payments.account_ready(acct)
    # KYC light worker: onboarding Stripe completato -> profilo verificato
    if ready:
        db.table("worker_profiles").update({"is_verified": True}).eq("id", uid).execute()
    return {"enabled": True, "account": acct, "ready": ready}


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
    db = get_db()
    etype = event.get("type", "")
    obj = (event.get("data") or {}).get("object") or {}
    meta = obj.get("metadata") or {}
    # 1) ESCROW contratto (fund) — pagamento singolo con contract_id
    if etype == "checkout.session.completed" and meta.get("contract_id"):
        db.table("contracts").update({
            "payment_status": "held",
            "payment_funded_at": datetime.utcnow().isoformat(),
            "stripe_payment_intent_id": obj.get("payment_intent"),
        }).eq("id", meta["contract_id"]).execute()
        return {"ok": True, "handled": "escrow"}
    # 2) SUBSCRIPTION struttura — attiva/revoca entitlement (venue_id in metadata)
    if entitlement.handle_subscription_event(db, event):
        return {"ok": True, "handled": "subscription"}
    return {"ok": True, "handled": None}
