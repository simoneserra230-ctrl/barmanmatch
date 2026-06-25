-- BarmanMatch — Contratti tipo Deliveroo (additivo allo schema.sql)
-- Esegui DOPO schema.sql nel SQL Editor di Supabase (usa set_updated_at() già definita lì).
--
-- Un contratto è l'artefatto formale generato quando una venue conferma un
-- professionista su un turno: blocca tariffa/ore/compenso + termini, e richiede
-- la firma di ENTRAMBE le parti (worker + venue) per diventare 'active'.

CREATE TABLE IF NOT EXISTS contracts (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shift_id         UUID NOT NULL REFERENCES shifts(id) ON DELETE CASCADE,
    application_id   UUID NOT NULL REFERENCES shift_applications(id) ON DELETE CASCADE,
    venue_id         UUID NOT NULL REFERENCES venue_profiles(id) ON DELETE CASCADE,
    worker_id        UUID NOT NULL REFERENCES worker_profiles(id) ON DELETE CASCADE,
    -- snapshot economico/orario (congelato alla generazione)
    role             TEXT NOT NULL,
    date             DATE NOT NULL,
    start_time       TIME NOT NULL,
    end_time         TIME NOT NULL,
    hourly_rate      NUMERIC(8,2) NOT NULL,
    est_hours        NUMERIC(6,2) NOT NULL,
    actual_hours     NUMERIC(6,2),
    gross_total      NUMERIC(10,2) NOT NULL,   -- compenso lordo worker (rate*ore)
    fee_pct          NUMERIC(5,4) NOT NULL DEFAULT 0.12,
    fee_amount       NUMERIC(10,2) NOT NULL,   -- commissione piattaforma (a carico venue)
    venue_total      NUMERIC(10,2) NOT NULL,   -- gross + fee (quanto paga la venue)
    worker_payout    NUMERIC(10,2) NOT NULL,   -- = gross (quanto incassa il worker)
    terms            JSONB DEFAULT '{}'::jsonb, -- requirements, dress_code, cancellation_policy, payment_terms
    status           TEXT NOT NULL DEFAULT 'draft'
                     CHECK (status IN ('draft','active','completed','cancelled','disputed')),
    worker_signed    BOOLEAN DEFAULT FALSE,
    venue_signed     BOOLEAN DEFAULT TRUE,
    worker_signed_at TIMESTAMPTZ,
    venue_signed_at  TIMESTAMPTZ DEFAULT NOW(),
    activated_at     TIMESTAMPTZ,
    completed_at     TIMESTAMPTZ,
    cancelled_at     TIMESTAMPTZ,
    cancel_reason    TEXT,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    updated_at       TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (application_id)
);

CREATE INDEX IF NOT EXISTS idx_contracts_venue  ON contracts(venue_id);
CREATE INDEX IF NOT EXISTS idx_contracts_worker ON contracts(worker_id);
CREATE INDEX IF NOT EXISTS idx_contracts_status ON contracts(status);

CREATE TRIGGER trg_contracts_updated BEFORE UPDATE ON contracts
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ─── ROW LEVEL SECURITY ─────────────────────────────────────────
ALTER TABLE contracts ENABLE ROW LEVEL SECURITY;

-- Entrambe le parti leggono il proprio contratto
CREATE POLICY "contracts_party_read" ON contracts
    FOR SELECT USING (auth.uid() = venue_id OR auth.uid() = worker_id);
-- La venue genera/gestisce i contratti dei propri turni
CREATE POLICY "contracts_venue_write" ON contracts
    FOR ALL USING (auth.uid() = venue_id);
-- Il worker può aggiornare (firmare) il proprio contratto
CREATE POLICY "contracts_worker_update" ON contracts
    FOR UPDATE USING (auth.uid() = worker_id);
