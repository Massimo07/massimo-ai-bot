
import os
import telebot
from flask import Flask, request

API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Ciao! Sono Massimo AI 🤖\n\nCome posso aiutarti oggi?\nScrivimi: prodotti, registrazione o business." )

@bot.message_handler(func=lambda message: True)
def custom_reply(message):
    text = message.text.lower()
    if "prodotti" in text:
        bot.reply_to(message, "Abbiamo una gamma completa: skincare, casa, benessere e tanto altro. Vuoi il catalogo completo o un consiglio personalizzato?")
    elif "registrazione" in text:
        bot.reply_to(message, "Per registrarti clicca qui 👉 https://magicteam.liveonplus.com/registrazione")
    elif "business" in text or "guadagnare" in text:
        bot.reply_to(message, "Scopri come puoi costruire una rendita mensile partendo da casa. Ti va se ti spiego tutto in pochi passi?")
    elif "ciao" in text or "sei tu" in text:
        bot.reply_to(message, "Certo! Sono il tuo assistente personale per crescere in Live On Plus 🚀")
    else:
        bot.reply_to(message, "Messaggio ricevuto! Ti rispondo al più presto oppure scrivimi: prodotti, registrazione, business.")

@app.route('/' + API_TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "OK", 200

@app.route('/')
def index():
    return "Massimo AI è online!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
