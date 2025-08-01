
import os
import requests
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Hafıza sistemi
chat_history = []

# OpenRouter API ayarları
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "openai/gpt-3.5-turbo"

# Hava durumu API key (Render ortam değişkeni)
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
WEATHER_CITY = "Bursa"
WEATHER_UNITS = "metric"
WEATHER_LANG = "tr"

def get_weather(city):
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": WEATHER_UNITS,
        "lang": WEATHER_LANG
    }
    response = requests.get(WEATHER_API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        temp = data["main"]["temp"]
        description = data["weather"][0]["description"]
        return f"{city} için şu an hava {description}, sıcaklık {temp}°C civarında."
    else:
        return "Hava durumu bilgisi alınamadı, sistemde bir sıkıntı olabilir."

@app.route("/", methods=["GET"])
def home():
    return "KAAN server aktif!", 200

@app.route("/command", methods=["POST"])
def chat():
    global chat_history

    data = request.get_json()
    message = data.get("message", "")
    history_count = len(chat_history)

    # Eğer mesaj hava durumu ile ilgiliyse özel yanıt
    if "hava" in message.lower() and "nasıl" in message.lower():
        weather_response = get_weather(WEATHER_CITY)
        return jsonify({
            "history_count": history_count,
            "response": weather_response
        })

    # Sohbet geçmişine yeni mesajı ekle
    chat_history.append({"role": "user", "content": message})

    # API’ye istek gönder
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": "Sen KAAN adında esprili ama gerektiğinde ciddi davranan bir asistansın. Türkçe konuşuyorsun ve Anıl'a yardımcı oluyorsun."},
            *chat_history
        ]
    }

    response = requests.post(OPENROUTER_BASE_URL, headers=headers, json=payload)

    if response.status_code == 200:
        reply = response.json()["choices"][0]["message"]["content"]
        chat_history.append({"role": "assistant", "content": reply})
        return jsonify({
            "history_count": history_count,
            "response": reply
        })
    else:
        return jsonify({
            "error": "OpenRouter yanıt vermedi.",
            "details": response.text
        }), 500

if __name__ == "__main__":
    app.run(debug=True)
