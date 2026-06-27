from fastapi import APIRouter, HTTPException, Depends
from database import get_db
from auth_middleware import require_uid
from models import VenueProfileCreate, VenueProfileUpdate
from kyc import valid_piva, normalize_piva

router = APIRouter()


@router.post("/profile")
def create_profile(body: VenueProfileCreate, uid: str = Depends(require_uid)):
    db = get_db()
    existing = db.table("venue_profiles").select("id").eq("id", uid).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Profilo già esistente")

    payload = body.model_dump()
    payload["id"] = uid
    payload["email"] = db.auth.admin.get_user_by_id(uid).user.email

    # KYC light: P.IVA -> verifica formato e marca is_verified
    if payload.get("vat_number"):
        if not valid_piva(payload["vat_number"]):
            raise HTTPException(status_code=422, detail="Partita IVA non valida")
        payload["vat_number"] = normalize_piva(payload["vat_number"])
        payload["is_verified"] = True

    res = db.table("venue_profiles").insert(payload).execute()
    if not res.data:
        raise HTTPException(status_code=500, detail="Errore creazione profilo")

    # avvia subito l'entitlement (trial automatico se configurato)
    try:
        from entitlement import _ensure_row
        _ensure_row(db, uid)
    except Exception:
        pass  # non bloccare la creazione profilo se l'entitlement fallisce

    return res.data[0]


@router.get("/profile/me")
def get_my_profile(uid: str = Depends(require_uid)):
    db = get_db()
    res = db.table("venue_profiles").select("*").eq("id", uid).single().execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Profilo non trovato")
    return res.data


@router.patch("/profile/me")
def update_profile(body: VenueProfileUpdate, uid: str = Depends(require_uid)):
    db = get_db()
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="Nessun campo da aggiornare")
    if updates.get("vat_number"):
        if not valid_piva(updates["vat_number"]):
            raise HTTPException(status_code=422, detail="Partita IVA non valida")
        updates["vat_number"] = normalize_piva(updates["vat_number"])
        updates["is_verified"] = True
    res = db.table("venue_profiles").update(updates).eq("id", uid).execute()
    if not res.data:
        raise HTTPException(status_code=500, detail="Aggiornamento fallito")
    return res.data[0]


@router.get("/favorites")
def get_favorites(uid: str = Depends(require_uid)):
    db = get_db()
    res = (
        db.table("venue_favorites")
        .select("*, worker_profiles(*)")
        .eq("venue_id", uid)
        .execute()
    )
    return res.data or []


@router.post("/favorites/{worker_id}")
def add_favorite(worker_id: str, uid: str = Depends(require_uid)):
    db = get_db()
    db.table("venue_favorites").upsert(
        {"venue_id": uid, "worker_id": worker_id}
    ).execute()
    return {"ok": True}


@router.delete("/favorites/{worker_id}")
def remove_favorite(worker_id: str, uid: str = Depends(require_uid)):
    db = get_db()
    db.table("venue_favorites").delete().eq("venue_id", uid).eq(
        "worker_id", worker_id
    ).execute()
    return {"ok": True}
