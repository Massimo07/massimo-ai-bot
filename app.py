
from flask import Flask, request
import telebot
import os
import openai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('OPENAI_API_KEY')
BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')

app = Flask(__name__)
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message.text}]
        )
        reply = response.choices[0].message.content
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, f"Errore: {str(e)}")

@app.route('/', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    else:
        return 'Webhook attivo', 405

if __name__ == '__main__':
    import threading
    import time
    port = int(os.environ.get('PORT', 10000))
    threading.Thread(target=bot.polling, daemon=True).start()
    while True:
        try:
            app.run(host='0.0.0.0', port=port)
        except:
            time.sleep(5)
