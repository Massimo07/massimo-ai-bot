
import os
import telebot
from flask import Flask, request

API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Ciao! Sono Massimo AI. Come posso aiutarti oggi? Scrivimi pure: vuoi info sui prodotti, sul business o registrarti?")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Perfetto! Ti rispondo subito.")

@app.route('/' + API_TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@app.route('/')
def webhook():
    return "Massimo AI Telegram Bot è attivo!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
