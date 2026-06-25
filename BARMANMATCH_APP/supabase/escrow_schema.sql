-- BarmanMatch — Escrow pagamento + snapshot tariffa minima sul contratto.
-- Additivo: esegui DOPO contracts_schema.sql.
--
-- payment_status: pending → held (venue finanzia) → released (a turno completato)
--                 | refunded (annullo dopo finanziamento). Niente pagamenti fuori
--                 piattaforma: il completamento richiede lo stato 'held'.
-- Il movimento reale di denaro sarà gestito da Stripe Connect (TODO).

ALTER TABLE contracts ADD COLUMN IF NOT EXISTS payment_status TEXT DEFAULT 'pending'
    CHECK (payment_status IN ('pending','held','released','refunded'));
ALTER TABLE contracts ADD COLUMN IF NOT EXISTS payment_funded_at   TIMESTAMPTZ;
ALTER TABLE contracts ADD COLUMN IF NOT EXISTS payment_released_at TIMESTAMPTZ;
ALTER TABLE contracts ADD COLUMN IF NOT EXISTS min_hourly_rate     NUMERIC(8,2);
