"""
BarmanMatch — Tariffa minima oraria (anti servizi sottopagati).

Blocca shift/contratti sotto la soglia minima per ruolo. I valori sono
LORDI INDICATIVI riferiti al CCNL Pubblici Esercizi/Turismo: DA VALIDARE con
un consulente del lavoro e da allineare ai minimi tabellari correnti
(principio human-in-the-loop). Override possibile via env WAGE_FLOOR_DEFAULT.
"""

import os
from fastapi import HTTPException

# €/h lordi minimi indicativi per ruolo (rif. CCNL Pubblici Esercizi/Turismo)
MIN_HOURLY = {
    "bartender":     9.5,
    "barista":       9.0,
    "barback":       8.5,
    "cameriere":     9.0,
    "runner":        8.5,
    "hostess":       9.0,
    "sommelier":    12.0,
    "chef":         12.0,
    "cuoco":        11.0,
    "aiuto cucina":  8.5,
    "lavapiatti":    8.0,
}
DEFAULT_FLOOR = float(os.environ.get("WAGE_FLOOR_DEFAULT", "8.5"))


def _norm(role: str) -> str:
    return (role or "").strip().lower()


def floor_for(role: str) -> float:
    return MIN_HOURLY.get(_norm(role), DEFAULT_FLOOR)


def enforce_floor(role: str, rate) -> float:
    """Solleva 422 se la tariffa è sotto il minimo. Ritorna la soglia applicata."""
    f = floor_for(role)
    if rate is None or float(rate) < f:
        raise HTTPException(
            status_code=422,
            detail=f"Tariffa sotto il minimo: per '{role}' il minimo è €{f}/h. "
                   f"BarmanMatch non ammette servizi sottopagati — adegua la tariffa.",
        )
    return f
