-- BarmanMatch — Chat in-app (anti-disintermediazione) + KYC light (P.IVA venue).
-- Additivo: esegui DOPO contracts_schema.sql (la chat e' legata al contratto).

-- ─── CHAT legata al contratto ───────────────────────────────────
CREATE TABLE IF NOT EXISTS messages (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id UUID NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
    sender_id   UUID NOT NULL,                 -- auth.users (parte del contratto)
    body        TEXT NOT NULL,                 -- gia' ripulito dallo scrub server-side
    flagged     BOOLEAN DEFAULT FALSE,         -- conteneva contatti rimossi
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_messages_contract ON messages(contract_id, created_at);

ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- Solo le due parti del contratto leggono/scrivono i messaggi (scrittura via backend service-role)
CREATE POLICY "messages_party_read" ON messages
    FOR SELECT USING (
        auth.uid() IN (
            SELECT venue_id FROM contracts WHERE id = contract_id
            UNION
            SELECT worker_id FROM contracts WHERE id = contract_id
        )
    );

-- ─── KYC light: P.IVA struttura ─────────────────────────────────
ALTER TABLE venue_profiles ADD COLUMN IF NOT EXISTS vat_number TEXT;
