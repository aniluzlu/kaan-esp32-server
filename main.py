
import os
import requests
from flask import Flask, request, jsonify
from datetime import datetime
import pytz

app = Flask(__name__)

# Hafıza sistemi
chat_history = []

# OpenRouter API ayarları
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "openai/gpt-3.5-turbo"

# Hava durumu API ayarları
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
WEATHER_CITY = "Bursa"
WEATHER_UNITS = "metric"
WEATHER_LANG = "tr"

def get_weather(city):
    if not WEATHER_API_KEY:
        return "Hava durumu servisi yapılandırılmamış. Lütfen sistem yöneticinize başvurun."
    try:
        params = {
            "q": city,
            "appid": WEATHER_API_KEY,
            "units": WEATHER_UNITS,
            "lang": WEATHER_LANG
        }
        response = requests.get(WEATHER_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        temp = data["main"]["temp"]
        description = data["weather"][0]["description"]
        return f"{city} için şu an hava {description}, sıcaklık {temp}°C civarında."
    except Exception as e:
        return f"Hava durumu servisi hata verdi: {str(e)}"

@app.route("/", methods=["GET"])
def home():
    return "KAAN server aktif!", 200

@app.route("/api/command", methods=["POST"])
def chat():
    global chat_history
    data = request.get_json()
    message = data.get("message", "")
    history_count = len(chat_history)

    lower_msg = message.lower()

    if "hava" in lower_msg and "nasıl" in lower_msg:
        weather_response = get_weather(WEATHER_CITY)
        return jsonify({
            "history_count": history_count,
            "response": weather_response
        })

    if "saat" in lower_msg and "kaç" in lower_msg:
        now_istanbul = datetime.now(pytz.timezone("Europe/Istanbul"))
        current_time = now_istanbul.strftime("%H:%M")
        return jsonify({
            "history_count": history_count,
            "response": f"Şu an saat {current_time} civarı, komutan!"
        })

    if "tarih" in lower_msg:
        now_istanbul = datetime.now(pytz.timezone("Europe/Istanbul"))
        current_date = now_istanbul.strftime("%d %B %Y")
        return jsonify({
            "history_count": history_count,
            "response": f"Bugünün tarihi: {current_date}."
        })

    today_date = datetime.now(pytz.timezone("Europe/Istanbul")).strftime("%d %B %Y")
    system_message = {
        "role": "system",
        "content": f"""Sen KAAN adında bir yapay zekâ asistansın. Bugünün tarihi: {today_date}.
Konuşma dilin Türkçe. Mizahi, samimi ve gerektiğinde ağırbaşlı bir tavrın var.
Kullanıcı sana soru sormadıkça asla 'Size nasıl yardımcı olabilirim?' gibi sorular sorma.
Direkt yanıt ver. Kendini kibar bir çağrı merkezi robotu gibi değil, dost gibi hisset.
Ama gerekirse disiplinli de ol. Eğer kullanıcı tarihi sorarsa bugünün tarihini net söyle."""
    }

    chat_history.append({"role": "user", "content": message})

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [system_message] + chat_history
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
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
