"""
BarmanMatch — KYC light.

- STRUTTURE: P.IVA italiana (11 cifre, checksum). Una venue con P.IVA valida e'
  marcata is_verified=true. Questo, con l'escrow e i minimi CCNL, tiene fuori
  chi vuole lavoro in nero / sottopagato.
- LAVORATORI: la verifica forte e' demandata all'onboarding Stripe Connect
  (identita' + payout), che setta worker_profiles.is_verified quando il conto e'
  pronto (vedi routes/payments.py).
"""

import re

_PIVA_RE = re.compile(r"^\d{11}$")


def normalize_piva(piva: str) -> str:
    return (piva or "").strip().replace(" ", "").replace(".", "").upper().removeprefix("IT")


def valid_piva(piva: str) -> bool:
    """Valida una Partita IVA italiana (11 cifre + cifra di controllo)."""
    p = normalize_piva(piva)
    if not _PIVA_RE.match(p):
        return False
    total = 0
    for i, ch in enumerate(p[:10]):
        d = int(ch)
        if i % 2 == 1:        # posizioni pari (1-indexed): raddoppia
            d *= 2
            if d > 9:
                d -= 9
        total += d
    check = (10 - (total % 10)) % 10
    return check == int(p[10])
