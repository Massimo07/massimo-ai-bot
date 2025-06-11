import os
import openai
import telebot

from .utils import detect_language, get_subscription_level

bot = telebot.TeleBot(os.environ['TELEGRAM_TOKEN'])

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Ciao, sono Massimo AI! Scrivimi qualcosa.")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    user_id = message.from_user.id
    language = detect_language(message.text)
    subscription = get_subscription_level(user_id)
    reply = generate_openai_reply(message.text, language, subscription)
    bot.reply_to(message, reply)


def generate_openai_reply(text: str, language: str, subscription: str) -> str:
    openai.api_key = os.environ.get('OPENAI_API_KEY')
    prompt = text
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Errore nella generazione della risposta: {e}"
