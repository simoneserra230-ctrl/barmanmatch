"""
BarmanMatch — Aziende/agenzie che staffano gli eventi.
Una company è gestita da un utente (owner_uid). BAD è una company con is_priority=true
(precedenza sugli eventi — vedi routes/events.py). is_priority è impostato lato admin/DB,
non dal self-service (un'azienda non si auto-promuove prioritaria).
"""

from fastapi import APIRouter, HTTPException, Depends
from database import get_db
from auth_middleware import require_uid
from models import CompanyCreate

router = APIRouter()


@router.post("")
def create_company(body: CompanyCreate, uid: str = Depends(require_uid)):
    db = get_db()
    existing = db.table("companies").select("id").eq("owner_uid", uid).execute()
    if existing.data:
        raise HTTPException(400, "Hai già un'azienda registrata")
    payload = {"owner_uid": uid, "name": body.name, "city": body.city, "is_priority": False}
    res = db.table("companies").insert(payload).execute()
    if not res.data:
        raise HTTPException(500, "Creazione azienda fallita")
    return res.data[0]


@router.get("/mine")
def my_company(uid: str = Depends(require_uid)):
    db = get_db()
    res = db.table("companies").select("*").eq("owner_uid", uid).single().execute()
    if not res.data:
        raise HTTPException(404, "Nessuna azienda registrata")
    return res.data
