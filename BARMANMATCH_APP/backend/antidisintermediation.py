"""
BarmanMatch — Anti-disintermediazione (tenere il lavoro IN piattaforma, no nero).

Due leve:
  1) SCRUB dei testi liberi: numeri di telefono, email, URL e handle social vengono
     oscurati prima di mostrarli alla controparte o di salvarli in chat.
  2) MASCHERAMENTO contatti: telefono/email/indirizzo esatto della controparte sono
     nascosti finche' non c'e' un contratto attivo (vedi contracts.contact).

Obiettivo: niente scambio di contatti "al volo" per saltare fee + escrow (= no nero).
Non e' a prova di bomba (nessuno scrub lo e'), ma alza l'attrito e segnala l'intento.
"""

import re

PLACEHOLDER = "[contatto rimosso]"
LINK_PLACEHOLDER = "[link rimosso]"

ANTI_DISINTERMEDIATION_NOTICE = (
    "Comunicazioni e pagamenti restano IN piattaforma. Scambiare contatti per "
    "concludere fuori da BarmanMatch (per saltare commissioni o pagare in nero) "
    "viola i Termini, annulla le tutele (escrow, assicurazione reputazione) e puo' "
    "comportare la sospensione dell'account. I contatti diretti si sbloccano a "
    "contratto firmato."
)

_EMAIL = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
_URL = re.compile(r"\b(?:https?://|www\.)\S+", re.I)
_SOCIAL = re.compile(
    r"\b(whats?app|wapp|telegram|tlgrm|signal|instagram|insta|messenger|skype|snapchat)\b[\s:@]*\S*",
    re.I,
)
_HANDLE = re.compile(r"(?<![A-Za-z0-9._])@[A-Za-z0-9._]{2,}")
# sequenze "telefoniche": +/00 prefisso opzionale, cifre con spazi/.-() in mezzo
_PHONE = re.compile(r"(?:\+|00)?\d[\d\s().\-]{6,}\d")


def _redact_phone(m: re.Match) -> str:
    s = m.group(0)
    digits = sum(c.isdigit() for c in s)
    return PLACEHOLDER if digits >= 8 else s   # >=8 cifre = quasi certamente un numero


def scrub_text(s):
    """Ritorna (testo_pulito, flagged) — flagged=True se qualcosa e' stato oscurato."""
    if not s:
        return s, False
    original = s
    s = _EMAIL.sub(PLACEHOLDER, s)
    s = _URL.sub(LINK_PLACEHOLDER, s)
    s = _SOCIAL.sub(PLACEHOLDER, s)
    s = _HANDLE.sub(PLACEHOLDER, s)
    s = _PHONE.sub(_redact_phone, s)
    return s, (s != original)


def scrub(s):
    """Solo testo pulito (comodo per i campi mostrati alla controparte)."""
    return scrub_text(s)[0]


def mask_worker_public(w: dict) -> dict:
    """Profilo worker mostrato a una venue PRIMA del contratto: niente telefono/email,
    bio ripulita dai contatti."""
    if not w:
        return w
    w = dict(w)
    w.pop("phone", None)
    w.pop("email", None)
    if w.get("bio"):
        w["bio"] = scrub(w["bio"])
    w["contact_locked"] = True
    return w


def mask_venue_public(v: dict) -> dict:
    """Profilo venue mostrato a un worker PRIMA del contratto: niente telefono/email/
    indirizzo esatto (resta la citta')."""
    if not v:
        return v
    v = dict(v)
    v.pop("phone", None)
    v.pop("email", None)
    if "address" in v:
        v["address"] = None
    v["contact_locked"] = True
    return v
