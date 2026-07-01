"""
BarmanMatch — Stato abbonamento STRUTTURA + comandi ADMIN.

- GET  /api/billing/status        stato del chiamante (worker=gratis, venue=entitlement, admin=bypass)
- POST /api/billing/checkout      Stripe subscription (TODO: 501 finche' non configurato)
- GET  /api/billing/admin/venues  [admin] elenco strutture + stato abbonamento
- POST /api/billing/admin/grant   [admin] attiva/sblocca una struttura
- POST /api/billing/admin/revoke  [admin] disattiva una struttura
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from database import get_db
from auth_middleware import get_current_user
import entitlement
import payments

router = APIRouter()


class AdminGrant(BaseModel):
    venue_id: str
    plan: str = "pro"
    days: Optional[int] = None     # durata; None = senza scadenza esplicita


class AdminRevoke(BaseModel):
    venue_id: str


def _utcnow():
    return datetime.now(timezone.utc)


# ── Stato del chiamante ──────────────────────────────────────────
@router.get("/status")
def my_status(user: dict = Depends(get_current_user)):
    if entitlement.is_admin(user):
        return {"role": "admin", "is_admin": True, "active": True, "plan": "admin", "status": "admin"}
    uid = user.get("sub")
    db = get_db()
    venue = db.table("venue_profiles").select("id").eq("id", uid).execute().data
    if not venue:
        # worker o profilo non-venue: app gratuita, nessun gate
        return {"role": "worker", "is_admin": False, "active": True, "plan": "free", "status": "free"}
    st = entitlement.entitlement_state(db, uid)
    st.update({"role": "venue", "is_admin": False})
    return st


# ── Acquisto abbonamento (Stripe subscription) ───────────────────
@router.post("/checkout")
def checkout(user: dict = Depends(get_current_user)):
    """Avvia il checkout di abbonamento per la STRUTTURA. Ritorna l'URL Stripe.
    Worker = gratis (400); admin = bypass (400); Stripe non configurato = 501 (usa lo sblocco admin)."""
    if entitlement.is_admin(user):
        raise HTTPException(400, "Gli amministratori non necessitano di abbonamento")
    uid = user.get("sub")
    db = get_db()
    venue = db.table("venue_profiles").select("id, email, name").eq("id", uid).execute().data
    if not venue:
        raise HTTPException(403, "Solo le strutture (venue) sottoscrivono l'abbonamento; i lavoratori usano l'app gratis")
    if not payments.subscription_ready():
        raise HTTPException(
            status_code=501,
            detail="Pagamento abbonamento non ancora attivo (Stripe/price non configurati). "
                   "Contatta l'amministratore per lo sblocco.",
        )
    try:
        url = payments.create_subscription_checkout(uid, (venue[0].get("email") or ""))
    except Exception as e:
        raise HTTPException(502, f"Stripe non disponibile: {e}")
    return {"url": url}


# ── ADMIN ────────────────────────────────────────────────────────
def _require_admin(user: dict):
    if not entitlement.is_admin(user):
        raise HTTPException(status_code=403, detail="Riservato all'amministratore")


@router.get("/admin/venues")
def admin_list(user: dict = Depends(get_current_user)):
    _require_admin(user)
    db = get_db()
    venues = db.table("venue_profiles").select("id, name, city, email").execute().data or []
    out = []
    for v in venues:
        st = entitlement.entitlement_state(db, v["id"])
        out.append({**v, **st})
    return out


@router.post("/admin/grant")
def admin_grant(body: AdminGrant, user: dict = Depends(get_current_user)):
    _require_admin(user)
    db = get_db()
    entitlement._ensure_row(db, body.venue_id)
    updates = {"plan": body.plan, "status": "active", "updated_at": _utcnow().isoformat()}
    updates["current_period_end"] = (
        (_utcnow() + timedelta(days=body.days)).isoformat() if body.days else None
    )
    db.table("venue_entitlements").update(updates).eq("venue_id", body.venue_id).execute()
    return entitlement.entitlement_state(db, body.venue_id)


@router.post("/admin/revoke")
def admin_revoke(body: AdminRevoke, user: dict = Depends(get_current_user)):
    _require_admin(user)
    db = get_db()
    entitlement._ensure_row(db, body.venue_id)
    db.table("venue_entitlements").update(
        {"plan": "none", "status": "inactive", "updated_at": _utcnow().isoformat()}
    ).eq("venue_id", body.venue_id).execute()
    return entitlement.entitlement_state(db, body.venue_id)
