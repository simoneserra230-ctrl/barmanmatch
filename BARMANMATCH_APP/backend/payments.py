"""
BarmanMatch — Stripe Connect dietro lo stato escrow del contratto.

Pattern "separate charges & transfers":
  fund     → Checkout Session a carico della venue per venue_total (gross+fee).
             I fondi restano sul saldo piattaforma (escrow). Il webhook
             checkout.session.completed porta il contratto a payment_status='held'.
  complete → Transfer di worker_payout al conto Connect del worker; la
             piattaforma trattiene fee_amount. payment_status='released'.
  cancel   → Refund del PaymentIntent della venue. payment_status='refunded'.

DEGRADAZIONE: se manca la lib `stripe` o STRIPE_SECRET_KEY, `enabled()` è False e
i router usano l'escrow SIMULATO (stato senza denaro). Così lo smoke test gira
senza Stripe e nulla si rompe.
"""

import os, json

try:
    import stripe as _stripe
    _LIB = True
except Exception:
    _stripe = None
    _LIB = False

STRIPE_SECRET = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
STRIPE_PRICE_VENUE = os.environ.get("STRIPE_PRICE_VENUE", "")   # price_... del piano struttura (subscription)
PUBLIC_URL = (os.environ.get("BMM_PUBLIC_URL")
              or os.environ.get("FRONTEND_ORIGIN", "http://localhost:5500").split(",")[0]).rstrip("/")


def enabled() -> bool:
    return _LIB and bool(STRIPE_SECRET)


def _s():
    _stripe.api_key = STRIPE_SECRET
    return _stripe


# ── Connect account del worker ───────────────────────────────────
def ensure_account(db, worker_id: str, email: str = "") -> str:
    s = _s()
    w = db.table("worker_profiles").select("stripe_account_id, email").eq("id", worker_id).single().execute().data or {}
    acct = w.get("stripe_account_id")
    if not acct:
        a = s.Account.create(type="express", email=w.get("email") or email or None,
                             capabilities={"transfers": {"requested": True}})
        acct = a.id
        db.table("worker_profiles").update({"stripe_account_id": acct}).eq("id", worker_id).execute()
    return acct


def onboarding_link(acct: str) -> str:
    s = _s()
    link = s.AccountLink.create(
        account=acct,
        refresh_url=PUBLIC_URL + "/app.html#worker",
        return_url=PUBLIC_URL + "/app.html#worker",
        type="account_onboarding",
    )
    return link.url


def account_ready(acct: str) -> bool:
    try:
        a = _s().Account.retrieve(acct)
        return bool(getattr(a, "payouts_enabled", False))
    except Exception:
        return False


# ── Subscription della STRUTTURA (venue paga) ────────────────────
def subscription_ready() -> bool:
    return enabled() and bool(STRIPE_PRICE_VENUE)


def create_subscription_checkout(venue_id: str, email: str = "") -> str:
    """Checkout Session in modalità subscription per la struttura. Ritorna l'URL Stripe.
    Il venue_id viaggia in metadata → il webhook attiva l'entitlement. Nessun pagamento fuori piattaforma."""
    if not STRIPE_PRICE_VENUE:
        raise RuntimeError("STRIPE_PRICE_VENUE non configurato")
    s = _s()
    sess = s.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": STRIPE_PRICE_VENUE, "quantity": 1}],
        customer_email=email or None,
        client_reference_id=venue_id,
        metadata={"venue_id": venue_id},
        subscription_data={"metadata": {"venue_id": venue_id}},
        success_url=PUBLIC_URL + "/app.html#venue",
        cancel_url=PUBLIC_URL + "/app.html#venue",
    )
    return sess.url


def cancel_subscription(subscription_id: str) -> bool:
    """Disdice una subscription (a fine periodo). Usato per la revoca lato piattaforma."""
    try:
        _s().Subscription.modify(subscription_id, cancel_at_period_end=True)
        return True
    except Exception:
        return False


# ── Escrow money movements ───────────────────────────────────────
def create_fund_checkout(contract: dict) -> str:
    """Checkout Session per la venue. Ritorna l'URL di pagamento Stripe."""
    s = _s()
    cents = int(round(float(contract.get("venue_total") or 0) * 100))
    sess = s.checkout.Session.create(
        mode="payment",
        line_items=[{
            "price_data": {"currency": "eur",
                           "product_data": {"name": "Turno %s · %s" % (contract.get("role", ""), contract.get("date", ""))},
                           "unit_amount": cents},
            "quantity": 1,
        }],
        metadata={"contract_id": contract["id"]},
        payment_intent_data={"metadata": {"contract_id": contract["id"]}},
        success_url=PUBLIC_URL + "/app.html#venue",
        cancel_url=PUBLIC_URL + "/app.html#venue",
    )
    return sess.url


def release(contract: dict, worker_account_id: str) -> str:
    """Transfer del worker_payout al conto Connect del worker. Ritorna transfer id."""
    s = _s()
    cents = int(round(float(contract.get("worker_payout") or 0) * 100))
    tr = s.Transfer.create(amount=cents, currency="eur", destination=worker_account_id,
                           metadata={"contract_id": contract["id"]})
    return tr.id


def refund(contract: dict) -> str:
    s = _s()
    pi = contract.get("stripe_payment_intent_id")
    if not pi:
        return ""
    r = s.Refund.create(payment_intent=pi, metadata={"contract_id": contract["id"]})
    return r.id


# ── Webhook ──────────────────────────────────────────────────────
def parse_webhook(payload: bytes, sig_header: str) -> dict:
    """Verifica (se c'è il secret) e ritorna l'evento Stripe come dict."""
    if STRIPE_WEBHOOK_SECRET and sig_header:
        return _s().Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    # dev senza secret: parse non verificato
    return json.loads(payload.decode("utf-8"))
