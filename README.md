# Massimo AI Bot

Bot Telegram con OpenAI e Flask pronto per Render.com

## Setup rapido
- **Requisiti**: Python 3.10+, Redis raggiungibile (anche locale con `redis-server`), account Telegram BotFather con token attivo.
- **Installazione**:
  ```bash
  python -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```
- **Esecuzione locale**:
  ```bash
  export TELEGRAM_TOKEN="<token_bot>"
  export OPENAI_API_KEY="<api_key>"
  export REDIS_URL="redis://localhost:6379/0"
  export ALLOWED_WEBHOOK_ORIGINS="https://<render-app>.onrender.com"
  flask --app bot run --port 8000
  ```
  Usa `ngrok http 8000` (o Render preview) e registra il webhook Telegram sul tunnel pubblico.

### Variabili d'ambiente (tabella)
| Nome | Obbligatoria | Default | Note operative |
| ---- | ------------ | ------- | -------------- |
| `TELEGRAM_TOKEN` | Sì | – | Token BotFather, da ruotare se il webhook viene compromesso. |
| `OPENAI_API_KEY` | Sì | – | Chiave OpenAI; evitare di loggarla, ruotare insieme al token Telegram in incident. |
| `REDIS_URL` | Sì | `redis://localhost:6379/0` | Usata per `agent_state`, rate-limit e lock distribuiti. |
| `ALLOWED_WEBHOOK_ORIGINS` | Sì | – | Lista separata da virgole degli host ammessi (Render, ngrok). Il Security Core rifiuta richieste da origini non incluse. |
| `FLASK_ENV` | No | `production` | Usare `development` solo in locale per reload. |
| `PORT` | No | `10000` (Render) | Porta bindata dal Procfile; sovrascrivere se si esegue in locale su altra porta. |

### Check rapido pre-commit
- `python -m compileall .` per intercettare errori sintattici.
- `flask --app bot routes` per verificare che i blueprint siano caricati.
- `curl -s http://localhost:8000/health` per il controllo di liveness senza dipendenze esterne.

### Checklist di produzione (riassunto operativo)
- **Sicurezza**: ruota `TELEGRAM_TOKEN` + `OPENAI_API_KEY` a ogni incidente o cambio di owner; abilita CORS/allowlist webhook con `ALLOWED_WEBHOOK_ORIGINS`.
- **Affidabilità**: watchdog sulla latenza end-to-end Telegram→Orchestrator (budget 2 s p95) e alert se backlog Redis cresce > 500 job.
- **Dati**: backup quotidiano di Redis (snapshot RDB) e log SIEM; verifica data retention minima 30 giorni per audit.
- **Deployment**: attiva liveness `/health` e readiness `/health?mode=deep` (separare dipendenze esterne); conferma che `Procfile` usi `gunicorn app:app` con binding su `$PORT`.
- **Runbook**: team on-call e canali Slack (`#ai-incident`, `#ai-objtracker`, `#ai-sentiment`) devono essere configurati prima del go-live.

### Playbook qualità conversazionale & sicurezza LLM
- **Prompt di sistema**: includi sempre policy di sicurezza (no dati sensibili, no consigli legali/clinici) e il ruolo dell'agente target; il Security Core rifiuta prompt senza `correlation_id` e `policy_decision`.
- **Filtri contenuti**: blocca richieste che contengono PII (regex email/telefono) se l'agente non è autorizzato a trattarle; registra evento `policy_decision=deny` con motivo.
- **Safety fallback**: in caso di score di rischio alto o moderato, rispondi con messaggio di cortesia predefinito e apri escalation; evita hallucination chiedendo conferma dati critici all'utente prima di procedere.
- **Limiti di frequenza**: applica rate-limit per chat ID (es. 10 req/min) e per IP sorgente webhook; in caso di throttling restituisci messaggio di attesa e logga `retry_after_ms`.
- **Red-team periodico**: esegui test mensili con prompt avversari (prompt injection, data exfiltration, jailbreak) e annota outcome in SIEM per migliorare le regole del Security Core.
- **Template di prompt tracciato** (esempio):
  ```text
  [SYSTEM]
  policy_decision=allow | correlation_id={{cid}} | agent={{agent_name}} | channel={{channel}}
  - Non trattare dati sanitari o finanziari non autorizzati.
  - Conferma i dati critici ripetendoli e chiedendo "Confermi?" prima di procedere.

  [USER]
  {{message}}
  ```
  In mancanza di `{{cid}}` o `{{agent_name}}`, il Security Core deve rispondere con `policy_decision=deny`.

## Cos'è Massimo AI
Massimo AI è un insieme di agenti coordinati dall'**Orchestrator**, che gestisce routing, memoria contestuale, throttling, logging ed escalation verso owner umani. Il sistema include un **Security Core Agent** responsabile di IAM, rotazione chiavi, rilevamento anomalie e audit continuity.

### Pilastri architetturali
- **Orchestrator**: governa la coda eventi, applica throttling per canale, conserva contesto breve/lungo termine, applica policy di autorizzazione e instrada l'escalation a owner umani quando la confidenza scende sotto soglia o l'azione richiede intervento manuale.
- **Security Core Agent**: presidia IAM (provisioning/deprovisioning), ruota chiavi/API token, effettua anomaly detection su audit log e blocca flussi sospetti; fornisce reportistica di compliance.
- **DataOps ETL Agent**: orchestra pipeline ETL e SLA monitorati (Airflow/Snowflake), pubblica feature store per gli agenti analytics e garantisce qualità dati > 99 %.
- **Reliability layer**: healthcheck `/health`, watchdog sui tempi di roundtrip Telegram↔Orchestrator, alert automatici in caso di tasso errori webhook 5xx > 1 %.

### Flusso end-to-end (Telegram → agenti)
1. **Webhook Telegram → Gateway Agent (livello 0)**: valida token bot, estrae intent o QR referral, applica rate-limit di ingresso per utente.
2. **Routing Orchestrator**: arricchisce il contesto con memoria breve (ultima sessione) e lunga (profilo utente), seleziona l'agente target in base a intent, ruolo, livello di rischio e canale.
3. **Security Core**: verifica permessi (scopes API, ruoli), applica controlli di anomalia (flooding, scope escalation) e può forzare blocco/step-up auth.
4. **Agente specializzato**: esegue la funzione (FAQ, Product Guide, ObjectiveTracker, SentimentMonitor, ecc.), interagendo con le fonti dati dichiarate e restituendo output + KPI loggati.
5. **Audit & Logging**: eventi e metriche vengono inviati a `agent_state`/Redis e SIEM; eventuali escalation verso Slack/Teams seguono il playbook in `AGENTS.md`.

#### Probe & osservabilità di salute
- **Liveness** (`/health`): deve restituire 200 OK senza dipendenze esterne; include `status":"ok"` e versione app.
- **Readiness** (`/health?mode=deep`): controlla Redis (`PING`), reachability OpenAI (HEAD su endpoint) e spazio disco; se uno qualsiasi fallisce restituisci 503 con dettaglio `component`.
- **Degraded mode**: se Redis è lento ma non down, l'Orchestrator limita fan-out e aggiunge header `X-Massimo-Degraded: true`; alert automatico su backlog > 300 job.
- **Tracing**: propaga `correlation_id` come header `X-Correlation-ID` nelle chiamate interne e lo allega a ogni log/trace; le richieste senza header vengono rifiutate dal Security Core.
- **Metriche minime**: `webhook_requests_total`, `webhook_failures_total` per codice HTTP, `orchestrator_latency_ms` per agente, `security_denies_total` per motivo; esporta su Prometheus o equivalente Render.

#### Schema messaggi & correlazione
- **Input minimo**: payload Telegram `update_id`, `message.chat.id`, `message.text`; il Gateway aggiunge `user_level`, `channel`, `locale`.
- **Context bag**: l'Orchestrator arricchisce con `session_id`, `memory_short`, `memory_long` (linkata a Redis) e `correlation_id` propagato a log e tracce.
- **Output**: `message_id`, `agent`, `latency_ms`, `policy_decision` (allow/deny/step-up) e `kpi_tag` per routing su dashboard.
- **Regole**: ogni chiamata a modelli LLM include `correlation_id` e `policy_decision` per essere accettata dal Security Core; i messaggi senza `correlation_id` sono scartati.

### Tipologie di agenti (livelli)
- **Core-service (senza livello)** – Orchestrator, Security Core, DataOps ETL: backend-only, acting come layer di controllo.
- **Livello 0–5** – Onboarding (Gateway), FAQ, guide prodotto, micro-learning, coaching piano marketing, follow-up post demo, CRM e calcolo compensi. Canali: web/app, chat, WhatsApp, Telegram, e-mail, SMS. KPI: login completati, TTA risposte, CTR schede, accuratezza calcoli.
- **Livello 6–10** – Automazioni multicanale, gamification, formazione VR, certificazioni, analytics predittive e monitoraggio KPI (ObjectiveTracker, SentimentMonitor). Canali: backend, app/web, VR/AR, dashboard. KPI: open rate, completion, F1 churn, alert entro SLA.
- **Livello 11–15** – Scheduler social/webinar, voice bot, marketplace di skill, white-labeling e dimostrazioni AR avanzate. Canali: Meta/TikTok, Zoom/Teams, voce, SDK/API. KPI: percentuale post corretti, CSAT, rollout multi-tenant.

### Canali, trigger e ownership
- **Canali supportati**: web/app, chat, WhatsApp, Telegram, e-mail, SMS, voce, VR/AR, dashboard. L'Orchestrator applica policy di rate-limit e ordering per canale.
- **Trigger**: eventi (CRM, vendite, auth), scheduler, user intent, webhook. Ogni agente dichiara trigger ammessi; il Security Core può bloccare trigger non autorizzati.
- **Ownership**: ogni agente ha un owner umano per governance e KPI (es. Growth Ops per Gateway, Customer Success per FAQ/SentimentMonitor, Sales Enablement per ObjectiveTracker, Security Ops per Security Core).
- **Runbook ownership**: escalation canale Slack `#ai-incident` (Security), `#ai-objtracker` (ObjectiveTracker), `#ai-sentiment` (SentimentMonitor) come da matrice in `AGENTS.md`.

### Metriche e KPI
- **Tempo**: TTA risposte < 2 s (FAQ), alert entro 5 min (ObjectiveTracker), MTTR incidenti < 15 min (Security Core).
- **Qualità**: accuratezza calcoli > 99.5 % (Billing & CompPlan), precision negativa > 0.85 (SentimentMonitor), login completati > 85 % (Gateway).
- **Engagement**: CTR schede > 40 %, open rate WhatsApp > 80 %, completion micro-learning > 75 %.
- **Affidabilità**: uptime webhook > 99.9 %, ratio errori 5xx Orchestrator < 0.5 %, drift modelli (sentiment/churn) monitorato mensilmente.

### Stack tecnico e variabili chiave
- **App**: Flask + python-telegram-bot; procfile per Render/Heroku; requirement in `requirements.txt`.
- **Persistenza & stato**: Redis per `agent_state` e rate-limit; log audit verso SIEM; feature store da DataOps ETL.
- **Config**: variabili necessarie `TELEGRAM_TOKEN`, `OPENAI_API_KEY`, `REDIS_URL`, `ALLOWED_WEBHOOK_ORIGINS`. Separare credenziali prod/staging via env.
- **Deploy**: webhook registrato su `/webhook` con certificato opzionale; healthcheck su `/health` (preferibile 200 OK senza dipendenze esterne).
- **Webhook setup**: esempio con cURL (sostituire `<bot_token>` e `<url>`):
  ```bash
  curl -X POST "https://api.telegram.org/bot<bot_token>/setWebhook" \
    -H "Content-Type: application/json" \
    -d '{"url":"<url>/webhook"}'
  ```
  Per disattivare rapidamente in incident: `setWebhook` con `"url":""`.

#### Onboarding nuovo agente
1. Definisci **owner umano** e inserisci la riga in `AGENTS.md` (livello, canali, trigger).
2. Registra **KPI** e target in dashboard (es. `kpi_tag=faq_tta_ms`).
3. Crea **policy di sicurezza** dedicate (scope API, regex PII) e aggiorna il Security Core.
4. Aggiungi **hook di osservabilità**: metriche specifiche dell'agente + `correlation_id` condiviso.
5. Esegui **test end-to-end** in staging (webhook simulato) con almeno 3 casi positivi e 3 negativi.
6. Concludi con **go-live checklist**: chiavi ruotate, accessi minimi, runbook dedicato e alert su canale Slack dell'owner.

#### Budget prestazionali e SLO
- **Routing**: Orchestrator latency p95 < 100 ms; Security Core decision p95 < 60 ms; coda eventi Redis < 200 job medi.
- **User experience**: round-trip Telegram↔LLM p95 < 2 s; retry massimi 3 con backoff esponenziale 0.5 s.
- **Affidabilità**: uptime webhook > 99.9 % e errori 5xx < 0.5 %; profondità backlog ingest mai oltre 1 min di traffico medio.
- **Dati**: success rate ETL > 99 %; drift check mensile con MDE 1 pp su sentiment/churn prima di redeploy.

### Deploy su Render (blueprint)
1. **Repository** collegato a Render con build command `pip install -r requirements.txt`.
2. **Start command** definito dal `Procfile`: `web: gunicorn app:app --bind 0.0.0.0:$PORT` (Render imposta `$PORT`).
3. **Env group**: inserire le variabili della tabella sopra, più `FLASK_ENV=production`.
4. **Post-deploy**: chiamare `setWebhook` puntando all'URL pubblico Render (`https://<service>.onrender.com/webhook`).
5. **Verifica**: `curl -i https://<service>.onrender.com/health` deve restituire `200 OK`; simulare un update Telegram con payload minimo per assicurarsi che il Security Core accetti l'origine.
6. **Rollback**: conserva gli ultimi 2 deploy buoni; in caso di regressione ripristina l'immagine precedente e ri-registra il webhook con lo stesso dominio.

### Resilienza e test
- **Load test**: simulare 200 richieste/min su `/webhook` mantenendo p95 < 2 s e 0 errori 5xx; se superato, aumentare worker Gunicorn (`WEB_CONCURRENCY`) e verificare che Redis regga il throughput (latency `PING` < 20 ms).
- **Chaos drill**: ogni mese disabilitare per 5 min l'accesso a Redis in staging; verificare che il bot passi in modalità degradata (`X-Massimo-Degraded: true`) e che i messaggi di cortesia vengano inviati.
- **Backup & recovery**: programmare `redis-cli SAVE` giornaliero con retention 7 giorni; eseguire restore trimestrale di prova e confrontare checksum delle chiavi critiche (`agent_state:*`).
- **Canary controllato**: prima di roll out 100 %, indirizzare 10 % del traffico reale al nuovo deploy e controllare che `webhook_failures_total` non superi +0.2 pp rispetto alla baseline; se OK, aumentare al 50 % e poi 100 %.
- **Pen test mirato**: usare script di red-team per prompt injection e flood di webhook (100 req/s per 30 s) in staging; il Security Core deve bloccare IP/Token e mantenere uptime > 99.9 % durante il test.

### Runbook operativo (estratto)
1. **Blocco traffico o flood** ➔ Security Core disabilita webhook e ruota chiavi; avvisa `#ai-incident` (vedi owner in `AGENTS.md`).
2. **KPI degradati** (es. alert ObjectiveTracker > 5 min) ➔ controllare coda eventi in Orchestrator e capacità Redis; se necessario scala pod + ripristina backlog.
3. **Errore data quality** ➔ DataOps ETL forza re-run pipeline, segnala item errati agli agenti analytics; pubblica report di qualità > 99 % prima del ri-deploy.
4. **Errore OpenAI o timeout LLM** ➔ fallback a risposta di cortesia + log in `agent_state`; Orchestrator riprova massimo 3 volte con backoff, poi escalation a owner.
5. **Webhook compromise** ➔ Security Core invalida token BotFather, ruota `OPENAI_API_KEY`, rigenera tunnel/URL Render; audit trail inviato a SIEM con motivo incident.
6. **Downstream API slow** ➔ l'Orchestrator applica circuit breaker su fonte esterna; Security Core riduce la finestra di throttling e fornisce messaggio di cortesia all'utente.
7. **Drift modelli** (Sentiment/Churn) ➔ DataOps ETL ricalcola baseline, aggiorna feature store e notifica i team owner prima del redeploy del modello.
8. **Crash loop pod** ➔ controlla readiness `/health?mode=deep`, scala a 0 → 1 per forzare ri-creazione, valida che Redis non abbia chiavi corrotte; ripristina da snapshot se necessario.
9. **Rotazione programmata chiavi** ➔ usa finestra di manutenzione di 5 min con messaggio statico; aggiorna `TELEGRAM_TOKEN` e `OPENAI_API_KEY` in blocco atomico su Render Env Group.
10. **Release management** ➔ attiva freeze di 24 h prima di eventi critici; usa canary (10 % traffico) verificando p95 round-trip < 2 s e assenza di errori 5xx aggiuntivi prima del rollout 100 %.
11. **Disaster recovery** ➔ se si perde lo stato Redis, ripristina snapshot RDB più recente, invalida sessioni attive (cleanup `memory_short`), reinvia webhook `setWebhook` per evitare update persi; comunica RTO target 15 min al team.
12. **Verifica post-incident** ➔ entro 24 h produci postmortem con `timeline`, `root cause`, `customer impact`, `fix` e `follow-up action owner`; aggiorna runbook e test di regressione (simulazione webhook) con i nuovi casi.
13. **PCI/PII hardening** ➔ se l'incident coinvolge dati personali, avvia entro 1 h l'audit di accesso chiavi (Security Core), sospendi esportazioni non essenziali e attiva logging verboso su accessi Redis; completa notifica legale entro SLA aziendale.
14. **Ritorno alla normalità** ➔ dopo il fix, monitora 1 h le metriche chiave (webhook errori, latency, `security_denies_total`); se stabili, chiudi l'incident e pianifica retrospettiva con owner.

### Test locale guidato
1. **Simula webhook**: `curl -X POST http://localhost:8000/webhook -H "Content-Type: application/json" -d '{"update_id":1,"message":{"chat":{"id":123},"text":"/start"}}'`.
2. **Verifica circuito Security Core**: controlla log `policy_decision=allow` e presenza di `correlation_id`.
3. **Reset stato**: `redis-cli -u "$REDIS_URL" FLUSHDB` (solo in locale/staging) per azzerare memoria breve/lunga.
4. **Escalation di prova**: forza errore su downstream (es. disabilita internet) e verifica che l'Orchestrator risponda con messaggio di cortesia + log escalation.

### Observability & alerting
- **Logging**: `app.py` scrive info di routing e agent invocation; abilitare livello DEBUG solo in staging per evitare leak PII.
- **Metrics**: esportare gauge/counter da Orchestrator (latency per agente, retry, code errore) verso Prometheus o equivalente Render add-on.
- **Alert**: soglie consigliate — latenza orchestrazione > 100 ms (warning), webhook errori 5xx > 1% (critical), fallimenti Security Core policy > 0.1% (warning).
- **Tracing**: inserire correlation-id per conversazione in log Telegram ↔ agent; Security Core verifica che id sia presente prima di accettare l'evento.
- **Dashboard suggerita**: pannelli per (1) latency p50/p95 per agente, (2) tasso errori webhook 4xx/5xx, (3) backlog coda Orchestrator, (4) eventi di escalation Security Core.

Per la tassonomia completa degli agenti, con trigger, fonti dati e owner, fare riferimento a `AGENTS.md`.

### Threat model e controlli di sicurezza
- **Surface Telegram webhook**: rischio token leakage o flood ➔ enforcement `ALLOWED_WEBHOOK_ORIGINS`, rate-limit IP + chat ID, audit di ogni `policy_decision` con motivo e `correlation_id`.
- **LLM prompt injection**: il Security Core valida presenza di prompt di sistema con policy; blocca output con URL esfiltrazione e filtra messaggi con PII non autorizzata.
- **Credential sprawl**: chiavi OpenAI/Telegram e segreti Redis gestiti via env group; rotazione coordinata (`freeze 5 min`) e revoca immediata in incident.
- **Data tampering/DR**: snapshot RDB giornaliero firmato; verifica integrità con checksum e confronto numero chiavi critiche (`agent_state:*`) pre/post restore.
- **Escalation path**: incident handler documentato con canali Slack dedicati (`#ai-incident`, `#ai-objtracker`, `#ai-sentiment`), owner e backup in `AGENTS.md`.

### Ciclo di vita dei dati e privacy
- **Classificazione**: taggare campi Telegram (`chat.id`, `username`) come PII; loggati solo in forma hashed quando non indispensabili; messaggi utente con retention massima 30 gg in staging, 7 gg in prod.
- **Minimizzazione**: l'Orchestrator passa al modello solo gli slot minimi (intent, contesto ridotto, lingua); `memory_long` in Redis non deve includere dati finanziari/sanitari.
- **Accesso**: il Security Core espone ruoli applicativi (bot-operator, analyst) con permessi separati su query log e dashboard; tutte le letture scrivono audit trail con `who/when/why`.
- **Right to forget**: endpoint amministrativo (solo Security Core) che lancia purge di chiavi Redis per `chat.id` specifico e invalida snapshot future; documentare richiesta e conferma in SIEM.
- **Data sharing**: export verso sistemi esterni (es. BI) devono anonimizzare `chat.id` e rimuovere testo libero; contratti di data processing revisionati a ogni nuovo connettore.

### Qualità e gate pre-rilascio
- **Test automatici**: harness di simulazione webhook con almeno 10 conversazioni (5 positive/5 negative) per ciascun agente attivo; verificare response p95 < 2 s e `policy_decision` coerente.
- **LLM eval**: set di 50 prompt per il FAQ/Product Guide con metriche BLEU/ROUGE e checklist di sicurezza (no PII, no hallucination); fail → blocco rilascio.
- **Performance**: profiling `gunicorn --workers` variabile per garantire che CPU per worker rimanga < 75 % durante load test; se > 75 % aumentare concurrency o ridurre timeout LLM.
- **Rollback readiness**: ogni deploy deve avere versione precedente riattivabile in < 5 min con webhook già preconfigurato; documentare in changelog interno.
- **Segnali di salute**: prima del go-live verificare trend 24 h di `webhook_failures_total`, backlog Redis e `security_denies_total`; se spike > +0.2 pp rispetto baseline ➔ freeze e investigazione.

### Template di escalation sintetici
- **Incident Security**: "Incident SECURITY (token/webhook). Azione: disattivo webhook, ruoto `TELEGRAM_TOKEN` + `OPENAI_API_KEY`, abilito logging verboso 15 min. Owner: Security Ops. Correlation: {{cid}}".
- **Degrado prestazioni**: "Incident LATENCY > 2s p95. Azione: aumento `WEB_CONCURRENCY`, verifico Redis `PING` < 20 ms, canary 10 % → 50 % se stabile. Owner: AI Platform. Correlation: {{cid}}".
- **Data quality**: "Incident DATAQUALITY < 99%. Azione: rerun ETL (DataOps), blocco export, confronto checksum `agent_state:*`, aggiorno dashboard. Owner: Data Engineering. Correlation: {{cid}}".
- **LLM safety**: "Incident SAFETY prompt injection. Azione: applico deny + messaggio cortesia, aggiorno regole Security Core, lancio red-team regression. Owner: Security Ops. Correlation: {{cid}}".
