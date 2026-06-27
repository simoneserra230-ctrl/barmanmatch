"""
BarmanMatch — verifica del JWT Supabase.

I progetti Supabase recenti firmano gli access token con CHIAVI ASIMMETRICHE
(ES256, esposte via JWKS), non piu' con il secret HS256. Qui supportiamo:
  - ES256 / RS256  -> verifica con la chiave pubblica del JWKS (cache 1h, per kid)
  - HS256          -> fallback con SUPABASE_JWT_SECRET (progetti legacy)
"""

import os
import time
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

bearer = HTTPBearer()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET", "")

_JWKS = {"keys": [], "fetched_at": 0.0}
_JWKS_TTL = 3600  # secondi


def _fetch_jwks(force: bool = False) -> list:
    now = time.time()
    if force or not _JWKS["keys"] or (now - _JWKS["fetched_at"]) > _JWKS_TTL:
        try:
            headers = {}
            apikey = os.environ.get("SUPABASE_KEY", "")
            if apikey:
                headers["apikey"] = apikey
            r = httpx.get(SUPABASE_URL + "/auth/v1/.well-known/jwks.json", headers=headers, timeout=5)
            r.raise_for_status()
            _JWKS["keys"] = r.json().get("keys", [])
            _JWKS["fetched_at"] = now
        except Exception:
            pass  # mantieni la cache precedente se il refresh fallisce
    return _JWKS["keys"]


def _key_for(kid: str):
    for k in _fetch_jwks():
        if k.get("kid") == kid:
            return k
    # kid non trovato: forza un refresh (rotazione chiavi) e riprova
    for k in _fetch_jwks(force=True):
        if k.get("kid") == kid:
            return k
    return None


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
) -> dict:
    token = creds.credentials
    try:
        header = jwt.get_unverified_header(token)
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token non valido: {e}")

    alg = header.get("alg", "")
    try:
        if alg == "HS256":
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"], options={"verify_aud": False})
        elif alg in ("ES256", "RS256"):
            jwk = _key_for(header.get("kid"))
            if not jwk:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Chiave di firma non trovata (JWKS)")
            payload = jwt.decode(token, jwk, algorithms=[alg], options={"verify_aud": False})
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Algoritmo token non supportato: {alg}")
        return payload
    except HTTPException:
        raise
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token non valido: {e}")


def require_uid(user: dict = Depends(get_current_user)) -> str:
    uid = user.get("sub")
    if not uid:
        raise HTTPException(status_code=401, detail="UID mancante nel token")
    return uid
