"""BarmanMatch — Policy pubbliche della piattaforma (tariffa minima, ecc.)."""
from fastapi import APIRouter
from wage_floor import MIN_HOURLY, DEFAULT_FLOOR

router = APIRouter()


@router.get("/wage-floor")
def wage_floor():
    return {
        "min_hourly": MIN_HOURLY,
        "default": DEFAULT_FLOOR,
        "nota": "Minimi orari lordi INDICATIVI (rif. CCNL Pubblici Esercizi/Turismo) — "
                "da validare con un consulente del lavoro e allineare ai tabellari correnti.",
    }
