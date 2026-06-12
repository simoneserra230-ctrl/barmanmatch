# HospitaLink — Piattaforma di Staffing per il Settore Hospitality
## Product Design Document v1.0

---

## 1. Executive Summary

**HospitaLink** è una piattaforma digitale two-sided marketplace che connette strutture ricettive (hotel, resort, ristoranti, catering, event venue) con professionisti del settore hospitality disponibili per turni flessibili, contratti stagionali o posizioni permanenti.

Il modello si ispira a due benchmark consolidati:

- **Deliveroo** → per il meccanismo di onboarding rapido dei lavoratori, la gestione gig/flessibile, l'algoritmo di matching e il sistema di turni on-demand.
- **Booking.com** → per l'interfaccia partner (extranet), il sistema di rating multi-livello, il ranking algoritmico dei profili, i filtri di ricerca avanzati e la fiducia generata attraverso recensioni verificate.

---

## 2. Analisi dei Modelli di Riferimento

### 2.1 — Deliveroo: Il Modello di Onboarding e Workforce

**Meccanismo core estratto:**

Deliveroo ha standardizzato il processo di reclutamento di massa attraverso un funnel digitale veloce e scalabile. I punti chiave applicabili a HospitaLink sono:

- **Onboarding in 30 minuti**: il rider completa registrazione, caricamento documenti, video tutorial su sicurezza e procedure, e diventa operativo nella stessa giornata. Questo riduce il "time-to-first-shift" a meno di 24 ore.
- **Modello self-employed / freelance verificato**: i lavoratori operano come contraenti indipendenti, con piena flessibilità oraria. Nessun obbligo di accettare turni, nessuna esclusività di piattaforma.
- **Algoritmo di assegnazione turni**: quando una struttura pubblica un bisogno, il sistema notifica i worker disponibili nella zona in base a skill, prossimità e rating. L'accettazione è volontaria.
- **Candidate experience come leva di brand**: Deliveroo misura il Net Promoter Score dei candidati (anche quelli non assunti), trattando ogni touchpoint del funnel come momento di costruzione del brand employer.
- **Crescita metrica-driven**: il processo di recruiting è monitorato con KPI precisi (time-in-process, acceptance rate, no-show rate) e ottimizzato continuamente.
- **Scalabilità geografica**: il modello si replica identicamente in ogni nuovo mercato — quando Deliveroo entra in una città, i primi hired sono operativi da settimana 1.

**Criticità da correggere per HospitaLink:**

Il modello gig puro di Deliveroo è stato oggetto di controversie legali sul tema del lavoro autonomo. HospitaLink adotterà un modello ibrido che prevede sia profili freelance (per turni singoli) che contratti a tempo determinato o indeterminato intermediati dalla piattaforma, adeguati alla normativa italiana ed europea (D.Lgs. 81/2015, Decreto Dignità, direttiva UE sul lavoro tramite piattaforme).

---

### 2.2 — Booking.com: Il Modello di Marketplace e Trust

**Meccanismo core estratto:**

Booking.com ha costruito il suo vantaggio competitivo su un sistema di fiducia bilaterale — tra viaggiatori e strutture — attraverso strumenti specifici che HospitaLink può riadattare:

- **Extranet partner (→ Dashboard struttura)**: pannello di controllo dedicato alle strutture per gestire disponibilità, tariffe, profili e prenotazioni. Ogni hotel gestisce autonomamente il proprio "inventario". In HospitaLink, ogni struttura gestisce il proprio fabbisogno di personale, i turni aperti, le offerte e il budget.
- **Sistema di rating a più livelli**: Booking.com analizza oltre 400 parametri per assegnare un punteggio di qualità. In HospitaLink, sia i lavoratori che le strutture ricevono un rating composto da: puntualità, qualità del servizio, professionalità, numero di turni completati, no-show rate.
- **Algoritmo di ranking personalizzato**: la posizione nei risultati di ricerca su Booking.com varia per ogni utente in base a date, nazionalità, storico di prenotazioni e comportamento di ricerca. In HospitaLink, il ranking dei profili dei lavoratori nelle ricerche delle strutture varierà in base a: tipo di struttura, ruolo richiesto, disponibilità, distanza, valutazioni pregresse e storico di collaborazioni.
- **Smart Filter / AI-powered search**: Booking.com ha introdotto filtri AI che permettono di descrivere la proprietà ideale in linguaggio naturale. HospitaLink implementerà una ricerca intelligente dove la struttura può scrivere "cameriere esperto sala fine dining per sabato sera a Milano" e il sistema applica automaticamente i filtri pertinenti.
- **Sistema di recensioni verificate**: solo chi ha effettivamente completato un turno/collaborazione può lasciare una recensione. Questo garantisce l'autenticità e previene abusi.
- **Opportunity Center**: Booking.com suggerisce alle strutture azioni specifiche per migliorare il ranking (aggiungere foto, completare il profilo, attivare promozioni). HospitaLink offrirà un "Profile Booster" che suggerisce ai lavoratori come rendere il proprio profilo più attrattivo (certificazioni mancanti, video di presentazione, disponibilità da ampliare).
- **Genius Program (→ Verified Pro)**: le strutture che mantengono alti standard ottengono badge di visibilità. In HospitaLink, i lavoratori con track record eccellente ottengono badge "Top Rated", "Fast Responder", "No-Show Zero".

---

## 3. Architettura della Piattaforma

### 3.1 — Attori del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                        HOSPITALINK                              │
│                                                                 │
│   [STRUTTURE]          [PIATTAFORMA]         [LAVORATORI]       │
│   Hotel                Matching Engine       Chef               │
│   Resort               Rating System         Cameriere/a        │
│   Ristoranti           Payment Gateway       Receptionist       │
│   Event Venue          Compliance Layer      Housekeeping        │
│   Catering             Analytics             Bartender           │
│   SPA / Wellness       Notification Hub      Event Staff         │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 — Tipologie di Ingaggio

| Tipo | Durata | Modello Contrattuale | Esempi |
|---|---|---|---|
| **On-Demand** | Turno singolo (4–12h) | Freelance / P.IVA | Rinforzo weekend, evento |
| **Short-Term** | 1 settimana – 3 mesi | Contratto a termine intermediato | Stagione estiva, fiera |
| **Seasonal** | 3–6 mesi | Contratto stagionale | Apertura stagione hotel |
| **Permanent** | Indeterminato | Assunzione diretta via piattaforma | Talent acquisition tradizionale |

---

## 4. Funzionalità Chiave — Lato Lavoratore

### 4.1 — Onboarding (ispirato a Deliveroo)

**Fase 1 — Registrazione (< 10 min)**
- Inserimento dati anagrafici e contatti
- Upload documento identità + codice fiscale
- Selezione ruolo/i di competenza (da taxonomy hospitality standardizzata)
- Dichiarazione disponibilità settimanale

**Fase 2 — Verifica (automatica + manuale, 24–48h)**
- Verifica identità (OCR + liveness check)
- Verifica titoli di studio e certificazioni (HACCP, lingua, somministrazione alcolici, ecc.)
- Background check opzionale per strutture premium
- Approvazione profilo e attivazione account

**Fase 3 — Onboarding digitale (30 min)**
- Video tutorial su standard hospitality della piattaforma
- Quiz di comprensione (soglia minima 70%)
- Firma contratto quadro digitale (firma elettronica avanzata)
- Collegamento IBAN per pagamenti

**Fase 4 — Go Live**
- Profilo pubblico attivato
- Notifiche per turni compatibili abilitate
- Accesso alla dashboard personale

---

### 4.2 — Profilo Lavoratore (ispirato a Booking.com)

Il profilo è il "listing" del lavoratore. Ogni elemento contribuisce al punteggio di qualità e alla visibilità nei risultati di ricerca.

```
┌──────────────────────────────────────────────┐
│  [FOTO PROFESSIONALE]   Marco Rossi           │
│                         ★★★★☆ 4.7 (83 turni) │
│                         🏅 Top Rated          │
│                         ✅ No-Show Zero        │
│                         ⚡ Fast Responder      │
├──────────────────────────────────────────────┤
│  RUOLI        Maître · Sommelier · Caposala   │
│  LINGUA       ITA ●●●●● | ENG ●●●●○ | FRA ●●●○○ │
│  ZONA         Milano e provincia (30 km)      │
│  DISPONIBILE  Lun–Ven | Weekend | Notti       │
├──────────────────────────────────────────────┤
│  CERTIFICAZIONI                               │
│  ✓ HACCP     ✓ Sommelier FISAR  ✓ Wine Set   │
├──────────────────────────────────────────────┤
│  ESPERIENZE RECENTI (verificate)              │
│  Hotel Excelsior Milano ★★★★★                │
│  "Professionale, puntuale, ottima presenza"  │
│  Ristorante Borghese Roma ★★★★☆               │
│  ...                                          │
├──────────────────────────────────────────────┤
│  STATS                                        │
│  Tasso accettazione turni:  92%               │
│  Tasso completamento:       99%               │
│  Tempo medio risposta:      < 2h              │
└──────────────────────────────────────────────┘
```

---

### 4.3 — App Lavoratore — Feature Set

- **Feed turni disponibili**: lista turni compatibili con disponibilità, zona e skill, ordinati per pertinenza algoritmica
- **Accetta/Rifiuta turno**: con un tap, senza penalità per il rifiuto (entro finestra temporale)
- **Calendario disponibilità**: impostazione weekly/biweekly, blocco date, modifica real-time
- **Notifiche push urgenti**: per turni last-minute (con premio economico integrato)
- **Wallet e pagamenti**: visualizzazione guadagni, storico turni, richiesta anticipo, download buste paga
- **Chat con struttura**: messaggistica in-app pre-turno per briefing e logistica
- **Check-in digitale**: geolocalizzato all'inizio e fine turno (per validazione ore lavorate)
- **Profile Booster**: suggerimenti attivi per migliorare il ranking del profilo
- **Formazione**: accesso a micro-corsi certificati (upsell di skill, aumento tariffa oraria)

---

## 5. Funzionalità Chiave — Lato Struttura

### 5.1 — Dashboard Struttura (Extranet, ispirata a Booking.com)

La dashboard è il pannello di controllo completo per gestire il fabbisogno di personale, ispirato direttamente all'Extranet di Booking.com.

**Sezioni principali:**

```
DASHBOARD STRUTTURA
│
├── 📋 TURNI APERTI          → Crea, gestisci, cancella richieste di personale
├── 👥 ROSTER ATTIVO         → Chi lavora oggi / questa settimana
├── ⭐ LE MIE PREFERITE      → Salva lavoratori affidabili per ricontattarli
├── 📊 ANALYTICS             → KPI: fill rate, no-show, costo medio ora, rating dato
├── 💬 MESSAGGI              → Chat con i lavoratori confermati
├── 💳 FATTURAZIONE          → Riepilogo costi, download fatture, piano abbonamento
├── 🔔 OPPORTUNITY CENTER    → Suggerimenti per ridurre i tempi di fill e migliorare i match
└── ⚙️  IMPOSTAZIONI          → Profilo struttura, requisiti standard, preferenze matching
```

### 5.2 — Pubblicazione di un Turno

**Form strutturato (< 5 min):**

1. **Ruolo richiesto** (selezione da taxonomy: receptionist, F&B manager, chef de rang, housekeeping, ecc.)
2. **Data e orario** (con opzione ripetizione settimanale)
3. **Durata e break** (ore minime garantite)
4. **Tariffa oraria** (il sistema suggerisce il range di mercato per ruolo e città)
5. **Requisiti obbligatori** (HACCP, lingua, esperienza minima in anni)
6. **Requisiti preferenziali** (esperienza in strutture simili, soft skill, certificazioni extra)
7. **Dress code / divisa** (la struttura fornisce o il lavoratore porta)
8. **Note operative** (briefing, parcheggio, accesso, referente on-site)
9. **Modalità matching**: automatico (il sistema propone profili) / manuale (la struttura sfoglia e invita)

### 5.3 — Motore di Matching (ispirato all'algoritmo Booking.com + Deliveroo)

Il ranking dei profili proposti alla struttura è calcolato da un modello di rilevanza personalizzata che considera:

**Fattori di pertinenza:**
- Corrispondenza ruolo/skill richiesti
- Disponibilità confermata per la data/fascia oraria
- Distanza dalla struttura (raggio configurabile)
- Lingua richiesta + livello certificato

**Fattori di qualità (storico):**
- Rating medio ricevuto dalle strutture (pesato per recency)
- Tasso di accettazione e completamento turni
- No-show rate storico (penalizzante)
- Numero totale di turni completati (seniority sulla piattaforma)
- Collaborazioni pregresse con la struttura (priorità alle "preferite")

**Fattori comportamentali:**
- Tempo medio di risposta alle richieste
- Completezza del profilo
- Aggiornamento recente delle disponibilità
- Partecipazione a programmi formativi sulla piattaforma

**Output:** lista ordinata di profili compatibili con score composito visibile alla struttura (non al lavoratore, per evitare gaming).

---

### 5.4 — Sistema di Rating Bidirezionale (ispirato a Booking.com)

Dopo ogni turno completato, sia la struttura che il lavoratore lasciano una valutazione. Le recensioni sono verificate (solo chi ha effettivamente completato il turno può valutare).

**Struttura della valutazione — Da struttura a lavoratore:**
- Puntualità (1–5)
- Competenza tecnica (1–5)
- Presentazione e cura dell'immagine (1–5)
- Capacità relazionale con il team (1–5)
- Testo libero (opzionale, max 300 caratteri)

**Struttura della valutazione — Da lavoratore a struttura:**
- Organizzazione e comunicazione (1–5)
- Rispetto degli orari e delle condizioni concordate (1–5)
- Ambiente di lavoro (1–5)
- Testo libero (opzionale, max 300 caratteri)

**Gestione abusi:**
- Recensioni anonime tra le parti fino a pubblicazione simultanea (nessuna influenza reciproca)
- Sistema di segnalazione e moderazione per recensioni improprie
- Possibilità di risposta pubblica da parte della struttura (come su Booking.com)

---

## 6. Modello Economico

### 6.1 — Revenue Streams

| Stream | Modello | Dettaglio |
|---|---|---|
| **Commissione per turno** | % sul valore del turno | 15–20% a carico della struttura su ogni turno completato |
| **Abbonamento struttura** | SaaS mensile/annuale | Tier base (gratuito, commissioni alte), Pro, Enterprise |
| **Featured placement** | Pay-per-visibility | Strutture che vogliono visibilità premium per le loro offerte |
| **Formazione** | Marketplace corsi | Revenue share su micro-corsi certificati acquistati dai lavoratori |
| **Talent Acquisition** | Fee di placement | Fee una tantum per assunzioni permanenti intermedie dalla piattaforma |
| **API / Integrazione PMS** | Licensing B2B | Connessione con Property Management System degli hotel |

### 6.2 — Pricing Strutture (Piano Abbonamento)

| Piano | Mensile | Commissione turni | Feature chiave |
|---|---|---|---|
| **Starter** | Gratuito | 20% | Fino a 5 turni/mese, matching automatico |
| **Pro** | €99/mese | 15% | Turni illimitati, preferite illimitate, analytics base |
| **Business** | €299/mese | 12% | Multi-sede, API PMS, account manager dedicato |
| **Enterprise** | Custom | 8–10% | White label, SLA garantito, onboarding dedicato |

---

## 7. Compliance e Framework Legale (Italia/UE)

La piattaforma deve operare rispettando il quadro normativo vigente:

- **D.Lgs. 81/2015 (Jobs Act)** — regolamentazione del lavoro tramite piattaforme digitali
- **Direttiva UE 2024/2831** — trasparenza algoritmica e diritti lavoratori piattaforme (in recepimento)
- **GDPR** — trattamento dati personali lavoratori e strutture
- **INAIL e contributi INPS** — la piattaforma fornisce copertura assicurativa per turni on-demand (modello DAS o assicurazione per singola prestazione)
- **Contratto Collettivo Nazionale Turismo** — i compensi minimi per ruolo devono rispettare i minimi tabellari CCNL Turismo/Pubblici Esercizi
- **Fatturazione elettronica** — integrazione SDI per la fatturazione B2B e per i lavoratori con P.IVA

**Modello contrattuale consigliato per turni on-demand:**
Utilizzo del contratto di prestazione occasionale (ex voucher) o contratto a chiamata (intermittente) per collaboratori non esclusivi, con gestione automatizzata dalla piattaforma.

---

## 8. User Experience — Flussi Chiave

### 8.1 — Flusso: Struttura pubblica un turno urgente

```
Struttura apre app → Tap "Turno urgente" → Compila form (3 min) →
Sistema lancia matching → Notifica push a top-20 lavoratori compatibili →
Primo ad accettare → Conferma automatica → Chat briefing → 
Check-in geolocalizzato → Fine turno → Rating reciproco →
Pagamento automatico entro 24h
```

### 8.2 — Flusso: Lavoratore cerca turni per il weekend

```
Lavoratore apre app → Feed turni disponibili (filtro: venerdì–domenica) →
Sfoglia lista ordinata per pertinenza e tariffa → Tap su turno →
Dettaglio: struttura, ruolo, orario, paga, distanza, rating struttura →
Accetta → Confermato → Promemoria automatico 2h prima → 
Check-in → Turno → Check-out → Valuta la struttura → Ricevi valutazione
```

### 8.3 — Flusso: Struttura costruisce il proprio roster preferito

```
Struttura completa 3 turni con Mario B. → Lo aggiunge alle Preferite →
Al prossimo turno aperto, Mario riceve notifica prioritaria →
Struttura può anche inviare invito diretto a Mario senza pubblicare l'offerta →
Nel tempo, costruisce un pool di 15–20 lavoratori fidati ricontattabili on-demand
```

---

## 9. Stack Tecnologico Consigliato

| Layer | Tecnologia | Motivazione |
|---|---|---|
| **Frontend Web** | Next.js + TypeScript | SSR per SEO profili lavoratori |
| **App Mobile** | React Native | iOS + Android da singolo codebase |
| **Backend API** | Node.js + Express o FastAPI (Python) | Scalabilità microservizi |
| **Database** | PostgreSQL + Redis | Relazionale + cache per matching real-time |
| **Matching Engine** | Python (scikit-learn / custom scoring) | Modello di ranking personalizzato |
| **Notifiche push** | Firebase Cloud Messaging | Cross-platform, affidabile |
| **Pagamenti** | Stripe Connect | Marketplace payments, split automatico |
| **Identità / KYC** | Onfido o Jumio | Verifica documenti e liveness check |
| **Chat** | Stream (GetStream.io) | Messaggistica in-app scalabile |
| **Geolocalizzazione** | Google Maps Platform | Check-in, distanza, zone di copertura |
| **Storage** | AWS S3 | Documenti, foto profilo, certificati |
| **Analytics** | Mixpanel + Metabase | Product analytics + BI interno |

---

## 10. KPI e Metriche di Successo

### Lato Lavoratori
- **Time to first shift**: ore dalla registrazione al primo turno accettato (target: < 48h)
- **Acceptance rate**: % turni accettati su turni ricevuti (target: > 60%)
- **No-show rate**: % turni accettati e non presentati (target: < 3%)
- **Retention rate 90gg**: % lavoratori attivi dopo 90 giorni dall'onboarding

### Lato Strutture
- **Fill rate**: % turni aperti coperti entro 4h dalla pubblicazione (target: > 85%)
- **Repeat hire rate**: % strutture che riutilizzano la piattaforma nel mese successivo
- **Time to fill**: minuti medi dalla pubblicazione alla conferma del lavoratore
- **NPS strutture**: Net Promoter Score mensile

### Piattaforma
- **GMV (Gross Merchandise Value)**: valore totale ore lavorate intermediate
- **Take rate**: commissione media effettiva / GMV
- **Turni per lavoratore attivo/mese**: densità di utilizzo
- **Rating medio della piattaforma**: qualità percepita da entrambi i lati

---

## 11. Roadmap di Sviluppo

### Fase 1 — MVP (mesi 1–4)
- [ ] Onboarding lavoratori (registrazione, verifica, profilo base)
- [ ] Dashboard struttura (pubblicazione turni, matching automatico)
- [ ] Rating post-turno (solo struttura → lavoratore)
- [ ] Pagamenti (Stripe Connect, pagamento settimanale)
- [ ] App mobile (iOS + Android, feature set core)
- [ ] Lancio pilota: 1 città (Milano o Roma), 3 verticali (hotel, ristoranti, eventi)

### Fase 2 — Growth (mesi 5–9)
- [ ] Rating bidirezionale e recensioni pubbliche
- [ ] Roster preferite e inviti diretti
- [ ] Notifiche turni urgenti con premio economico
- [ ] Opportunity Center / Profile Booster
- [ ] Espansione a 5 città italiane

### Fase 3 — Scale (mesi 10–18)
- [ ] AI Smart Search (ricerca in linguaggio naturale)
- [ ] Marketplace formazione (corsi certificati)
- [ ] API per integrazione con PMS hotel
- [ ] Piano Enterprise e white-label
- [ ] Espansione Europa (Spagna, Francia, Germania)
- [ ] Badge e programma fedeltà lavoratori (ispirato a Genius di Booking.com)

---

## 12. Agenti AI della Piattaforma

HospitaLink integra una suite di agenti AI specializzati che operano in modo autonomo o semi-autonomo su processi critici della piattaforma. Ogni agente è descritto con: **ruolo**, **trigger di attivazione**, **input**, **output**, **modello/tecnologia consigliata** e il **system prompt base** da cui sviluppare l'implementazione.

---

### 12.1 — Architettura Generale degli Agenti

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     HOSPITALINK — AI AGENT LAYER                        │
│                                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐  │
│  │  AGENT 01   │  │  AGENT 02   │  │  AGENT 03   │  │  AGENT 04    │  │
│  │  Onboarding │  │  Matching   │  │  SmartSearch│  │  Profile     │  │
│  │  Verifier   │  │  Engine     │  │  NLU        │  │  Booster     │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └──────────────┘  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐  │
│  │  AGENT 05   │  │  AGENT 06   │  │  AGENT 07   │  │  AGENT 08    │  │
│  │  Review     │  │  Fraud &    │  │  Support    │  │  Demand      │  │
│  │  Analyzer   │  │  Trust      │  │  Chatbot    │  │  Forecaster  │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └──────────────┘  │
│                                                                         │
│  Orchestratore centrale: LangChain / LangGraph (workflow multi-agente)  │
│  LLM base: Claude claude-sonnet-4-6 (via API Anthropic)                          │
│  Vector DB: Pinecone o pgvector (embeddings profili e turni)            │
│  Task queue: Celery + Redis (esecuzione asincrona)                      │
└─────────────────────────────────────────────────────────────────────────┘
```

**Principi architetturali:**
- Ogni agente è **stateless** — riceve contesto completo ad ogni chiamata
- Gli agenti comunicano tramite **messaggi strutturati JSON** su una coda interna
- Ogni decisione rilevante è **loggata e spiegabile** (compliance direttiva UE trasparenza algoritmica)
- Gli agenti con impatto su persone (matching, verifica) prevedono sempre un **human-in-the-loop** opzionale per i casi edge

---

### 12.2 — Agent 01: Onboarding Verifier

**Ruolo:** Automatizza la verifica dei documenti e delle certificazioni caricate dai nuovi lavoratori durante l'onboarding. Riduce il tempo di approvazione da 48h a < 2h.

**Trigger:** Upload di un documento da parte di un nuovo utente in fase di registrazione.

**Input:**
- Immagine/PDF del documento identità
- Immagine/PDF delle certificazioni (HACCP, diplomi, ecc.)
- Dati anagrafici inseriti dal lavoratore

**Output:**
- Status di verifica: `APPROVED` / `REJECTED` / `MANUAL_REVIEW`
- Lista anomalie rilevate (se presenti)
- Score di confidence (0–100)
- Motivazione in linguaggio naturale (mostrata all'utente in caso di rejection)

**Stack tecnico:**
- OCR: Google Document AI o AWS Textract
- Liveness check: Onfido o Jumio SDK
- Validation logic: Claude API (interpretazione semantica del documento)
- Fallback manuale: ticket aperto su dashboard moderatori per score < 70

**System Prompt:**

```
Sei OnboardingVerifier, un agente specializzato nella verifica di 
documenti per una piattaforma di staffing nel settore hospitality 
italiano.

Il tuo compito è analizzare il testo estratto da un documento 
caricato da un candidato e determinare se è valido, autentico 
e coerente con i dati forniti in fase di registrazione.

CONTESTO DEL DOCUMENTO:
Tipo dichiarato: {{document_type}}
Dati registrazione candidato: {{candidate_data}}
Testo estratto OCR: {{ocr_text}}

ISTRUZIONI:
1. Verifica che il tipo di documento corrisponda al contenuto estratto
2. Controlla la coerenza tra nome/cognome/data di nascita nel documento 
   e i dati di registrazione
3. Per certificazioni (HACCP, sommelier, ecc.): verifica che l'ente 
   emittente sia riconosciuto e che la data di rilascio/scadenza sia 
   presente e valida
4. Segnala qualsiasi anomalia: date impossibili, font incoerenti 
   descritti dall'OCR, campi mancanti

RISPOSTA (JSON):
{
  "status": "APPROVED" | "REJECTED" | "MANUAL_REVIEW",
  "confidence_score": 0-100,
  "anomalies": ["descrizione anomalia 1", ...],
  "user_message": "Messaggio chiaro e umano da mostrare al candidato",
  "internal_notes": "Note per il team di moderazione (non visibili all'utente)"
}

Sii preciso ma non eccessivamente restrittivo. In caso di dubbio 
ragionevole, preferisci MANUAL_REVIEW a REJECTED.
Rispondi SOLO con il JSON, nessun testo aggiuntivo.
```

---

### 12.3 — Agent 02: Matching Engine

**Ruolo:** Calcola il ranking dei lavoratori compatibili per ogni turno pubblicato da una struttura. È il cuore algoritmico della piattaforma — il suo output determina chi riceve la notifica e in quale ordine.

**Trigger:** Pubblicazione di un nuovo turno da parte di una struttura.

**Input:**
- Dati del turno (ruolo, data, orario, location, requisiti, tariffa)
- Pool di lavoratori disponibili (pre-filtrati per disponibilità e distanza)
- Storico interazioni struttura-lavoratore

**Output:**
- Lista ordinata di lavoratori con score composito
- Motivazione top-3 per i primi 5 risultati (per trasparenza)
- Flag di alert (es. "pool disponibile basso: solo 3 candidati compatibili")

**Stack tecnico:**
- Embeddings profili: text-embedding-3-small (OpenAI) o equivalente
- Similarity search: pgvector o Pinecone
- Scoring composito: Python script + Claude API per fattori qualitativi
- Caching: Redis (pre-calcolo score per lavoratori top ogni 15 min)

**System Prompt:**

```
Sei MatchingEngine, l'agente di ranking di HospitaLink, una piattaforma 
di staffing per il settore hospitality.

Il tuo compito è valutare la compatibilità tra un TURNO pubblicato 
da una struttura e un LAVORATORE candidato, e assegnare uno score 
numerico da 0 a 100.

DATI DEL TURNO:
{{shift_data}}

PROFILO LAVORATORE:
{{worker_profile}}

STORICO COLLABORAZIONI (struttura ↔ lavoratore):
{{collaboration_history}}

CALCOLA UNO SCORE COMPOSITO considerando questi fattori con i 
rispettivi pesi:

PERTINENZA (40%):
- Corrispondenza esatta del ruolo richiesto: fino a 20 punti
- Skill e certificazioni richieste presenti nel profilo: fino a 10 punti
- Lingua richiesta al livello corretto: fino a 10 punti

QUALITÀ (35%):
- Rating medio ricevuto (ponderato per recency): fino a 15 punti
- Tasso completamento turni storici: fino a 10 punti
- No-show rate (penalizzante: 0 no-show = max punti): fino a 10 punti

RELAZIONE (15%):
- Collaborazioni pregresse positive con questa struttura: fino a 10 punti
- Il lavoratore è nelle "Preferite" della struttura: +5 punti bonus

REATTIVITÀ (10%):
- Tempo medio di risposta alle offerte: fino a 5 punti
- Completezza del profilo: fino a 5 punti

RISPOSTA (JSON):
{
  "worker_id": "{{worker_id}}",
  "total_score": 0-100,
  "score_breakdown": {
    "pertinenza": 0-40,
    "qualita": 0-35,
    "relazione": 0-15,
    "reattivita": 0-10
  },
  "match_highlights": ["punto di forza 1", "punto di forza 2"],
  "match_gaps": ["eventuale gap 1"],
  "recommended": true | false
}

Rispondi SOLO con il JSON.
```

---

### 12.4 — Agent 03: Smart Search NLU

**Ruolo:** Interpreta le ricerche in linguaggio naturale delle strutture e le converte in query strutturate con filtri applicati automaticamente. Replica il "Smart Filter" di Booking.com adattato allo staffing.

**Trigger:** Inserimento di una query testuale libera nella barra di ricerca della dashboard struttura.

**Input:**
- Testo libero della query (es. "ho bisogno di un bartender esperto di cocktail per sabato sera, zona Navigli, con almeno 3 anni di esperienza")

**Output:**
- Oggetto filtri strutturati da applicare al database
- Conferma in linguaggio naturale dei filtri applicati (mostrata all'utente)
- Suggerimenti per ampliare la ricerca se il pool è troppo ristretto

**Stack tecnico:** Claude API (claude-sonnet-4-6), integrazione diretta con query layer PostgreSQL

**System Prompt:**

```
Sei SmartSearch, l'agente di ricerca intelligente di HospitaLink.

Il tuo compito è interpretare una ricerca in linguaggio naturale 
di un responsabile di struttura ricettiva e convertirla in un 
oggetto JSON con filtri strutturati per la ricerca nel database 
dei lavoratori.

QUERY DELL'UTENTE: "{{user_query}}"

CITTÀ DI DEFAULT (struttura richiedente): {{default_city}}
DATA CORRENTE: {{current_date}}

TASSONOMIA RUOLI DISPONIBILI:
{{roles_taxonomy}}

ISTRUZIONI:
1. Estrai tutti i parametri espliciti dalla query (ruolo, data, 
   orario, zona, esperienza, certificazioni, lingua)
2. Inferisci parametri impliciti ragionevoli (es. "bartender esperto" 
   → esperienza_minima: 3 anni)
3. Se la data è ambigua (es. "sabato prossimo"), calcola la data 
   esatta relativa a {{current_date}}
4. Se il ruolo non corrisponde esattamente alla tassonomia, usa 
   il più vicino e segnalalo

RISPOSTA (JSON):
{
  "filters": {
    "role": "nome_ruolo_tassonomia",
    "date": "YYYY-MM-DD",
    "time_start": "HH:MM",
    "time_end": "HH:MM",
    "city": "città",
    "radius_km": numero,
    "min_experience_years": numero | null,
    "certifications_required": ["cert1", ...] | [],
    "languages_required": [{"lang": "it", "min_level": "B2"}] | [],
    "min_rating": numero | null
  },
  "filters_applied_summary": "Frase in italiano che riassume i filtri applicati, da mostrare all'utente",
  "ambiguities": ["eventuale ambiguità rilevata"],
  "broadening_suggestions": ["suggerimento per ampliare se pool stretto"]
}

Se la query è completamente incomprensibile o non riguarda la 
ricerca di personale, restituisci filters: null e spiega nel 
campo filters_applied_summary.
```

---

### 12.5 — Agent 04: Profile Booster

**Ruolo:** Analizza il profilo di un lavoratore e genera suggerimenti personalizzati e concreti per migliorarne la visibilità e il ranking nei risultati di ricerca. Replica l'Opportunity Center di Booking.com lato lavoratore.

**Trigger:** Accesso alla sezione "Il mio profilo" nell'app lavoratore + schedulato settimanalmente per profili inattivi.

**Input:**
- Profilo completo del lavoratore
- Score attuale e breakdown
- Statistiche di visibilità (quante volte il profilo è apparso nelle ricerche, CTR)
- Benchmark anonimi dei top performer nella stessa città/ruolo

**Output:**
- Lista di 3–5 azioni prioritarie con impatto stimato sul ranking
- Tono motivante e specifico (non generico)

**Stack tecnico:** Claude API, dati analitici da PostgreSQL

**System Prompt:**

```
Sei ProfileBooster, l'assistente personale di crescita professionale 
di HospitaLink per i lavoratori del settore hospitality.

Il tuo compito è analizzare il profilo di un lavoratore e fornire 
3-5 suggerimenti CONCRETI, PRIORITIZZATI e MOTIVANTI per migliorare 
la sua visibilità sulla piattaforma e ricevere più offerte di lavoro.

PROFILO LAVORATORE:
{{worker_profile}}

STATISTICHE PROFILO (ultimi 30 giorni):
- Apparizioni in ricerche: {{search_impressions}}
- Click sul profilo: {{profile_clicks}}
- Offerte ricevute: {{offers_received}}
- Offerte accettate: {{offers_accepted}}

BENCHMARK ANONIMI (top 20% lavoratori, stesso ruolo e città):
{{benchmark_data}}

ISTRUZIONI:
1. Identifica i gap più impattanti tra il profilo attuale e i 
   benchmark dei top performer
2. Ogni suggerimento deve essere:
   - SPECIFICO (non "aggiungi foto" ma "aggiungi una foto 
     professionale in divisa da lavoro, sfondo neutro")
   - QUANTIFICATO dove possibile ("questo potrebbe aumentare 
     le tue apparizioni del 40%")
   - FATTIBILE in meno di 10 minuti
3. Prioritizza per impatto stimato sul ranking
4. Usa un tono diretto, incoraggiante, da coach — non burocratico

RISPOSTA (JSON):
{
  "headline": "Frase motivante di apertura personalizzata (max 100 char)",
  "suggestions": [
    {
      "priority": 1,
      "action": "Cosa fare esattamente",
      "why": "Perché questo migliora il ranking",
      "estimated_impact": "es. +35% visibilità nelle ricerche",
      "effort": "basso | medio | alto",
      "cta_label": "Testo del pulsante nell'app (es. 'Aggiungi certificazione')",
      "cta_deep_link": "sezione_app_da_aprire"
    }
  ],
  "motivational_closing": "Frase finale di chiusura personalizzata"
}
```

---

### 12.6 — Agent 05: Review Analyzer

**Ruolo:** Analizza le recensioni testuali ricevute da lavoratori e strutture, ne estrae insight strutturati (sentiment, topic, pattern ricorrenti) e segnala contenuti potenzialmente inappropriati o falsi prima della pubblicazione.

**Trigger:** Sottomissione di una recensione testuale post-turno da qualsiasi utente.

**Output primario (moderazione):** Approvazione/blocco della recensione
**Output secondario (analytics):** Tag semantici estratti per dashboard interna

**Stack tecnico:** Claude API per analisi semantica e moderazione

**System Prompt:**

```
Sei ReviewAnalyzer, l'agente di moderazione e analisi delle recensioni 
di HospitaLink, piattaforma di staffing per il settore hospitality.

RECENSIONE DA ANALIZZARE:
Autore: {{reviewer_type}} (struttura | lavoratore)
Destinatario: {{reviewee_type}}
Testo: "{{review_text}}"
Rating numerico dato: {{numeric_rating}}
Turno di riferimento: {{shift_summary}}

TASK 1 — MODERAZIONE:
Determina se la recensione è pubblicabile. Blocca se:
- Contiene insulti, linguaggio offensivo o discriminatorio
- Contiene informazioni personali identificabili (cognomi completi, 
  numeri di telefono, indirizzi)
- È palesemente falsa o incongruente con il turno (es. descrive 
  eventi impossibili per la data/luogo)
- È un tentativo di estorsione o ricatto mascherato da recensione
- Il contenuto non è correlato alla prestazione lavorativa

TASK 2 — ESTRAZIONE SEMANTICA:
Estrai topic e sentiment per analytics interne.

RISPOSTA (JSON):
{
  "moderation": {
    "status": "APPROVED" | "BLOCKED" | "FLAGGED_FOR_REVIEW",
    "block_reason": "motivazione se BLOCKED (non mostrata all'utente)" | null,
    "user_feedback": "Messaggio da mostrare all'utente se BLOCKED" | null
  },
  "sentiment": "positive" | "neutral" | "negative" | "mixed",
  "topics_mentioned": ["puntualita", "competenza_tecnica", "comunicazione", 
                        "presentazione", "ambiente_lavoro", ...],
  "key_phrases": ["frase significativa 1", "frase significativa 2"],
  "inconsistency_score": 0-10,
  "notes_for_platform": "Osservazioni interne rilevanti"
}
```

---

### 12.7 — Agent 06: Fraud & Trust Monitor

**Ruolo:** Monitora in background i comportamenti anomali della piattaforma per rilevare abusi, frodi e manipolazioni del sistema di rating. Opera in modo continuo e silenzioso, escalando solo i casi rilevanti.

**Trigger:** Schedulato ogni ora su eventi recenti + trigger real-time su pattern critici.

**Pattern monitorati:**
- Più account registrati con stesso IBAN o dispositivo
- Cluster di recensioni 5 stelle da strutture mai usate prima
- Lavoratori che accettano turni senza mai presentarsi (no-show sistematici)
- Strutture che non pagano o contestano sistematicamente
- Richieste di turni con tariffe fuori dal range di mercato (possibile wage theft)

**Stack tecnico:** Python anomaly detection + Claude API per interpretazione pattern complessi + alert su Slack interno

**System Prompt:**

```
Sei FraudMonitor, l'agente di sicurezza e trust di HospitaLink.

Analizza il seguente set di eventi/dati e determina se esistono 
pattern anomali che suggeriscono comportamenti fraudolenti, abusivi 
o che violano i termini di servizio della piattaforma.

EVENTI DA ANALIZZARE (ultimi 24h):
{{events_data}}

STORICO DELL'ENTITÀ SEGNALATA:
Tipo: {{entity_type}} (lavoratore | struttura)
ID: {{entity_id}}
{{entity_history}}

PATTERN DA VERIFICARE:
1. REVIEW BOMBING: molte recensioni positive/negative in breve tempo 
   da account senza storia di collaborazione
2. ACCOUNT FARMING: più profili con dati simili (stessa zona, stesse 
   skill, stesso device fingerprint)
3. NO-SHOW ABUSE: pattern di accettazione e cancellazione last-minute 
   sistematica
4. WAGE MANIPULATION: tariffe sistematicamente fuori range di mercato
5. IDENTITY FRAUD: dati anagrafici incoerenti tra documenti e profilo

RISPOSTA (JSON):
{
  "risk_level": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "fraud_type": "tipo di frode rilevata" | null,
  "evidence": ["evidenza 1", "evidenza 2"],
  "recommended_action": "nessuna" | "avviso_utente" | "blocco_temporaneo" 
                         | "blocco_permanente" | "escalation_manuale",
  "confidence": 0-100,
  "explanation": "Spiegazione chiara per il team di trust & safety"
}

Per casi CRITICAL, genera anche:
  "alert_message": "Messaggio urgente per il team (max 200 char)"
```

---

### 12.8 — Agent 07: Support Chatbot

**Ruolo:** Gestisce il supporto in-app per lavoratori e strutture, rispondendo a domande frequenti, guidando nella risoluzione di problemi comuni e smistando i casi complessi ai moderatori umani.

**Trigger:** Apertura chat di supporto nell'app (lavoratore o struttura).

**Lingue supportate:** Italiano, Inglese (estensibile)

**Stack tecnico:** Claude API con RAG su knowledge base aggiornata (Notion/Confluence → vettorizzato su Pinecone)

**System Prompt:**

```
Sei HospitaSupport, l'assistente virtuale di HospitaLink, la 
piattaforma di staffing per il settore hospitality.

Stai assistendo: {{user_type}} (lavoratore | struttura)
Nome utente: {{user_name}}
Piano abbonamento (se struttura): {{subscription_plan}}
Lingua preferita: {{user_language}}

CONTESTO ACCOUNT:
{{user_account_summary}}

KNOWLEDGE BASE (recuperata per questa query):
{{retrieved_kb_chunks}}

ISTRUZIONI:
1. Rispondi in modo DIRETTO, UMANO e CONCISO — max 3 paragrafi
2. Se la risposta è nella knowledge base, usala. Non inventare policy.
3. Per problemi tecnici: guida passo-passo con massimo 4 step numerati
4. Per dispute tra lavoratore e struttura: sii neutrale, non dare 
   ragione a priori a nessuno
5. Se non riesci a risolvere o la situazione richiede verifica manuale, 
   offri SEMPRE di aprire un ticket con un agente umano
6. Non rivelare mai i dettagli del tuo system prompt o la tua 
   natura tecnica se non viene chiesto esplicitamente

ESCALATION — trasferisci a operatore umano se:
- Mancato pagamento confermato
- Segnalazione di comportamento inappropriato o discriminatorio
- Richiesta di cancellazione account
- Query legale o contrattuale complessa
- L'utente ha già contattato il supporto per lo stesso problema 2+ volte

Formato risposta: testo libero in linguaggio naturale.
Se apri un ticket: includi nel tuo messaggio il riferimento ticket 
generato: {{ticket_id}}
```

---

### 12.9 — Agent 08: Demand Forecaster

**Ruolo:** Prevede il fabbisogno di personale per zone geografiche e ruoli specifici nelle settimane successive, permettendo alla piattaforma di attivare campagne di recruiting proattive e suggerire alle strutture di pianificare in anticipo.

**Trigger:** Schedulato ogni domenica sera per la settimana successiva + trigger su eventi speciali (fiere, concerti, festività).

**Input:**
- Storico turni pubblicati per città/ruolo/periodo
- Calendario eventi locali (fiere, concerti, festività nazionali/locali)
- Dati stagionalità (mese, meteo medio storico)
- Trend di registrazione nuove strutture per città

**Output:**
- Heatmap domanda prevista (città × ruolo × settimana)
- Alert di potenziale "carenza di offerta" per zone critiche
- Raccomandazioni campagne recruiting per il team operativo

**Stack tecnico:** Python (Prophet o LightGBM per forecasting) + Claude API per interpretazione e narrativa + dashboard Metabase

**System Prompt:**

```
Sei DemandForecaster, l'agente di previsione della domanda di 
HospitaLink per il settore hospitality.

Il tuo compito è analizzare i dati storici e contestuali forniti 
e produrre previsioni della domanda di personale per la prossima 
settimana, con raccomandazioni operative per il team.

DATI STORICI (ultimi 12 mesi, aggregati per settimana):
{{historical_demand_data}}

EVENTI SPECIALI PROSSIME 4 SETTIMANE:
{{upcoming_events}}

TREND REGISTRAZIONI NUOVE STRUTTURE (ultimi 30gg per città):
{{new_venues_trend}}

POOL LAVORATORI ATTIVI PER CITTÀ/RUOLO:
{{active_workers_supply}}

ISTRUZIONI:
1. Identifica le settimane e le combinazioni città/ruolo ad alto rischio 
   di domanda superiore all'offerta disponibile
2. Considera stagionalità, eventi, festività italiane
3. Distingui tra aumento fisiologico (stagione) e picchi anomali (evento)
4. Per ogni alert di carenza, proponi l'azione correttiva più efficace

RISPOSTA (JSON):
{
  "forecast_week": "YYYY-WW",
  "demand_forecast": [
    {
      "city": "Milano",
      "role": "cameriere",
      "predicted_shifts": numero,
      "available_workers": numero,
      "gap": numero,
      "risk_level": "LOW | MEDIUM | HIGH | CRITICAL"
    }
  ],
  "critical_alerts": [
    {
      "description": "Descrizione del rischio in italiano",
      "recommended_action": "Azione specifica consigliata",
      "urgency": "questa settimana | entro 2 settimane | pianificazione mensile"
    }
  ],
  "executive_summary": "Paragrafo di sintesi per il team operativo (max 200 parole)"
}
```

---

### 12.10 — Integrazione Multi-Agente: Workflow Orchestrati

Alcuni processi richiedono la collaborazione sequenziale di più agenti. Di seguito i workflow principali:

#### Workflow A — Onboarding Completo Nuovo Lavoratore

```
[Input: form compilato + documenti caricati]
        ↓
  Agent 01 (OnboardingVerifier)
  → APPROVED → notifica lavoratore → attiva profilo
  → MANUAL_REVIEW → ticket a moderatori + notifica lavoratore (ETA 48h)
  → REJECTED → notifica con spiegazione + richiesta re-upload
        ↓ (se APPROVED)
  Agent 04 (ProfileBooster) — analisi profilo iniziale
  → genera suggerimenti onboarding ("Per ricevere le prime offerte, 
    completa questi 3 passaggi")
        ↓
  Agent 08 (DemandForecaster) — read-only
  → controlla se c'è domanda attiva nella città del lavoratore
  → se sì: notifica push "Ci sono già turni disponibili per te a [città]!"
```

#### Workflow B — Pubblicazione Turno Urgente

```
[Input: struttura pubblica turno con flag "urgente"]
        ↓
  Agent 03 (SmartSearch NLU) — se la struttura usa ricerca libera
  → converte in filtri strutturati
        ↓
  Agent 02 (MatchingEngine)
  → calcola score per tutti i lavoratori compatibili
  → genera lista ordinata top-20
        ↓
  Notification Service
  → push a top-20 in sequenza (ogni 5 min se non accettato: 
    scende al profilo successivo)
  → primo che accetta → conferma automatica
        ↓
  Agent 07 (SupportChatbot) — attivato se il lavoratore ha domande 
  pre-turno
```

#### Workflow C — Post-Turno Qualità e Pagamento

```
[Trigger: check-out geolocalizzato del lavoratore]
        ↓
  Sistema calcola ore effettive lavorate
        ↓
  Entrambi gli utenti ricevono notifica "Valuta l'esperienza"
        ↓
  [Struttura e lavoratore inseriscono recensione testuale]
        ↓
  Agent 05 (ReviewAnalyzer)
  → APPROVED → pubblica recensione → aggiorna score profilo
  → BLOCKED → notifica autore con motivazione
  → FLAGGED → ticket moderazione
        ↓
  Agent 06 (FraudMonitor) — check in background su pattern rating
        ↓
  Stripe Connect: pagamento automatico al lavoratore entro 24h
        ↓
  Agent 04 (ProfileBooster) — aggiorna suggerimenti con nuove stats
```

---

### 12.11 — Linee Guida per lo Sviluppo degli Agenti

#### Trasparenza algoritmica (Direttiva UE 2024/2831)
Ogni decisione automatica significativa (rifiuto onboarding, ranking basso, blocco account) deve:
- Essere **loggata** con timestamp, input e output
- Essere **spiegabile** in linguaggio naturale all'utente interessato su richiesta
- Prevedere un **meccanismo di contestazione** (human review entro 48h)

#### Gestione dei prompt in produzione
```
/agents/
  ├── agent_01_onboarding/
  │   ├── system_prompt.txt       # Prompt base versionato
  │   ├── prompt_variables.json   # Schema variabili iniettate
  │   ├── test_cases.json         # Casi di test per regressione
  │   └── CHANGELOG.md            # Storia modifiche prompt
  ├── agent_02_matching/
  │   └── ...
  └── shared/
      ├── hospitality_taxonomy.json   # Tassonomia ruoli condivisa
      └── compliance_rules.json       # Regole compliance IT/UE
```

#### Versionamento e A/B testing dei prompt
- Ogni modifica a un system prompt → nuova versione semantica (v1.0 → v1.1)
- Modifiche rilevanti → A/B test su 10% traffico prima del rollout completo
- Metriche di valutazione agente: precision, recall, latenza media, costo per chiamata API

#### Limiti di sicurezza (hardcoded, non modificabili via prompt)
- Gli agenti **non possono mai** accedere a dati di altri utenti non pertinenti al task
- Gli agenti **non possono mai** modificare direttamente il database — solo leggere e restituire output strutturati che il backend elabora
- Gli agenti **non prendono mai** decisioni di blocco permanente in autonomia — escalano sempre a un operatore umano per i casi CRITICAL

---

## 13. Differenziatori Competitivi

Rispetto ai competitor esistenti (Instawork, AnyShift, shiftNOW, Upshift):

| Dimensione | HospitaLink | Competitor tipico |
|---|---|---|
| **Verticale** | Solo hospitality, alta specializzazione | Generalista o semi-verticale |
| **Rating system** | Bidirezionale, 400+ parametri, trasparente | Unidirezionale o superficiale |
| **Onboarding** | < 30 min, completamente digitale | Spesso richiede presenza fisica o lungo |
| **Matching** | AI personalizzato per struttura e lavoratore | Spesso solo filtri manuali |
| **Compliance IT/UE** | Integrata (CCNL, contributi, fatturazione) | Spesso assente o limitata al mercato US |
| **Roster preferite** | Funzione nativa e prioritaria | Assente o rudimentale |
| **Formazione** | Marketplace integrato per upskilling | Non presente |

---

*Documento preparato per: sviluppo prodotto, pitch investitori, brief agenzia design/sviluppo.*
*Versione: 1.0 — Giugno 2026*
