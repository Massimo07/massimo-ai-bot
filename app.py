import telebot
import openai
from flask import Flask, request

import os

API_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
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
    bot.reply_to(message, "Ciao! Sono Massimo AI 🤖\n\nCome posso aiutarti oggi?\nScrivimi: prodotti, registrazione o business.")

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
        bot.reply_to(message, "Si è verificato un errore nel rispondere: " + str(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)