"""
BarmanMatch — Eventi ("Booking.com degli eventi") con prelazione BAD.

Flusso:
  owner pubblica evento  →  POST /api/events        (apre con finestra di prelazione)
  azienda claima         →  POST /api/events/{id}/claim
        · durante la finestra: SOLO aziende is_priority=true (es. BAD)
        · dopo la finestra: qualsiasi azienda
  owner apre subito a tutti → POST /api/events/{id}/open-now (chiude la prelazione)
  owner completa/annulla    → POST /api/events/{id}/complete | /cancel

Le esigenze di staff dell'evento sono shifts collegati via shifts.event_id
(riusano il flusso candidature/contratti esistente).
"""

import os
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends

from database import get_db
from auth_middleware import require_uid
from models import EventCreate, EventCancel

router = APIRouter()

PRIORITY_DEFAULT_HOURS = int(os.environ.get("EVENT_PRIORITY_HOURS", "24"))


def _now() -> datetime:
    return datetime.utcnow()


def _iso(dt: datetime) -> str:
    return dt.isoformat()


def _parse(ts) -> datetime:
    if not ts:
        return _now()
    s = str(ts).replace("Z", "")
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return _now()


def _caller_company(db, uid: str):
    res = db.table("companies").select("*").eq("owner_uid", uid).single().execute()
    return res.data


def _in_priority_window(ev: dict) -> bool:
    return _now() < _parse(ev.get("priority_until"))


# ── PUBBLICA EVENTO ──────────────────────────────────────────────
@router.post("")
def create_event(body: EventCreate, uid: str = Depends(require_uid)):
    db = get_db()
    hours = body.priority_hours if body.priority_hours is not None else PRIORITY_DEFAULT_HOURS
    payload = body.model_dump(exclude={"priority_hours"})
    payload["date"] = str(payload["date"])
    payload["start_time"] = str(payload["start_time"])
    payload["end_time"] = str(payload["end_time"])
    payload["owner_id"] = uid
    payload["priority_until"] = _iso(_now() + timedelta(hours=max(0, hours)))
    payload["status"] = "open"
    res = db.table("events").insert(payload).execute()
    if not res.data:
        raise HTTPException(500, "Creazione evento fallita")
    ev = res.data[0]
    ev["in_priority_window"] = _in_priority_window(ev)
    return ev


# ── LISTA EVENTI APERTI ──────────────────────────────────────────
@router.get("")
def list_events(uid: str = Depends(require_uid)):
    db = get_db()
    rows = db.table("events").select("*").eq("status", "open").execute().data or []
    company = _caller_company(db, uid)
    is_priority = bool(company and company.get("is_priority"))
    for ev in rows:
        in_win = _in_priority_window(ev)
        ev["in_priority_window"] = in_win
        # claimabile ora dal chiamante?
        ev["claimable_by_me"] = bool(company) and (is_priority or not in_win)
    return sorted(rows, key=lambda e: (e.get("date") or "", e.get("start_time") or ""))


@router.get("/{event_id}")
def get_event(event_id: str, uid: str = Depends(require_uid)):
    db = get_db()
    res = db.table("events").select("*").eq("id", event_id).single().execute()
    if not res.data:
        raise HTTPException(404, "Evento non trovato")
    res.data["in_priority_window"] = _in_priority_window(res.data)
    return res.data


# ── CLAIM (azienda prende l'evento) ──────────────────────────────
@router.post("/{event_id}/claim")
def claim_event(event_id: str, uid: str = Depends(require_uid)):
    db = get_db()
    company = _caller_company(db, uid)
    if not company:
        raise HTTPException(403, "Serve un profilo azienda per prendere un evento")

    ev = db.table("events").select("*").eq("id", event_id).single().execute()
    if not ev.data:
        raise HTTPException(404, "Evento non trovato")
    if ev.data["status"] != "open" or ev.data.get("claimed_by_company"):
        raise HTTPException(409, "Evento non più disponibile")

    if _in_priority_window(ev.data) and not company.get("is_priority"):
        raise HTTPException(
            403,
            f"Evento in prelazione fino a {ev.data['priority_until']} (riservato alle aziende prioritarie)",
        )

    updates = {"status": "claimed", "claimed_by_company": company["id"], "claimed_at": _iso(_now())}
    res = db.table("events").update(updates).eq("id", event_id).execute()
    return res.data[0] if res.data else {"ok": True, **updates}


# ── OWNER: apri subito a tutte le aziende ────────────────────────
@router.post("/{event_id}/open-now")
def open_now(event_id: str, uid: str = Depends(require_uid)):
    db = get_db()
    ev = db.table("events").select("owner_id, status").eq("id", event_id).single().execute()
    if not ev.data:
        raise HTTPException(404, "Evento non trovato")
    if ev.data["owner_id"] != uid:
        raise HTTPException(403, "Solo chi ha pubblicato l'evento può aprirlo")
    db.table("events").update({"priority_until": _iso(_now())}).eq("id", event_id).execute()
    return {"ok": True, "message": "Prelazione chiusa: evento aperto a tutte le aziende"}


# ── OWNER: completa / annulla ────────────────────────────────────
@router.post("/{event_id}/complete")
def complete_event(event_id: str, uid: str = Depends(require_uid)):
    db = get_db()
    ev = db.table("events").select("owner_id").eq("id", event_id).single().execute()
    if not ev.data or ev.data["owner_id"] != uid:
        raise HTTPException(403, "Non autorizzato")
    db.table("events").update({"status": "completed"}).eq("id", event_id).execute()
    return {"ok": True}


@router.post("/{event_id}/cancel")
def cancel_event(event_id: str, body: EventCancel = EventCancel(), uid: str = Depends(require_uid)):
    db = get_db()
    ev = db.table("events").select("owner_id, status").eq("id", event_id).single().execute()
    if not ev.data or ev.data["owner_id"] != uid:
        raise HTTPException(403, "Non autorizzato")
    if ev.data["status"] == "completed":
        raise HTTPException(400, "Evento già completato")
    db.table("events").update(
        {"status": "cancelled", "cancel_reason": body.reason}
    ).eq("id", event_id).execute()
    return {"ok": True}
