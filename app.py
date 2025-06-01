from flask import Flask
import threading
import bot  # importa il bot da bot.py

app = Flask(__name__)

@app.route('/')
def home():
    return "Massimo AI è attivo e funzionante!"

if __name__ == '__main__':
    # Avvia il bot in un thread separato
    threading.Thread(target=bot.main).start()
    # Avvia il web server per soddisfare Render
    app.run(host='0.0.0.0', port=10000)