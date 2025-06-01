import requests

# Inserisci qui il tuo vero token del bot Telegram
TOKEN = "7599536260:AAHHzBRYvPAU8QbR7hOoc-yltpv4H_YfIh0"
url = f"https://api.telegram.org/bot{TOKEN}/deleteWebhook"

response = requests.get(url)
print("Status code:", response.status_code)
print("Risposta:", response.json())
