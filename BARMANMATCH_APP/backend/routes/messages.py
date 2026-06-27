"""
BarmanMatch — Chat in-app legata al CONTRATTO (anti-disintermediazione).

La conversazione vive sul contratto: solo le due parti (venue + worker) possono
leggere/scrivere. Ogni messaggio passa per lo scrub anti-disintermediazione, quindi
numeri/email/handle vengono oscurati prima del salvataggio (niente "ti chiamo io").

  GET  /api/messages/{contract_id}        elenco messaggi (solo parti)
  POST /api/messages/{contract_id}        invia {body} (scrub + flagged)
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from database import get_db
from auth_middleware import require_uid
from antidisintermediation import scrub_text

router = APIRouter()


class MessageCreate(BaseModel):
    body: str


def _contract_party(db, contract_id: str, uid: str) -> dict:
    c = db.table("contracts").select("id, venue_id, worker_id").eq("id", contract_id).single().execute()
    if not c.data or uid not in (c.data.get("venue_id"), c.data.get("worker_id")):
        raise HTTPException(404, "Conversazione non trovata")
    return c.data


@router.get("/{contract_id}")
def list_messages(contract_id: str, uid: str = Depends(require_uid)):
    db = get_db()
    _contract_party(db, contract_id, uid)
    rows = (
        db.table("messages")
        .select("*")
        .eq("contract_id", contract_id)
        .order("created_at", desc=False)
        .execute()
        .data
        or []
    )
    for m in rows:
        m["mine"] = (m.get("sender_id") == uid)
    return rows


@router.post("/{contract_id}")
def send_message(contract_id: str, body: MessageCreate, uid: str = Depends(require_uid)):
    db = get_db()
    _contract_party(db, contract_id, uid)
    text = (body.body or "").strip()
    if not text:
        raise HTTPException(400, "Messaggio vuoto")
    clean, flagged = scrub_text(text)
    payload = {
        "contract_id": contract_id,
        "sender_id": uid,
        "body": clean,
        "flagged": flagged,
    }
    res = db.table("messages").insert(payload).execute()
    if not res.data:
        raise HTTPException(500, "Invio fallito")
    msg = res.data[0]
    msg["mine"] = True
    if flagged:
        msg["notice"] = "Contatti diretti rimossi: comunica e paga in piattaforma."
    return msg
