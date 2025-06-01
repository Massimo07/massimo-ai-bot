import telebot
import os

# Usa la variabile d’ambiente definita su Render
bot = telebot.TeleBot(os.environ['TELEGRAM_TOKEN'])

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Ciao, come posso aiutarti oggi?")

def main():
    bot.infinity_polling()