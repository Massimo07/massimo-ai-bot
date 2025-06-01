
import telebot
import openai
from flask import Flask, request
import os

API_TOKEN = os.getenv("API_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

@app.route("/", methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        update = telebot.types.Update.de_json(request.get_data().decode("utf-8"))
        bot.process_new_updates([update])
        return "OK"
    return "Invalid", 403

@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "Ciao! Sono Massimo AI 🤖\n\nCome posso aiutarti oggi? Scrivimi pure!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Sei Massimo AI, un assistente esperto di network marketing, prodotti, registrazioni e supporto al team Magic Team Live On Plus."},
                {"role": "user", "content": message.text}
            ]
        )
        bot.reply_to(message, response.choices[0].message.content)
    except Exception as e:
        bot.reply_to(message, f"Errore nel rispondere: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
