-- ════════════════════════════════════════════════════════════
--  BarmanMatch — SETUP COMPLETO (esegui in un nuovo progetto Supabase)
--  Generato concatenando i 4 schema nell ordine corretto.
--  Fonte di verita = i singoli file; questo e solo per il setup one-shot.
-- ════════════════════════════════════════════════════════════

-- ===== 1) schema.sql =====
-- BarmanMatch MVP — Schema Supabase PostgreSQL
-- Esegui questo file nel SQL Editor di Supabase

-- ─── WORKER PROFILES ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS worker_profiles (
    id                      UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name               TEXT NOT NULL,
    email                   TEXT NOT NULL,
    phone                   TEXT,
    city                    TEXT NOT NULL,
    roles                   TEXT[] NOT NULL DEFAULT '{}',
    skills                  TEXT[] DEFAULT '{}',
    certifications          TEXT[] DEFAULT '{}',
    years_experience        INTEGER DEFAULT 0,
    bio                     TEXT,
    hourly_rate_min         NUMERIC(8,2),
    -- Stats denormalizzate per query veloci
    rating_avg              NUMERIC(3,2) DEFAULT 5.0,
    rating_count            INTEGER DEFAULT 0,
    completion_rate         NUMERIC(5,2) DEFAULT 100.0,
    no_show_count           INTEGER DEFAULT 0,
    total_shifts_completed  INTEGER DEFAULT 0,
    avg_response_time_mins  INTEGER DEFAULT 60,
    -- Badge
    badge_top_rated         BOOLEAN DEFAULT FALSE,
    badge_no_show_zero      BOOLEAN DEFAULT TRUE,
    badge_fast_responder    BOOLEAN DEFAULT FALSE,
    -- Stato
    is_verified             BOOLEAN DEFAULT FALSE,
    is_active               BOOLEAN DEFAULT TRUE,
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    updated_at              TIMESTAMPTZ DEFAULT NOW()
);

-- ─── VENUE PROFILES ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS venue_profiles (
    id          UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    name        TEXT NOT NULL,
    email       TEXT NOT NULL,
    phone       TEXT,
    city        TEXT NOT NULL,
    venue_type  TEXT NOT NULL CHECK (venue_type IN ('hotel','ristorante','resort','catering','event_venue','bar','altro')),
    address     TEXT,
    description TEXT,
    plan        TEXT DEFAULT 'starter' CHECK (plan IN ('starter','pro','business','enterprise')),
    is_verified BOOLEAN DEFAULT FALSE,
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- ─── SHIFTS (TURNI) ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS shifts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    venue_id        UUID NOT NULL REFERENCES venue_profiles(id) ON DELETE CASCADE,
    role            TEXT NOT NULL,
    date            DATE NOT NULL,
    start_time      TIME NOT NULL,
    end_time        TIME NOT NULL,
    hourly_rate     NUMERIC(8,2) NOT NULL,
    city            TEXT NOT NULL,
    requirements    TEXT[] DEFAULT '{}',
    description     TEXT,
    dress_code      TEXT,
    spots           INTEGER DEFAULT 1,
    status          TEXT DEFAULT 'open' CHECK (status IN ('open','filled','cancelled','completed')),
    is_urgent       BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ─── SHIFT APPLICATIONS ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS shift_applications (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shift_id            UUID NOT NULL REFERENCES shifts(id) ON DELETE CASCADE,
    worker_id           UUID NOT NULL REFERENCES worker_profiles(id) ON DELETE CASCADE,
    status              TEXT DEFAULT 'pending' CHECK (status IN ('pending','confirmed','rejected','completed','no_show','withdrawn')),
    match_score         NUMERIC(5,2),
    applied_at          TIMESTAMPTZ DEFAULT NOW(),
    confirmed_at        TIMESTAMPTZ,
    contract_accepted   BOOLEAN DEFAULT FALSE,
    contract_accepted_at TIMESTAMPTZ,
    UNIQUE(shift_id, worker_id)
);

-- ─── RATINGS ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ratings (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shift_id            UUID NOT NULL REFERENCES shifts(id),
    application_id      UUID NOT NULL REFERENCES shift_applications(id),
    rater_type          TEXT NOT NULL CHECK (rater_type IN ('venue','worker')),
    rater_id            UUID NOT NULL,
    ratee_id            UUID NOT NULL,
    score               INTEGER NOT NULL CHECK (score BETWEEN 1 AND 5),
    comment             TEXT,
    -- Dimensioni per venue→worker
    punctuality         INTEGER CHECK (punctuality BETWEEN 1 AND 5),
    professionalism     INTEGER CHECK (professionalism BETWEEN 1 AND 5),
    skill_level         INTEGER CHECK (skill_level BETWEEN 1 AND 5),
    -- Dimensioni per worker→venue
    work_environment    INTEGER CHECK (work_environment BETWEEN 1 AND 5),
    payment_punctuality INTEGER CHECK (payment_punctuality BETWEEN 1 AND 5),
    is_published        BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(application_id, rater_type)
);

-- ─── VENUE FAVORITES ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS venue_favorites (
    venue_id    UUID NOT NULL REFERENCES venue_profiles(id) ON DELETE CASCADE,
    worker_id   UUID NOT NULL REFERENCES worker_profiles(id) ON DELETE CASCADE,
    added_at    TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (venue_id, worker_id)
);

-- ─── INDEXES ────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_shifts_open          ON shifts(city, role, date) WHERE status = 'open';
CREATE INDEX IF NOT EXISTS idx_shifts_venue         ON shifts(venue_id);
CREATE INDEX IF NOT EXISTS idx_apps_worker          ON shift_applications(worker_id);
CREATE INDEX IF NOT EXISTS idx_apps_shift           ON shift_applications(shift_id);
CREATE INDEX IF NOT EXISTS idx_ratings_ratee        ON ratings(ratee_id);
CREATE INDEX IF NOT EXISTS idx_ratings_application  ON ratings(application_id);

-- ─── UPDATED_AT TRIGGER ─────────────────────────────────────────
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_worker_updated  BEFORE UPDATE ON worker_profiles  FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_venue_updated   BEFORE UPDATE ON venue_profiles   FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_shift_updated   BEFORE UPDATE ON shifts           FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ─── ROW LEVEL SECURITY ─────────────────────────────────────────
ALTER TABLE worker_profiles  ENABLE ROW LEVEL SECURITY;
ALTER TABLE venue_profiles   ENABLE ROW LEVEL SECURITY;
ALTER TABLE shifts            ENABLE ROW LEVEL SECURITY;
ALTER TABLE shift_applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE ratings           ENABLE ROW LEVEL SECURITY;
ALTER TABLE venue_favorites   ENABLE ROW LEVEL SECURITY;

-- Worker può leggere il proprio profilo e aggiornarlo
CREATE POLICY "worker_self" ON worker_profiles
    FOR ALL USING (auth.uid() = id);
-- Chiunque autenticato può vedere i profili worker (per matching)
CREATE POLICY "worker_read_all" ON worker_profiles
    FOR SELECT USING (auth.role() = 'authenticated');

-- Venue può leggere il proprio profilo
CREATE POLICY "venue_self" ON venue_profiles
    FOR ALL USING (auth.uid() = id);
-- Chiunque autenticato può vedere i venue (per info turni)
CREATE POLICY "venue_read_all" ON venue_profiles
    FOR SELECT USING (auth.role() = 'authenticated');

-- Turni: venue crea i propri, tutti leggono i turni aperti
CREATE POLICY "shifts_venue_write" ON shifts
    FOR ALL USING (auth.uid() = venue_id);
CREATE POLICY "shifts_read_open" ON shifts
    FOR SELECT USING (auth.role() = 'authenticated');

-- Applicazioni: worker crea le proprie, venue vede quelle dei propri turni
CREATE POLICY "apps_worker_insert" ON shift_applications
    FOR INSERT WITH CHECK (auth.uid() = worker_id);
CREATE POLICY "apps_worker_read" ON shift_applications
    FOR SELECT USING (auth.uid() = worker_id);
CREATE POLICY "apps_venue_manage" ON shift_applications
    FOR ALL USING (
        auth.uid() IN (SELECT venue_id FROM shifts WHERE id = shift_id)
    );

-- Rating: solo chi è coinvolto può inserire
CREATE POLICY "ratings_insert" ON ratings
    FOR INSERT WITH CHECK (auth.uid() = rater_id);
CREATE POLICY "ratings_read_published" ON ratings
    FOR SELECT USING (is_published = TRUE OR auth.uid() = rater_id);

-- Favorites: solo la venue gestisce le proprie
CREATE POLICY "favorites_venue" ON venue_favorites
    FOR ALL USING (auth.uid() = venue_id);


-- ===== 2) contracts_schema.sql =====
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


-- ===== 3) events_schema.sql =====
-- BarmanMatch — Eventi ("Booking.com degli eventi") + Aziende + Prelazione BAD
-- Additivo: esegui DOPO schema.sql (usa set_updated_at()).
--
-- Modello:
--   events    = ingaggi prenotabili (matrimonio, aziendale...) pubblicati da un owner.
--   companies = aziende/agenzie che STAFFano gli eventi (BAD è una di queste, con priorità).
--   Ogni evento apre con una FINESTRA DI PRELAZIONE (priority_until): finché è attiva,
--   solo le aziende is_priority=true (es. BAD) possono "claimare" l'evento; dopo, tutte.
--   Le esigenze di staff di un evento sono shifts collegati via shifts.event_id.

CREATE TABLE IF NOT EXISTS companies (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_uid   UUID NOT NULL,                  -- auth.users che gestisce l'azienda
    name        TEXT NOT NULL,
    city        TEXT,
    is_priority BOOLEAN DEFAULT FALSE,          -- BAD = TRUE (precedenza sugli eventi)
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (owner_uid)
);

CREATE TABLE IF NOT EXISTS events (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id           UUID NOT NULL,           -- chi pubblica l'evento (cliente/venue)
    title              TEXT NOT NULL,
    event_type         TEXT NOT NULL DEFAULT 'privato',  -- matrimonio|aziendale|privato|catering|altro
    date               DATE NOT NULL,
    start_time         TIME NOT NULL,
    end_time           TIME NOT NULL,
    city               TEXT NOT NULL,
    guests             INTEGER,
    description        TEXT,
    budget             NUMERIC(10,2),
    priority_until     TIMESTAMPTZ NOT NULL DEFAULT NOW(),  -- fine finestra prelazione
    status             TEXT NOT NULL DEFAULT 'open'
                       CHECK (status IN ('open','claimed','staffing','completed','cancelled')),
    claimed_by_company UUID REFERENCES companies(id),
    claimed_at         TIMESTAMPTZ,
    cancel_reason      TEXT,
    created_at         TIMESTAMPTZ DEFAULT NOW(),
    updated_at         TIMESTAMPTZ DEFAULT NOW()
);

-- Le esigenze di staff di un evento sono shifts collegati (additivo)
ALTER TABLE shifts ADD COLUMN IF NOT EXISTS event_id UUID REFERENCES events(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_events_open   ON events(city, date) WHERE status = 'open';
CREATE INDEX IF NOT EXISTS idx_events_owner  ON events(owner_id);
CREATE INDEX IF NOT EXISTS idx_shifts_event  ON shifts(event_id);

CREATE TRIGGER trg_events_updated    BEFORE UPDATE ON events    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_companies_updated BEFORE UPDATE ON companies FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ─── ROW LEVEL SECURITY ─────────────────────────────────────────
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE events    ENABLE ROW LEVEL SECURITY;

CREATE POLICY "companies_self"     ON companies FOR ALL    USING (auth.uid() = owner_uid);
CREATE POLICY "companies_read_all" ON companies FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "events_owner_write" ON events FOR ALL    USING (auth.uid() = owner_id);
CREATE POLICY "events_read_all"    ON events FOR SELECT USING (auth.role() = 'authenticated');
-- Il claim aggiorna l'evento: la regola di prelazione è applicata nel backend.
CREATE POLICY "events_claim_update" ON events FOR UPDATE USING (auth.role() = 'authenticated');


-- ===== 4) escrow_schema.sql =====
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


-- ===== 5) payments_stripe_schema.sql =====
-- BarmanMatch — Stripe Connect (additivo). Riferimenti Stripe per il movimento
-- reale dietro lo stato escrow del contratto.

ALTER TABLE worker_profiles ADD COLUMN IF NOT EXISTS stripe_account_id        TEXT;
ALTER TABLE contracts       ADD COLUMN IF NOT EXISTS stripe_payment_intent_id TEXT;
ALTER TABLE contracts       ADD COLUMN IF NOT EXISTS stripe_transfer_id       TEXT;
ALTER TABLE contracts       ADD COLUMN IF NOT EXISTS stripe_refund_id         TEXT;


-- ===== 6) entitlements_schema.sql =====
-- BarmanMatch — Entitlement / abbonamento STRUTTURE (additivo).
-- Lavoratori gratis; le venue hanno bisogno di status attivo (trial o abbonamento)
-- per pubblicare turni / assumere. Admin bypassa. Stripe scrivera' qui dopo.

CREATE TABLE IF NOT EXISTS venue_entitlements (
    venue_id               UUID PRIMARY KEY REFERENCES venue_profiles(id) ON DELETE CASCADE,
    plan                   TEXT NOT NULL DEFAULT 'none',
    status                 TEXT NOT NULL DEFAULT 'inactive'
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

ALTER TABLE venue_entitlements ENABLE ROW LEVEL SECURITY;

CREATE POLICY "entitlements_self_read" ON venue_entitlements
    FOR SELECT USING (auth.uid() = venue_id);

