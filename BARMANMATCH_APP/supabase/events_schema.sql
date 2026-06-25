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
