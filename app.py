import telebot
import os
import openai
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(API_TOKEN)
openai.api_key = OPENAI_API_KEY

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Ciao! Sono Massimo AI 🤖. Come posso aiutarti oggi?")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Sei Massimo AI, un assistente esperto nel network marketing di Live On Plus. Aiuti le persone a capire i prodotti, il piano compensi e come iniziare."},
                {"role": "user", "content": message.text}
            ]
        )
        reply = response.choices[0].message.content
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, "Errore: impossibile contattare l'intelligenza artificiale.")

if __name__ == "__main__":
    bot.polling()
