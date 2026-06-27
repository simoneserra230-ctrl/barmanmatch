# 🚀 BarmanMatch — Guida al deploy (Render backend + Vercel frontend)

> File di deploy GIA' pronti nel repo. Niente e' ancora pubblicato.
> Quando vuoi andare online (idealmente dopo aver comprato i domini — vedi
> `ECOSISTEMA_MAPPA_DOMINI.md`), segui questi passi. ~20 minuti.

Architettura: **Vercel** serve il frontend statico e fa da **proxy** delle API
verso **Render** (`/api/*` → backend). Cosi' il browser parla sempre con un solo
dominio: niente CORS, niente URL hardcoded in `app.html`. Il DB e' **Supabase**.

---

## 0) Prerequisiti
- Repo BarmanMatch su GitHub (gia' un repo git locale: fai `git push` su un remoto).
- Account **Supabase** (progetto `barmanmatch` gia' creato), **Render**, **Vercel**.
- Le chiavi sono nei tuoi `_SEGRETI_SkillSolutions/` — NON finiscono nel repo.

## 1) Database Supabase (una volta)
Nel progetto `barmanmatch` → SQL Editor → esegui `supabase/setup_all.sql`
(idempotente: crea tutte le tabelle, RLS, entitlement, chat, KYC).
> Sul progetto di sviluppo attuale e' gia' applicato.

## 2) Backend su Render (Blueprint)
1. Render → **New** → **Blueprint** → collega il repo. Render legge `render.yaml`.
2. Conferma il servizio `barmanmatch-api` (rootDir `BARMANMATCH_APP/backend`).
3. Imposta le **env** marcate `sync:false` (Dashboard → Environment):
   - `SUPABASE_URL` = https://gxapswdsxdhgdjuucrae.supabase.co
   - `SUPABASE_KEY` = **service_role** del progetto (segreto, solo backend)
   - `SUPABASE_JWT_SECRET` = (facoltativo; i token nuovi sono ES256 e si verificano via JWKS)
   - `BMM_ADMIN_EMAILS` = simoneserra230@gmail.com
   - `FRONTEND_ORIGIN` = (per ora `*`; dopo lo step 3 metti l'URL Vercel)
   - `BMM_PUBLIC_URL` = (dopo lo step 3: l'URL Vercel)
   - Stripe: lascia vuote finche' non attivi i pagamenti.
4. Deploy. Verifica: `https://<servizio>.onrender.com/health` → `{"status":"healthy"}`.
5. Copia l'URL del backend (es. `https://barmanmatch-api.onrender.com`).

## 3) Frontend su Vercel
1. Vercel → **Add New Project** → importa il repo.
2. **Root Directory** = `BARMANMATCH_APP/frontend`. Framework: **Other** (statico).
3. Apri `BARMANMATCH_APP/frontend/vercel.json` e sostituisci
   `REPLACE-WITH-RENDER-BACKEND.onrender.com` con l'host Render dello step 2.
   (commit + push: Vercel rideploya da solo)
4. Deploy. Ottieni l'URL Vercel (es. `https://barmanmatch.vercel.app`).

## 4) Richiudi il cerchio
- Su **Render** aggiorna `FRONTEND_ORIGIN` e `BMM_PUBLIC_URL` con l'URL Vercel → redeploy.
- Apri l'URL Vercel: registra una struttura + un lavoratore e prova il flusso.

## 5) Smoke test in produzione (facoltativo)
Gli script E2E locali (`scratchpad`) puntano al DB reale; per testare l'HTTP pubblico
basta registrarsi dall'app e fare: pubblica turno → candidatura → conferma →
contratto → firma → escrow → completa, + chat.

---

## Note
- **Hub link / cross-link ecosistema**: dentro `app.html` il link "✦ Hub" e i ritorni
  all'ecosistema sono **relativi** (validi in locale). In produzione (sottodomini separati)
  diventano URL assoluti: compila `ECOSISTEMA_MAPPA_DOMINI.md` e li allineo.
- **Stripe (dopo)**: quando attivi i pagamenti, imposta `STRIPE_SECRET_KEY` +
  `STRIPE_WEBHOOK_SECRET` su Render e configura il webhook
  `https://<backend>/api/payments/webhook` (evento `checkout.session.completed`).
  Senza Stripe, l'escrow gira in modalita' simulata (nessun denaro reale).
- **Accesso app da Hub (paganti + admin)**: il gate entitlement e' attivo
  (strutture: trial poi abbonamento; lavoratori gratis; tu admin bypassi). L'acquisto
  abbonamento via Stripe sara' l'ultimo pezzo; per ora l'admin attiva dal pannello.
- **Render free**: il servizio va in sleep dopo inattivita' (primo accesso lento).
