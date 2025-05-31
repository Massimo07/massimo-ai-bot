import telebot
import openai
import os
from flask import Flask, request

# Carica le API key dalle variabili d’ambiente
API_TOKEN = os.environ.get('TELEGRAM_API_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK'

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Ciao e benvenuto! Sono Massimo AI 🤖\nCome posso aiutarti oggi?\n\n📦 Prodotti\n📝 Registrazione\n💼 Business\nScrivi una parola chiave oppure scegli dalle opzioni!")

@bot.message_handler(func=lambda message: True)
def chatgpt_reply(message):
    try:
        risposta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Sei Massimo AI, un assistente esperto in network marketing, prodotti per la persona, registrazioni e supporto per il team Magic Team Live On Plus."},
                {"role": "user", "content": message.text}
            ]
        )
        bot.reply_to(message, risposta.choices[0].message.content)
    except Exception as e:
        bot.reply_to(message, "⚠️ Si è verificato un errore: " + str(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
