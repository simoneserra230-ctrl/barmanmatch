"""
BarmanMatch — Entitlement / abbonamento STRUTTURE.

Modello deciso: i LAVORATORI usano l'app gratis; le STRUTTURE (venue) hanno
bisogno di un abbonamento ATTIVO per le AZIONI A PAGAMENTO (pubblicare turni,
generare contratti / assumere). L'ADMIN (tu) bypassa tutto.

Per ora il gate e' un FLAG entitlement: trial automatico alla creazione del
profilo + sblocco manuale dell'admin. L'aggancio a Stripe (subscription +
webhook) arrivera' dopo: bastera' che il webhook scriva qui
status='active' / current_period_end. Nessun pagamento fuori piattaforma.

Stati: inactive | trialing | active | past_due | cancelled
Attivo = trialing (trial non scaduto) OPPURE active (period non scaduto).
"""

import os
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from database import get_db
from auth_middleware import get_current_user

# Giorni di trial automatico al primo accesso di una struttura (0 = solo sblocco admin)
TRIAL_DAYS = int(os.environ.get("BMM_TRIAL_DAYS", "14"))


def _csv_env(name: str) -> set:
    return {x.strip() for x in os.environ.get(name, "").split(",") if x.strip()}


def is_admin(user: dict) -> bool:
    """Admin = email o uid presenti in BMM_ADMIN_EMAILS / BMM_ADMIN_UIDS."""
    email = (user.get("email") or "").lower()
    uid = user.get("sub") or ""
    admin_emails = {e.lower() for e in _csv_env("BMM_ADMIN_EMAILS")}
    return (bool(email) and email in admin_emails) or (bool(uid) and uid in _csv_env("BMM_ADMIN_UIDS"))


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse(ts):
    if not ts:
        return None
    s = str(ts).replace("Z", "+00:00")
    try:
        d = datetime.fromisoformat(s)
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _ensure_row(db, venue_id: str) -> dict:
    """Carica l'entitlement della venue; se manca lo crea (con trial se attivo)."""
    rows = db.table("venue_entitlements").select("*").eq("venue_id", venue_id).execute().data
    if rows:
        return rows[0]
    payload = {"venue_id": venue_id}
    if TRIAL_DAYS > 0:
        payload.update({
            "plan": "trial",
            "status": "trialing",
            "trial_ends_at": (_now() + timedelta(days=TRIAL_DAYS)).isoformat(),
        })
    else:
        payload.update({"plan": "none", "status": "inactive"})
    ins = db.table("venue_entitlements").insert(payload).execute()
    return ins.data[0] if ins.data else payload


def entitlement_state(db, venue_id: str) -> dict:
    """Stato calcolato dell'abbonamento di una struttura."""
    row = _ensure_row(db, venue_id)
    status = row.get("status", "inactive")
    now = _now()
    active = False
    reason = status
    if status == "active":
        cpe = _parse(row.get("current_period_end"))
        active = (cpe is None) or (cpe > now)
        if not active:
            reason = "expired"
    elif status == "trialing":
        te = _parse(row.get("trial_ends_at"))
        active = (te is not None) and (te > now)
        if not active:
            reason = "trial_expired"
    days_left = None
    horizon = _parse(row.get("current_period_end")) or _parse(row.get("trial_ends_at"))
    if active and horizon:
        days_left = max(0, (horizon - now).days)
    return {
        "venue_id": venue_id,
        "plan": row.get("plan", "none"),
        "status": status,
        "active": active,
        "reason": reason,
        "days_left": days_left,
        "trial_ends_at": row.get("trial_ends_at"),
        "current_period_end": row.get("current_period_end"),
    }


# ── Dependency: azione riservata a struttura con abbonamento attivo ──
def require_active_venue(user: dict = Depends(get_current_user)) -> str:
    """Ritorna l'uid se: admin (bypass) OPPURE struttura con entitlement attivo.
    Altrimenti 402 (abbonamento richiesto) o 403 (non e' una struttura)."""
    uid = user.get("sub")
    if not uid:
        raise HTTPException(status_code=401, detail="UID mancante nel token")
    if is_admin(user):
        return uid
    db = get_db()
    venue = db.table("venue_profiles").select("id").eq("id", uid).execute().data
    if not venue:
        raise HTTPException(status_code=403, detail="Solo le strutture possono eseguire questa azione")
    st = entitlement_state(db, uid)
    if not st["active"]:
        raise HTTPException(status_code=402, detail={
            "code": "subscription_required",
            "message": "Abbonamento struttura richiesto per pubblicare turni e assumere. "
                       "Attiva il piano per continuare.",
            "plan": st["plan"],
            "status": st["status"],
            "reason": st["reason"],
        })
    return uid
