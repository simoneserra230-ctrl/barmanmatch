"""
BarmanMatch — Contratti tipo Deliveroo.

Flusso:
  venue conferma candidatura  →  POST /from-application/{id}  (genera contratto, venue firma)
  worker firma                →  POST /{id}/sign              (entrambe firmate → 'active')
  fine turno                  →  POST /{id}/complete          (venue, opz. ore effettive)
  annullo                     →  POST /{id}/cancel            (una delle parti, con motivo)

Economia (trasparente e deterministica):
  gross_total  = hourly_rate * ore        (compenso del worker)
  fee_amount   = gross_total * fee_pct     (commissione piattaforma, a carico venue)
  venue_total  = gross_total + fee_amount  (quanto paga la venue)
  worker_payout= gross_total
"""

import os
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends

from database import get_db
from auth_middleware import require_uid
from entitlement import require_active_venue
from antidisintermediation import ANTI_DISINTERMEDIATION_NOTICE
from models import ContractCreate, ContractComplete, ContractCancel
from wage_floor import enforce_floor
import payments

router = APIRouter()

DEFAULT_FEE_PCT = float(os.environ.get("PLATFORM_FEE_PCT", "0.12"))
DEFAULT_CANCELLATION = "Cancellazione gratuita fino a 24h prima dell'inizio. Oltre, addebito del 50% del compenso."
DEFAULT_PAYMENT = "Pagamento al worker entro 7 giorni dal completamento del turno."


def _now() -> str:
    return datetime.utcnow().isoformat()


def _to_minutes(t) -> int:
    parts = str(t).split(":")
    h = int(parts[0]); m = int(parts[1]) if len(parts) > 1 else 0
    return h * 60 + m


def _hours(start, end) -> float:
    s, e = _to_minutes(start), _to_minutes(end)
    if e <= s:           # turno a cavallo della mezzanotte
        e += 24 * 60
    return round((e - s) / 60, 2)


def _economics(rate: float, hours: float, fee_pct: float) -> dict:
    gross = round(rate * hours, 2)
    fee = round(gross * fee_pct, 2)
    return {
        "est_hours": hours,
        "gross_total": gross,
        "fee_pct": fee_pct,
        "fee_amount": fee,
        "venue_total": round(gross + fee, 2),
        "worker_payout": gross,
    }


def _is_party(c: dict, uid: str) -> bool:
    return uid in (c.get("venue_id"), c.get("worker_id"))


# ── GENERA CONTRATTO (venue, da candidatura confermata) ──────────
@router.post("/from-application/{application_id}")
def create_from_application(application_id: str, body: ContractCreate = ContractCreate(), uid: str = Depends(require_active_venue)):
    # require_active_venue: assumere richiede abbonamento struttura attivo (admin bypassa)
    db = get_db()

    app = db.table("shift_applications").select("*").eq("id", application_id).single().execute()
    if not app.data:
        raise HTTPException(404, "Candidatura non trovata")
    if app.data.get("status") != "confirmed":
        raise HTTPException(400, "Il contratto si genera solo da una candidatura confermata")

    shift = db.table("shifts").select("*").eq("id", app.data["shift_id"]).single().execute()
    if not shift.data:
        raise HTTPException(404, "Turno non trovato")
    if shift.data["venue_id"] != uid:
        raise HTTPException(403, "Solo la struttura del turno può generare il contratto")

    # tariffa minima bloccante (difesa in profondità anche sul turno già esistente)
    min_rate = enforce_floor(shift.data["role"], float(shift.data["hourly_rate"]))

    fee_pct = body.fee_pct if body.fee_pct is not None else DEFAULT_FEE_PCT
    hours = _hours(shift.data["start_time"], shift.data["end_time"])
    econ = _economics(float(shift.data["hourly_rate"]), hours, fee_pct)

    payload = {
        "shift_id": shift.data["id"],
        "application_id": application_id,
        "venue_id": uid,
        "worker_id": app.data["worker_id"],
        "role": shift.data["role"],
        "date": str(shift.data["date"]),
        "start_time": str(shift.data["start_time"]),
        "end_time": str(shift.data["end_time"]),
        "hourly_rate": float(shift.data["hourly_rate"]),
        **econ,
        "terms": {
            "requirements": shift.data.get("requirements", []),
            "dress_code": shift.data.get("dress_code"),
            "cancellation_policy": body.cancellation_policy or DEFAULT_CANCELLATION,
            "payment_terms": body.payment_terms or DEFAULT_PAYMENT,
            "platform_policy": ANTI_DISINTERMEDIATION_NOTICE,
        },
        "status": "draft",
        "venue_signed": True,
        "venue_signed_at": _now(),
        "worker_signed": False,
        "min_hourly_rate": min_rate,
        "payment_status": "pending",   # escrow: pending → held → released/refunded
    }
    res = db.table("contracts").insert(payload).execute()
    if not res.data:
        raise HTTPException(400, "Contratto già esistente per questa candidatura")
    return res.data[0]


# ── LISTA CONTRATTI (worker o venue) ─────────────────────────────
@router.get("/mine")
def my_contracts(uid: str = Depends(require_uid)):
    db = get_db()
    as_venue = db.table("contracts").select("*").eq("venue_id", uid).execute().data or []
    as_worker = db.table("contracts").select("*").eq("worker_id", uid).execute().data or []
    merged = {c["id"]: c for c in as_venue}
    merged.update({c["id"]: c for c in as_worker})
    return sorted(merged.values(), key=lambda c: c.get("created_at", ""), reverse=True)


@router.get("/{contract_id}")
def get_contract(contract_id: str, uid: str = Depends(require_uid)):
    db = get_db()
    res = db.table("contracts").select("*").eq("id", contract_id).single().execute()
    if not res.data or not _is_party(res.data, uid):
        raise HTTPException(404, "Contratto non trovato")
    return res.data


# ── CONTATTI controparte (sbloccati a contratto firmato) ─────────
@router.get("/{contract_id}/contact")
def get_contact(contract_id: str, uid: str = Depends(require_uid)):
    """Contatti diretti della controparte: disponibili SOLO quando il contratto
    e' attivo o completato (anti-disintermediazione)."""
    db = get_db()
    c = db.table("contracts").select("*").eq("id", contract_id).single().execute()
    if not c.data or not _is_party(c.data, uid):
        raise HTTPException(404, "Contratto non trovato")
    if c.data.get("status") not in ("active", "completed"):
        raise HTTPException(403, "I contatti si sbloccano quando il contratto e' firmato da entrambi")

    if uid == c.data["venue_id"]:
        w = db.table("worker_profiles").select("full_name, phone, email, city").eq("id", c.data["worker_id"]).single().execute().data or {}
        return {"role": "worker", "name": w.get("full_name"), "phone": w.get("phone"), "email": w.get("email"), "city": w.get("city")}
    v = db.table("venue_profiles").select("name, phone, email, city, address").eq("id", c.data["venue_id"]).single().execute().data or {}
    return {"role": "venue", "name": v.get("name"), "phone": v.get("phone"), "email": v.get("email"), "city": v.get("city"), "address": v.get("address")}


# ── FIRMA ────────────────────────────────────────────────────────
@router.post("/{contract_id}/sign")
def sign_contract(contract_id: str, uid: str = Depends(require_uid)):
    db = get_db()
    c = db.table("contracts").select("*").eq("id", contract_id).single().execute()
    if not c.data or not _is_party(c.data, uid):
        raise HTTPException(404, "Contratto non trovato")
    if c.data["status"] != "draft":
        raise HTTPException(400, f"Contratto non firmabile (stato: {c.data['status']})")

    updates = {}
    worker_signed = bool(c.data.get("worker_signed"))
    venue_signed = bool(c.data.get("venue_signed"))
    if uid == c.data["worker_id"]:
        updates["worker_signed"] = True
        updates["worker_signed_at"] = _now()
        worker_signed = True
    else:
        updates["venue_signed"] = True
        updates["venue_signed_at"] = _now()
        venue_signed = True

    if worker_signed and venue_signed:
        updates["status"] = "active"
        updates["activated_at"] = _now()

    res = db.table("contracts").update(updates).eq("id", contract_id).execute()
    return res.data[0] if res.data else {"ok": True, **updates}


# ── ESCROW: la venue finanzia il pagamento (anti-nero) ───────────
@router.post("/{contract_id}/fund")
def fund_contract(contract_id: str, uid: str = Depends(require_uid)):
    """La venue versa il compenso in escrow sulla piattaforma. Stub stato:
    qui muove solo lo stato 'pending'→'held'; il movimento reale di denaro
    sarà gestito da Stripe Connect (TODO). Niente pagamenti fuori piattaforma."""
    db = get_db()
    c = db.table("contracts").select("*").eq("id", contract_id).single().execute()
    if not c.data:
        raise HTTPException(404, "Contratto non trovato")
    if c.data["venue_id"] != uid:
        raise HTTPException(403, "Solo la struttura può finanziare il contratto")
    if c.data["status"] != "active":
        raise HTTPException(400, "Finanziabile solo quando il contratto è attivo (firmato da entrambi)")
    if c.data.get("payment_status") != "pending":
        raise HTTPException(400, f"Pagamento già gestito (stato: {c.data.get('payment_status')})")
    # Con Stripe: la venue paga via Checkout, il webhook porterà a 'held'.
    if payments.enabled():
        try:
            url = payments.create_fund_checkout(c.data)
        except Exception as e:
            raise HTTPException(502, f"Errore Stripe: {e}")
        return {"ok": True, "checkout_url": url}
    # Fallback simulato (nessun denaro reale)
    updates = {"payment_status": "held", "payment_funded_at": _now()}
    res = db.table("contracts").update(updates).eq("id", contract_id).execute()
    return res.data[0] if res.data else {"ok": True, **updates}


# ── COMPLETA (venue) ─────────────────────────────────────────────
@router.post("/{contract_id}/complete")
def complete_contract(contract_id: str, body: ContractComplete = ContractComplete(), uid: str = Depends(require_uid)):
    db = get_db()
    c = db.table("contracts").select("*").eq("id", contract_id).single().execute()
    if not c.data:
        raise HTTPException(404, "Contratto non trovato")
    if c.data["venue_id"] != uid:
        raise HTTPException(403, "Solo la struttura può completare il contratto")
    if c.data["status"] != "active":
        raise HTTPException(400, f"Contratto non attivo (stato: {c.data['status']})")
    if c.data.get("payment_status") != "held":
        raise HTTPException(400, "Finanzia il pagamento in escrow (POST /fund) prima di completare il turno — niente pagamenti fuori piattaforma")

    updates = {"status": "completed", "completed_at": _now(),
               "payment_status": "released", "payment_released_at": _now()}
    final = dict(c.data)
    if body.actual_hours is not None:
        econ = _economics(float(c.data["hourly_rate"]), round(float(body.actual_hours), 2), float(c.data["fee_pct"]))
        updates["actual_hours"] = econ["est_hours"]
        updates["gross_total"] = econ["gross_total"]
        updates["fee_amount"] = econ["fee_amount"]
        updates["venue_total"] = econ["venue_total"]
        updates["worker_payout"] = econ["worker_payout"]
        final.update(updates)

    # Con Stripe: accredita il compenso al conto Connect del worker.
    if payments.enabled():
        w = db.table("worker_profiles").select("stripe_account_id").eq("id", c.data["worker_id"]).single().execute().data or {}
        acct = w.get("stripe_account_id")
        if not acct or not payments.account_ready(acct):
            raise HTTPException(400, "Il professionista deve completare l'onboarding pagamenti prima dell'accredito")
        try:
            updates["stripe_transfer_id"] = payments.release(final, acct)
        except Exception as e:
            raise HTTPException(502, f"Errore accredito Stripe: {e}")

    res = db.table("contracts").update(updates).eq("id", contract_id).execute()
    return res.data[0] if res.data else {"ok": True, **updates}


# ── ANNULLA (una delle parti) ────────────────────────────────────
@router.post("/{contract_id}/cancel")
def cancel_contract(contract_id: str, body: ContractCancel = ContractCancel(), uid: str = Depends(require_uid)):
    db = get_db()
    c = db.table("contracts").select("*").eq("id", contract_id).single().execute()
    if not c.data or not _is_party(c.data, uid):
        raise HTTPException(404, "Contratto non trovato")
    if c.data["status"] in ("completed", "cancelled"):
        raise HTTPException(400, f"Contratto non annullabile (stato: {c.data['status']})")

    updates = {
        "status": "cancelled",
        "cancelled_at": _now(),
        "cancel_reason": body.reason or ("Annullato dalla struttura" if uid == c.data["venue_id"] else "Annullato dal professionista"),
    }
    if c.data.get("payment_status") == "held":   # escrow finanziato → rimborso alla venue
        if payments.enabled():
            try:
                rid = payments.refund(c.data)
                if rid:
                    updates["stripe_refund_id"] = rid
            except Exception as e:
                raise HTTPException(502, f"Errore rimborso Stripe: {e}")
        updates["payment_status"] = "refunded"
    res = db.table("contracts").update(updates).eq("id", contract_id).execute()
    return res.data[0] if res.data else {"ok": True, **updates}
