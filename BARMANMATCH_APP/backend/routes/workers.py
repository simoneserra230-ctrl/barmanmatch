from fastapi import APIRouter, HTTPException, Depends
from database import get_db
from auth_middleware import require_uid
from models import WorkerProfileCreate, WorkerProfileUpdate

router = APIRouter()


@router.post("/profile")
def create_profile(body: WorkerProfileCreate, uid: str = Depends(require_uid)):
    db = get_db()
    existing = db.table("worker_profiles").select("id").eq("id", uid).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Profilo già esistente")

    payload = body.model_dump()
    payload["id"] = uid
    payload["email"] = db.auth.admin.get_user_by_id(uid).user.email

    res = db.table("worker_profiles").insert(payload).execute()
    if not res.data:
        raise HTTPException(status_code=500, detail="Errore creazione profilo")
    return res.data[0]


@router.get("/profile/me")
def get_my_profile(uid: str = Depends(require_uid)):
    db = get_db()
    res = db.table("worker_profiles").select("*").eq("id", uid).single().execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Profilo non trovato")
    return res.data


@router.get("/profile/{worker_id}")
def get_profile(worker_id: str, uid: str = Depends(require_uid)):
    db = get_db()
    res = db.table("worker_profiles").select("*").eq("id", worker_id).single().execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Profilo non trovato")
    return res.data


@router.patch("/profile/me")
def update_profile(body: WorkerProfileUpdate, uid: str = Depends(require_uid)):
    db = get_db()
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="Nessun campo da aggiornare")
    res = db.table("worker_profiles").update(updates).eq("id", uid).execute()
    if not res.data:
        raise HTTPException(status_code=500, detail="Aggiornamento fallito")
    return res.data[0]


@router.get("/applications")
def get_my_applications(uid: str = Depends(require_uid)):
    """Tutte le candidature del lavoratore con dettagli turno e venue."""
    db = get_db()
    res = (
        db.table("shift_applications")
        .select("*, shifts(*, venue_profiles(name, city, venue_type))")
        .eq("worker_id", uid)
        .order("applied_at", desc=True)
        .execute()
    )
    return res.data or []
