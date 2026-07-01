# Barman Match — Bozza modello legale (APL / intermediazione)

> ⚠️ **BOZZA di lavoro — NON è consulenza legale.** Va validata da un **giuslavorista** e, se si sceglie
> un modello autorizzato, con **ANPAL/Ispettorato**. Serve a inquadrare le opzioni e i guardrail già
> presenti nel codice. Nessun numero/soglia qui è definitivo → **[DA VERIFICARE]**.

## Il nodo giuridico
Barman Match mette in relazione **professionisti** (barman, sala, cucina) con **strutture/eventi**. In
Italia questo può ricadere in regimi diversi (D.Lgs. 276/2003 e s.m.i.):

| Modello | Cos'è | Autorizzazione | Barman Match è… |
|---|---|---|---|
| **A. Marketplace di autonomi** | I professionisti sono **lavoratori autonomi** (P.IVA o prestazione occasionale) che contrattano direttamente con la struttura; la piattaforma **intermedia** e fornisce strumenti | **Nessuna APL** *se* la piattaforma non esercita poteri datoriali | intermediario tecnologico |
| **B. Somministrazione di lavoro** (staff leasing) | La piattaforma **assume** i lavoratori e li **somministra** alla struttura | **APL autorizzata** (Albo Informatico ANPAL, requisiti di capitale e garanzie) | datore di lavoro/somministratore |
| **C. Intermediazione / ricerca e selezione** | Attività di incontro domanda/offerta come servizio | **Autorizzazione** (art. 4-6 D.Lgs. 276/2003) | agenzia autorizzata |

## Modello raccomandato per partire: **A — Marketplace di autonomi**
Il più snello e coerente con l'attuale architettura. La piattaforma **non è datore di lavoro**: non
dirige, non disciplina, non retribuisce come dipendenti. Requisiti per restare in A (evitare
riqualificazione in subordinazione/somministrazione):

1. **Il professionista è autonomo** — P.IVA o prestazione occasionale entro le soglie **[DA VERIFICARE]**;
   sceglie se accettare i turni, non ha vincolo di esclusiva.
2. **Il contratto è tra struttura e professionista** — la piattaforma è *terzo intermediario*. → già
   modellato in `routes/contracts.py` (contratto per turno).
3. **La piattaforma non esercita potere direttivo/disciplinare** sul lavoratore.
4. **Trasparenza del compenso** — nessun compenso sotto una soglia minima equa. → già presente
   `wage_floor.py` (floor sul `worker_payout`).
5. **Pagamenti tracciati e in piattaforma** — escrow: la struttura versa, i fondi restano in escrow,
   payout al professionista a servizio reso. → già presente `payments.py` (Stripe Connect, separate
   charges & transfers) + `entitlement.py` (la struttura ha un abbonamento; il lavoratore è gratis).
6. **Anti-disintermediazione** — scoraggiare l'accordo fuori piattaforma per aggirare tutele/compensi.
   → già presente `antidisintermediation.py`.
7. **KYC/verifica** — identità e requisiti del professionista. → già presente `kyc.py` + verifica via
   onboarding Stripe Connect (`is_verified`).

### Cosa dice (e non dice) il codice oggi
- **Chi paga**: la **struttura** (venue) ha l'abbonamento (`entitlement`), il **lavoratore usa gratis**.
  Coerente con A: il ricavo della piattaforma è un **canone di servizio** alla struttura + eventuale
  **fee** sull'escrow, non una marginalità sul lavoro somministrato.
- **Escrow**: `payments.create_fund_checkout` (la struttura versa `venue_total`), `release` (transfer del
  `worker_payout` al conto Connect del professionista), la piattaforma trattiene `fee_amount`.
- **Subscription**: `payments.create_subscription_checkout` (nuovo) — canone struttura via Stripe; il
  webhook attiva l'`entitlement`. Nessun pagamento fuori piattaforma.

## Se in futuro si vuole il modello B/C (autorizzato)
Serve costituire/associarsi a una **APL autorizzata**: requisiti di forma societaria, **capitale
versato** e **garanzie** **[DA VERIFICARE]**, iscrizione all'**Albo Informatico** ANPAL, LUL/contribuzione,
responsabilità solidale committente-somministratore. Impatto tecnico: la piattaforma diventerebbe
**datore di lavoro** → gestione buste paga, contribuzione, CCNL applicato (Pubblici Esercizi/Turismo)
**[DA VERIFICARE]**. È un salto di modello, non un'aggiunta.

## Guardrail da tenere sempre (qualunque modello)
- Compenso mai sotto il **floor** equo (`wage_floor`).
- Sicurezza sul lavoro: se il professionista opera nella sede del committente, obblighi D.Lgs. 81/08
  in capo al committente **[DA VERIFICARE]** (sinergia con SSFormazione/BAD360).
- Trasparenza su fee e trattenute (già in escrow).
- Tutela dati (GDPR) su profili/KYC.

## Prossimi passi legali (checklist)
- [ ] Parere di un **giuslavorista** sul modello A e sui confini con la somministrazione.
- [ ] Definire **inquadramento** dei professionisti (autonomo occasionale vs P.IVA) e soglie.
- [ ] **T&C** e **contratto di servizio** struttura↔piattaforma e professionista↔struttura.
- [ ] Verificare obblighi **assicurativi/RC** e sicurezza sede.
- [ ] Valutare, a scala, il passaggio a **APL autorizzata** (modello B) con business case.
