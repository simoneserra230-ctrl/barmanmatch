from fastapi import APIRouter, HTTPException
from database import get_db
from models import RegisterRequest

router = APIRouter()


@router.post("/register")
def register(body: RegisterRequest):
    """Registra un nuovo utente (worker o venue) su Supabase Auth."""
    db = get_db()
    try:
        res = db.auth.sign_up({"email": body.email, "password": body.password})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not res.user:
        raise HTTPException(status_code=400, detail="Registrazione fallita")

    uid = res.user.id
    # Salva il ruolo nei metadata dell'utente (utile per RLS e frontend)
    db.auth.admin.update_user_by_id(uid, {"user_metadata": {"role": body.role}})

    return {
        "user_id": uid,
        "email": res.user.email,
        "role": body.role,
        "message": "Registrazione completata. Controlla la tua email per confermare l'account.",
    }


@router.post("/login")
def login(body: RegisterRequest):
    """Login con email/password, restituisce il JWT Supabase."""
    db = get_db()
    try:
        res = db.auth.sign_in_with_password(
            {"email": body.email, "password": body.password}
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail="Credenziali non valide")

    if not res.session:
        raise HTTPException(status_code=401, detail="Login fallito")

    return {
        "access_token": res.session.access_token,
        "token_type": "bearer",
        "user_id": res.user.id,
        "role": res.user.user_metadata.get("role", "unknown"),
    }
