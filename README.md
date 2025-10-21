# Massimo AI Bot

Semplice bot Telegram costruito con Python, Flask e OpenAI.

## Configurazione

1. Creare un file `.env` (oppure esportare le variabili d'ambiente) con:

   ```bash
   TELEGRAM_TOKEN=<il-token-del-bot>
   ```

2. Per l'esecuzione su piattaforme come Render, assicurarsi che la variabile
   d'ambiente `PORT` sia impostata (il server ne farà uso automaticamente).

## Avvio locale

Installare le dipendenze e avviare l'app:

```bash
pip install -r requirements.txt
python app.py
```

La rotta `http://localhost:10000/` (o la porta specificata da `PORT`) risponderà
con `Massimo AI è attivo e funzionante!`.
