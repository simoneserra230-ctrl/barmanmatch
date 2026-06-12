# BarmanMatch — Stato e Percorso
# Aggiornato: 12 giugno 2026 | Ruolo: MODULO BAD360 (lato venue) + app standalone (lato worker)

## ✅ INTEGRATO IN BAD360 (12/6/2026)
Il lato venue (locali) di BarmanMatch ora vive DENTRO BAD360 come modulo
"Staff Match" (`BAD360_SPLIT/barmanmatch.html` + `backend/staff_match.py` +
agente C7.6 AI Staff Rescue). Stesso algoritmo di matching (40/35/15/10),
stesso schema Supabase (`BAD360/supabase/staff_match_schema.sql`).
Questa app standalone resta per il LATO WORKER (i professionisti che cercano
turni) — si sviluppa quando il lato domanda (locali BAD360) esiste.

## Cos'è
Marketplace matching domanda/offerta per staff HoReCa: i locali pubblicano
turni, i professionisti (bartender, camerieri...) si candidano. Rating bilaterale.

## Stato attuale — COMPLETO AL ~40%
✅ Backend FastAPI: routes auth, matching, shifts, venues, workers, ratings
✅ Frontend doppio: area locale (post turni, dashboard) + area lavoratore
✅ Schema Supabase (supabase/schema.sql)
✅ Landing concept: barman_network.html, barman_sellable.html + index
⬜ Mai testato end-to-end, nessun deploy, nessun utente
⬜ Pagamenti/fee marketplace non progettati

## Percorso al "livello finale" (QUANDO si scongela)
1. Collegare Supabase reale (progetto + env) e smoke test del flusso:
   locale registra → pubblica turno → lavoratore si candida → match → rating
2. Deploy (Render + Vercel — riusare i pattern di BA.IA)
3. Modello fee: % sul turno o abbonamento locale
4. Cold start: partire da UNA città (Cagliari) e dal network personale

## Regola strategica
NON riprendere finché BA.IA non ha 10 clienti paganti e BAD360 non è lanciato.
Il marketplace ha il problema più difficile (due lati da popolare) — va
affrontato con la forza del network già costruito dagli altri prodotti
(i locali clienti BAD360 sono il lato domanda già pronto).
