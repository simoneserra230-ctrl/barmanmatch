-- BarmanMatch — Stripe Connect (additivo). Esegui DOPO contracts_schema.sql + escrow_schema.sql.
-- Riferimenti Stripe per il movimento reale dietro lo stato escrow del contratto.

ALTER TABLE worker_profiles ADD COLUMN IF NOT EXISTS stripe_account_id        TEXT;
ALTER TABLE contracts       ADD COLUMN IF NOT EXISTS stripe_payment_intent_id TEXT;
ALTER TABLE contracts       ADD COLUMN IF NOT EXISTS stripe_transfer_id       TEXT;
ALTER TABLE contracts       ADD COLUMN IF NOT EXISTS stripe_refund_id         TEXT;
