# Massimo AI — AGENTS.md

> **Versione 0.5 – 10 giugno 2025**
> Documento interno. Non distribuire all’esterno del team Live On Plus senza approvazione.

---

## Scopo del documento

Definire la tassonomia completa degli **Agenti** (software + prompt) che costituiscono Massimo AI, specificando:

* **Livello di accesso (0–15 + Core)**
* **Canali supportati** (Web/App, WhatsApp, Telegram, e‑mail, SMS, voce, VR/AR)
* **Trigger di attivazione** (event‑driven, schedule, user intent, webhook)
* **Funzioni core**
* **Fonti dati** e API consumate
* **Metriche di performance chiave (KPI)**
* **Owner** (ruolo umano responsabile)

L’insieme degli Agenti è orchestrato da **Massimo AI Orchestrator** che gestisce priorità, contesto, autorizzazioni, throttle e logging.

---

## Vista d’insieme

### Core‑service agents (senza livello numerico)

| Nome agente                 | Canali  | Funzione primaria                           | Trigger                 | Fonti dati            | Owner                | KPI principale                  |
| --------------------------- | ------- | ------------------------------------------- | ----------------------- | --------------------- | -------------------- | ------------------------------- |
| **Massimo AI Orchestrator** | Backend | Routing, memory, rate‑limit, escalation     | Event bus               | `agent_state`, Redis  | **AI Platform**      | Latency orchestrazione < 100 ms |
| **Security Core Agent**     | Backend | IAM, key rotation, anomaly detection, audit | Auth events, schedulato | `iam_logs`, SIEM      | **Security Ops**     | Incident MTTR < 15 min          |
| **DataOps ETL Agent**       | Backend | Orchestrazione pipeline ETL, SLA monitoring | Schedule, event‑driven  | Airflow DB, Snowflake | **Data Engineering** | SLA rispettati > 99 %           |

### Agenti livelli 0‑15

| #  | Nome agente                  | Livello | Canali                  | Funzione primaria                                           | Trigger                      | Fonti dati                   | Owner                 | KPI principale             |
| -- | ---------------------------- | ------- | ----------------------- | ----------------------------------------------------------- | ---------------------------- | ---------------------------- | --------------------- | -------------------------- |
| 0  | Gateway Agent                | 0       | Web, WhatsApp, Telegram | Onboarding, login/SSO, GDPR                                 | Link/QR                      | `users_temp`, `consents`     | Growth Ops            | % login completati > 85 %  |
| 1  | FAQ Agent                    | 1       | Tutti                   | Risposte rapide a FAQ                                       | User intent                  | `kb_faq`                     | Customer Success      | TTA < 2 s                  |
| 2  | Product Guide Agent          | 2       | Web/App                 | Catalogo prodotti, ingredienti                              | Browse prodotto              | PIM API                      | Product Enablement    | CTR schede > 40 %          |
| 2  | **MicroLearn Agent**         | 2       | Web/App, Mobile         | Quiz/video micro‑learning                                   | User intent, scheduler       | `learning_db`, CDN           | Training Team         | Completion mobile > 75 %   |
| 3  | PlanCoach Agent              | 3       | Chat                    | Spiega piano marketing, simulatore PV/GV                    | User intent                  | `comp_plan`, FastAPI         | Sales Enablement      | % simulazioni > 60 %       |
| 4  | Follow‑Up Agent              | 4       | WhatsApp, e‑mail, SMS   | Promemoria personalizzati post‑demo                         | Evento demo                  | `crm_events`                 | Customer Success      | % follow‑up < 24 h         |
| 5  | CRM Agent                    | 5       | Web/App                 | Lead scoring, pipeline assignment                           | Nuovo lead                   | HubSpot, SFDC                | Sales Ops             | Lead score ±10 %           |
| 5  | **Billing & CompPlan Agent** | 5       | Web/App, PDF exporter   | Calcolo PV/GV, commissioni, report compensi                 | Fine mese, on‑demand         | `sales_ledger`, ERP          | Finance Ops           | Calcoli corretti > 99.5 %  |
| 6  | Automation Hub Agent         | 6       | Backend                 | Drip‑campaign multicanale (WhatsApp, e‑mail, SMS)           | Schedule                     | `campaign_db`                | Marketing Automation  | Open rate WA > 80 %        |
| 7  | Gamification Agent           | 7       | App, Web                | Badge, leaderboard live, sfide, token                       | Milestone evento             | `token_chain`, `leaderboard` | Community Manager     | Engagement sfide ≥ 50 %    |
| 8  | VR Trainer Agent             | 8       | Quest 2/3, WebXR        | Micro‑learning immersivo                                    | User start VR                | `unity_events`               | Training Team         | Completion > 70 %          |
| 9  | Certification Agent          | 9       | Web/App, Blockchain     | Issuing NFT certificati                                     | Corso completato             | IPFS, `badges_db`            | Learning & Compliance | % certificati senza errori |
| 10 | Analytics Agent v2           | 10      | Dashboard               | Predictive churn, realtime dashboard, weekly report PDF     | Snapshot + cron              | Snowflake, dbt               | Data Science          | F1 churn ≥ 0.85            |
| 10 | **ObjectiveTracker Agent**   | 10      | Backend, WhatsApp       | Monitor PV/GV target (60 PV, 30 000 GV, 4 Director) e alert | Schedule 1h, event milestone | `sales_ledger`, `crm_stats`  | Sales Enablement      | Alert inviati entro 5 min  |
| 10 | **SentimentMonitor Agent**   | 10      | Chat, Voice             | Rileva sentimento negativo, attiva retention playbook       | Streaming events             | `chat_logs`, `voice_logs`    | Customer Success      | Precision negativa > 0.85  |
| 11 | SocialScheduler Agent        | 11      | Meta, TikTok            | Post pianificati, A/B                                       | Time schedule                | `social_posts`               | Social Media          | % post corretti            |
| 11 | **WebinarScheduler Agent**   | 11      | Web/App, Zoom, Teams    | Pianifica webinar, RSVP, follow‑up                          | Event schedule               | `webinar_events`, Zoom API   | Events Marketing      | % RSVP → attendance > 60 % |
| 12 | VoiceBot Agent               | 12      | Phone, Alexa            | Assistenza vocale                                           | Chiamata inbound/outbound    | `voice_logs`                 | Voice Ops             | CSAT ≥ 4.5/5               |
| 13 | Marketplace Agent            | 13      | Web/App                 | Plug‑in skill third‑party                                   | Submission skill             | `market_db`                  | Partner Team          | # skill attive             |
| 14 | WhiteLabel Agent             | 14      | API, SDK                | Tenancy multipla brandizzata                                | New tenant                   | `tenant_config`              | Platform Team         | Rollout < 2 gg             |
| 15 | Advanced AR Agent            | 15      | Vision OS, HoloLens     | Demo prodotto AR realtime                                   | Launch AR                    | `ar_assets`                  | Experience Design     | Dwell time > 3 min         |

---

## Schede dettagliate — nuovi agenti

### ObjectiveTracker Agent (Livello 10)

* **Trigger:** Scheduler orario + eventi `pv.update`, `gv.update`, `rank.director`.
* **Workflow:**

  1. Aggrega metriche di produzione (`sales_ledger`, `crm_stats`).
  2. Calcola gap verso target personali (60 PV) e di gruppo (30 k GV).
  3. Se gap ≤ 15 % e periodo < 7 gg ➔ invia alert motivazionale via WhatsApp template + dashboard.
  4. Se “Director attivi” < 4 ➔ suggerisce piano azioni ai team lead.
* **Owner:** Sales Enablement.
* **KPI:** % alert entro 5 min; aumento medio PV post‑alert ≥ 10 %.

### SentimentMonitor Agent (Livello 10)

* **Trigger:** Streaming chat/voice events → sentiment score ogni nuovo messaggio.
* **Modello:** BERT fine‑tuned italiano EN‑IT; threshold negativa ≥ 0.6.
* **Azioni:**

  1. Flag chat con due o più messaggi negativi consecutivi.
  2. Notifica Customer Success; suggerisce contenuti perk (coupon, video motivazionale).
  3. Se CS interviene ➔ registra outcome (retained/lost).
* **Owner:** Customer Success.
* **KPI:** Precision negativa > 0.85; churn evitato per chat flaggate ≥ 20 %.

---

## Sicurezza, privacy e conformità

*(come versione 0.4 – invariato)*

---

## Governance & Owner Matrix (estratto nuove righe)

| Agente           | Owner primario   | Backup       | Escalation Slack |
| ---------------- | ---------------- | ------------ | ---------------- |
| ObjectiveTracker | Sales Enablement | Sales Ops    | #ai-objtracker   |
| SentimentMonitor | Customer Success | Data Science | #ai-sentiment    |

*(le righe esistenti rimangono)*

---

## Roadmap ➔ Agenti (aggiornata)

| Mese                | Milestone Roadmap                                             | Agenti coinvolti                                                                                                                      |
| ------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| 3–4                 | Livelli 6–10 + A/B testing, Analytics + Billing + KPI tracker | Automation Hub, Gamification, VR Trainer, Certification, Analytics v2, Billing & CompPlan, **ObjectiveTracker**, **SentimentMonitor** |
| *(resto invariato)* |                                                               |                                                                                                                                       |

---

## Changelog

* **10 giu 2025:** Versione 0.5 — aggiunti ObjectiveTracker Agent e SentimentMonitor Agent (livello 10); aggiornate tabelle, governance e roadmap.
* **10 giu 2025:** Versione 0.4 — SMS (Automation Hub), sfide (Gamification), weekly PDF (Analytics), E2E encryption; Follow‑Up include SMS.
* **10 giu 2025:** Versione 0.3 — DataOps ETL, MicroLearn, Billing & CompPlan, WebinarScheduler.
* **10 giu 2025:** Versione 0.2 — Orchestrator & Security Core, schede uniformate.
* **10 giu 2025:** Versione 0.1 — prima stesura.

---

*End of document*
