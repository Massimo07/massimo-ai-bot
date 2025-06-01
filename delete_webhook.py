
import telebot

BOT_TOKEN = '7599536260:AAHHzBRYvPAU8QbR7hOoc-yltpv4H_YfIh0'  # 🔁 Sostituisci con il token reale
bot = telebot.TeleBot(BOT_TOKEN)

# Cancellazione webhook
if bot.remove_webhook():
    print("✅ Webhook cancellato con successo.")
else:
    print("❌ Qualcosa è andato storto nella cancellazione del webhook.")
