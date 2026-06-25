from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from database import get_db
from auth_middleware import require_uid
from entitlement import require_active_venue
from models import ShiftCreate, ShiftUpdate, ApplyRequest, ConfirmApplicationRequest
from wage_floor import enforce_floor

router = APIRouter()


# ── VENUE: aggiorna stato di una singola candidatura ─────────────
@router.patch("/application/{app_id}")
def update_application_status(app_id: str, body: dict, uid: str = Depends(require_uid)):
    """Permette alla venue di rifiutare una candidatura."""
    db = get_db()
    app = (
        db.table("shift_applications")
        .select("shift_id, shifts(venue_id)")
        .eq("id", app_id)
        .single()
        .execute()
    )
    if not app.data:
        raise HTTPException(status_code=404, detail="Candidatura non trovata")
    if app.data["shifts"]["venue_id"] != uid:
        raise HTTPException(status_code=403, detail="Non autorizzato")
    db.table("shift_applications").update({"status": body.get("status", "rejected")}).eq("id", app_id).execute()
    return {"ok": True}


# ── VENUE: crea / leggi / aggiorna turni ─────────────────────────

@router.post("")
def create_shift(body: ShiftCreate, uid: str = Depends(require_active_venue)):
    # require_active_venue: solo struttura con abbonamento attivo (admin bypassa)
    db = get_db()

    # tariffa minima bloccante (no servizi sottopagati)
    enforce_floor(body.role, body.hourly_rate)

    payload = body.model_dump()
    payload["venue_id"] = uid
    payload["date"] = str(payload["date"])
    payload["start_time"] = str(payload["start_time"])
    payload["end_time"] = str(payload["end_time"])

    res = db.table("shifts").insert(payload).execute()
    if not res.data:
        raise HTTPException(status_code=500, detail="Creazione turno fallita")
    return res.data[0]


@router.get("/mine")
def get_my_shifts(uid: str = Depends(require_uid)):
    db = get_db()
    res = (
        db.table("shifts")
        .select("*, shift_applications(*, worker_profiles(full_name, city, rating_avg, roles))")
        .eq("venue_id", uid)
        .order("date", desc=True)
        .execute()
    )
    return res.data or []


@router.get("/{shift_id}")
def get_shift(shift_id: str, uid: str = Depends(require_uid)):
    db = get_db()
    res = (
        db.table("shifts")
        .select("*, venue_profiles(name, city, venue_type, address)")
        .eq("id", shift_id)
        .single()
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=404, detail="Turno non trovato")
    return res.data


@router.patch("/{shift_id}")
def update_shift(shift_id: str, body: ShiftUpdate, uid: str = Depends(require_uid)):
    db = get_db()
    shift = db.table("shifts").select("venue_id").eq("id", shift_id).single().execute()
    if not shift.data or shift.data["venue_id"] != uid:
        raise HTTPException(status_code=403, detail="Non autorizzato")
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    res = db.table("shifts").update(updates).eq("id", shift_id).execute()
    return res.data[0] if res.data else {}


@router.delete("/{shift_id}")
def cancel_shift(shift_id: str, uid: str = Depends(require_uid)):
    db = get_db()
    shift = db.table("shifts").select("venue_id, status").eq("id", shift_id).single().execute()
    if not shift.data or shift.data["venue_id"] != uid:
        raise HTTPException(status_code=403, detail="Non autorizzato")
    db.table("shifts").update({"status": "cancelled"}).eq("id", shift_id).execute()
    return {"ok": True}


# ── WORKER: candidatura ──────────────────────────────────────────

@router.post("/{shift_id}/apply")
def apply_to_shift(shift_id: str, body: ApplyRequest, uid: str = Depends(require_uid)):
    db = get_db()

    worker = db.table("worker_profiles").select("id").eq("id", uid).single().execute()
    if not worker.data:
        raise HTTPException(status_code=403, detail="Solo i lavoratori possono candidarsi")

    shift = db.table("shifts").select("*").eq("id", shift_id).single().execute()
    if not shift.data:
        raise HTTPException(status_code=404, detail="Turno non trovato")
    if shift.data["status"] != "open":
        raise HTTPException(status_code=400, detail="Turno non disponibile")

    # calcola match score
    from routes.matching import compute_match_score
    worker_full = db.table("worker_profiles").select("*").eq("id", uid).single().execute()
    score = compute_match_score(worker_full.data, shift.data, {})

    payload = {
        "shift_id": shift_id,
        "worker_id": uid,
        "match_score": score,
        "contract_accepted": body.contract_accepted,
        "contract_accepted_at": datetime.utcnow().isoformat() if body.contract_accepted else None,
    }
    res = db.table("shift_applications").insert(payload).execute()
    if not res.data:
        raise HTTPException(status_code=400, detail="Candidatura fallita (già candidato?)")

    return {
        "application_id": res.data[0]["id"],
        "match_score": score,
        "message": "Candidatura inviata con successo",
    }


@router.post("/{shift_id}/withdraw")
def withdraw_application(shift_id: str, uid: str = Depends(require_uid)):
    db = get_db()
    db.table("shift_applications").update({"status": "withdrawn"}).eq(
        "shift_id", shift_id
    ).eq("worker_id", uid).execute()
    return {"ok": True}


# ── VENUE: gestione applicazioni ─────────────────────────────────

@router.post("/{shift_id}/confirm")
def confirm_worker(
    shift_id: str,
    body: ConfirmApplicationRequest,
    uid: str = Depends(require_uid),
):
    db = get_db()
    shift = db.table("shifts").select("venue_id, spots").eq("id", shift_id).single().execute()
    if not shift.data or shift.data["venue_id"] != uid:
        raise HTTPException(status_code=403, detail="Non autorizzato")

    db.table("shift_applications").update(
        {"status": "confirmed", "confirmed_at": datetime.utcnow().isoformat()}
    ).eq("id", body.application_id).execute()

    # conta confirmati, se raggiunge spots → chiude il turno
    confirmed_count = (
        db.table("shift_applications")
        .select("id", count="exact")
        .eq("shift_id", shift_id)
        .eq("status", "confirmed")
        .execute()
    )
    if (confirmed_count.count or 0) >= shift.data["spots"]:
        db.table("shifts").update({"status": "filled"}).eq("id", shift_id).execute()

    return {"ok": True, "message": "Lavoratore confermato"}


@router.post("/{shift_id}/complete")
def mark_completed(shift_id: str, uid: str = Depends(require_uid)):
    """Venue marca il turno come completato (abilitando i rating)."""
    db = get_db()
    shift = db.table("shifts").select("venue_id").eq("id", shift_id).single().execute()
    if not shift.data or shift.data["venue_id"] != uid:
        raise HTTPException(status_code=403, detail="Non autorizzato")

    db.table("shifts").update({"status": "completed"}).eq("id", shift_id).execute()
    db.table("shift_applications").update({"status": "completed"}).eq(
        "shift_id", shift_id
    ).eq("status", "confirmed").execute()
    return {"ok": True}
