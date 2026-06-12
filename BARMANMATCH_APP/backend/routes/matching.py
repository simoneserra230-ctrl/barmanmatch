from fastapi import APIRouter, HTTPException, Depends
from database import get_db
from auth_middleware import require_uid

router = APIRouter()


def compute_match_score(worker: dict, shift: dict, history: dict) -> float:
    """
    Score composito 0–100:
    Pertinenza 40% | Qualità 35% | Relazione 15% | Reattività 10%
    """
    # ── PERTINENZA 40 ────────────────────────────────────────────
    p = 0.0
    roles = [r.lower() for r in (worker.get("roles") or [])]
    shift_role = (shift.get("role") or "").lower()
    if shift_role in roles:
        p += 25.0
    elif any(shift_role in r or r in shift_role for r in roles):
        p += 12.0

    req = set(r.lower() for r in (shift.get("requirements") or []))
    skills = set(s.lower() for s in (worker.get("skills") or []))
    if req:
        overlap = len(req & skills) / len(req)
        p += overlap * 10.0
    else:
        p += 5.0 if skills else 0.0

    w_city = (worker.get("city") or "").lower().strip()
    s_city = (shift.get("city") or "").lower().strip()
    if w_city == s_city:
        p += 5.0

    # ── QUALITÀ 35 ────────────────────────────────────────────────
    q = 0.0
    rating_count = worker.get("rating_count") or 0
    if rating_count > 0:
        q += (float(worker.get("rating_avg") or 5.0) / 5.0) * 20.0
    else:
        q += 14.0  # default generoso per nuovi lavoratori

    completion = float(worker.get("completion_rate") or 100.0)
    q += (completion / 100.0) * 10.0

    no_shows = int(worker.get("no_show_count") or 0)
    q += max(0.0, 5.0 - no_shows * 2.5)

    # ── RELAZIONE 15 ─────────────────────────────────────────────
    r = 0.0
    together = int(history.get("worked_together_count") or 0)
    if together >= 3:
        r = 15.0
    elif together > 0:
        r = 10.0
    elif history.get("is_favorite"):
        r = 8.0

    # ── REATTIVITÀ 10 ────────────────────────────────────────────
    rt = int(worker.get("avg_response_time_mins") or 60)
    if rt <= 15:
        rv = 10.0
    elif rt <= 30:
        rv = 8.0
    elif rt <= 60:
        rv = 6.0
    elif rt <= 120:
        rv = 4.0
    else:
        rv = 2.0

    return min(100.0, round(p + q + r + rv, 1))


@router.get("/shift/{shift_id}")
def rank_workers_for_shift(shift_id: str, uid: str = Depends(require_uid)):
    """
    Restituisce i top-20 lavoratori compatibili per un turno,
    ordinati per match score decrescente. Solo la venue proprietaria può chiamare.
    """
    db = get_db()

    # verifica che il turno appartenga alla venue
    shift_res = db.table("shifts").select("*").eq("id", shift_id).single().execute()
    if not shift_res.data:
        raise HTTPException(status_code=404, detail="Turno non trovato")
    shift = shift_res.data
    if shift["venue_id"] != uid:
        raise HTTPException(status_code=403, detail="Non autorizzato")

    # carica tutti i worker attivi
    workers_res = (
        db.table("worker_profiles").select("*").eq("is_active", True).execute()
    )
    workers = workers_res.data or []

    # carica preferiti della venue
    fav_res = (
        db.table("venue_favorites")
        .select("worker_id")
        .eq("venue_id", uid)
        .execute()
    )
    fav_ids = {row["worker_id"] for row in (fav_res.data or [])}

    # carica storico collaborazioni
    history_res = (
        db.table("shift_applications")
        .select("worker_id, shifts!inner(venue_id)")
        .eq("shifts.venue_id", uid)
        .eq("status", "completed")
        .execute()
    )
    history_count: dict[str, int] = {}
    for row in history_res.data or []:
        wid = row["worker_id"]
        history_count[wid] = history_count.get(wid, 0) + 1

    ranked = []
    for w in workers:
        wid = w["id"]
        hist = {
            "worked_together_count": history_count.get(wid, 0),
            "is_favorite": wid in fav_ids,
        }
        score = compute_match_score(w, shift, hist)
        ranked.append({**w, "match_score": score})

    ranked.sort(key=lambda x: x["match_score"], reverse=True)
    return ranked[:20]


@router.get("/worker/shifts")
def get_matching_shifts_for_worker(uid: str = Depends(require_uid)):
    """
    Restituisce i turni aperti compatibili per il lavoratore loggato,
    con il suo match score per ciascuno.
    """
    db = get_db()
    worker_res = (
        db.table("worker_profiles").select("*").eq("id", uid).single().execute()
    )
    if not worker_res.data:
        raise HTTPException(status_code=404, detail="Profilo lavoratore non trovato")
    worker = worker_res.data

    shifts_res = (
        db.table("shifts")
        .select("*, venue_profiles(name, city, venue_type)")
        .eq("status", "open")
        .execute()
    )
    shifts = shifts_res.data or []

    # già candidato a questi turni
    applied_res = (
        db.table("shift_applications")
        .select("shift_id")
        .eq("worker_id", uid)
        .execute()
    )
    applied_ids = {r["shift_id"] for r in (applied_res.data or [])}

    result = []
    for s in shifts:
        sid = s["id"]
        if sid in applied_ids:
            s["already_applied"] = True
        else:
            s["already_applied"] = False
        s["match_score"] = compute_match_score(worker, s, {})
        result.append(s)

    result.sort(key=lambda x: x["match_score"], reverse=True)
    return result
