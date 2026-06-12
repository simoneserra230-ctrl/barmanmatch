from fastapi import APIRouter, HTTPException, Depends
from database import get_db
from auth_middleware import require_uid
from models import RatingCreate

router = APIRouter()


@router.post("")
def submit_rating(body: RatingCreate, uid: str = Depends(require_uid)):
    db = get_db()

    # carica l'applicazione
    app_res = (
        db.table("shift_applications")
        .select("*, shifts(venue_id, status)")
        .eq("id", body.application_id)
        .single()
        .execute()
    )
    if not app_res.data:
        raise HTTPException(status_code=404, detail="Applicazione non trovata")
    app = app_res.data
    shift = app["shifts"]

    if shift["status"] != "completed":
        raise HTTPException(status_code=400, detail="Il turno non è ancora completato")

    # determina rater_type e ratee_id
    venue_id = shift["venue_id"]
    worker_id = app["worker_id"]

    if uid == venue_id:
        rater_type = "venue"
        ratee_id = worker_id
    elif uid == worker_id:
        rater_type = "worker"
        ratee_id = venue_id
    else:
        raise HTTPException(status_code=403, detail="Non coinvolto in questo turno")

    payload = body.model_dump()
    payload["shift_id"] = app["shift_id"]
    payload["rater_type"] = rater_type
    payload["rater_id"] = uid
    payload["ratee_id"] = ratee_id
    payload["is_published"] = True

    res = db.table("ratings").insert(payload).execute()
    if not res.data:
        raise HTTPException(status_code=400, detail="Rating già inserito o errore")

    # aggiorna statistiche lavoratore se la venue ha valutato il worker
    if rater_type == "venue":
        _update_worker_stats(db, worker_id)

    return res.data[0]


def _update_worker_stats(db, worker_id: str):
    """Ricalcola e aggiorna rating_avg e rating_count del lavoratore."""
    res = (
        db.table("ratings")
        .select("score")
        .eq("ratee_id", worker_id)
        .eq("rater_type", "venue")
        .eq("is_published", True)
        .execute()
    )
    scores = [r["score"] for r in (res.data or [])]
    if not scores:
        return
    avg = round(sum(scores) / len(scores), 2)
    count = len(scores)
    # aggiorna badge
    badge_top = avg >= 4.8 and count >= 10
    db.table("worker_profiles").update(
        {
            "rating_avg": avg,
            "rating_count": count,
            "badge_top_rated": badge_top,
        }
    ).eq("id", worker_id).execute()


@router.get("/worker/{worker_id}")
def get_worker_ratings(worker_id: str, uid: str = Depends(require_uid)):
    db = get_db()
    res = (
        db.table("ratings")
        .select("*")
        .eq("ratee_id", worker_id)
        .eq("rater_type", "venue")
        .eq("is_published", True)
        .order("created_at", desc=True)
        .execute()
    )
    return res.data or []
