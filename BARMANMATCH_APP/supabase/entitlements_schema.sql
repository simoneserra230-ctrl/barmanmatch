-- BarmanMatch — Entitlement / abbonamento STRUTTURE (additivo).
-- Esegui DOPO schema.sql (usa set_updated_at()).
--
-- Modello: i LAVORATORI usano l'app gratis. Le STRUTTURE (venue) hanno bisogno
-- di un entitlement ATTIVO (trial o abbonamento) per le AZIONI A PAGAMENTO
-- (pubblicare turni, generare contratti / assumere). L'admin bypassa tutto.
-- L'aggancio a Stripe (subscription + webhook) arrivera' dopo: il webhook
-- scrivera' status='active' / current_period_end / stripe_* qui.

CREATE TABLE IF NOT EXISTS venue_entitlements (
    venue_id               UUID PRIMARY KEY REFERENCES venue_profiles(id) ON DELETE CASCADE,
    plan                   TEXT NOT NULL DEFAULT 'none',      -- none | trial | pro
    status                 TEXT NOT NULL DEFAULT 'inactive'   -- inactive | trialing | active | past_due | cancelled
                           CHECK (status IN ('inactive','trialing','active','past_due','cancelled')),
    trial_ends_at          TIMESTAMPTZ,
    current_period_end     TIMESTAMPTZ,
    stripe_customer_id     TEXT,
    stripe_subscription_id TEXT,
    created_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at             TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_entitlements_status ON venue_entitlements(status);

CREATE TRIGGER trg_entitlements_updated BEFORE UPDATE ON venue_entitlements
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ─── ROW LEVEL SECURITY ─────────────────────────────────────────
ALTER TABLE venue_entitlements ENABLE ROW LEVEL SECURITY;

-- La struttura legge il proprio entitlement (la scrittura passa dal backend service-role)
CREATE POLICY "entitlements_self_read" ON venue_entitlements
    FOR SELECT USING (auth.uid() = venue_id);
