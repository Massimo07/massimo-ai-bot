import telebot
import os

# Istanzia il bot solo se è presente il token
token = os.getenv('TELEGRAM_TOKEN')
if not token:
    raise RuntimeError('TELEGRAM_TOKEN non configurato')

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Ciao, come posso aiutarti oggi?")

def main():
    bot.infinity_polling()
