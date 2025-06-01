import telebot
import openai
from flask import Flask, request

import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

chat_histories = {}

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    user_message = message.text

    if chat_id not in chat_histories:
        chat_histories[chat_id] = []

    # Aggiungiamo l’input utente
    chat_histories[chat_id].append({"role": "user", "content": user_message})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # o "gpt-3.5-turbo"
            messages=chat_histories[chat_id][-10:],  # ultimi 10 scambi
            temperature=0.7
        )

        reply = response.choices[0].message.content.strip()

        # Aggiungiamo la risposta dell'assistente
        chat_histories[chat_id].append({"role": "assistant", "content": reply})
        bot.reply_to(message, reply)

    except Exception as e:
        bot.reply_to(message, f"Errore: {e}")

@app.route('/', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

if __name__ == '__main__':
    app.run(debug=False)
