"""BarmanMatch — Policy pubbliche della piattaforma (tariffa minima, ecc.)."""
from fastapi import APIRouter
from wage_floor import MIN_HOURLY, DEFAULT_FLOOR
from antidisintermediation import ANTI_DISINTERMEDIATION_NOTICE

router = APIRouter()


@router.get("/terms")
def terms():
    return {
        "anti_disintermediation": ANTI_DISINTERMEDIATION_NOTICE,
        "no_black_work": "Niente pagamenti in nero: il compenso passa dall'escrow di piattaforma.",
        "min_wage": "Tariffe sotto il minimo CCNL indicativo vengono rifiutate.",
    }


@router.get("/wage-floor")
def wage_floor():
    return {
        "min_hourly": MIN_HOURLY,
        "default": DEFAULT_FLOOR,
        "nota": "Minimi orari lordi INDICATIVI (rif. CCNL Pubblici Esercizi/Turismo) — "
                "da validare con un consulente del lavoro e allineare ai tabellari correnti.",
    }
