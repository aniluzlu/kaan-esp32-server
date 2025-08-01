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

# Hava durumu API key (Render ortam değişkeni)
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
    except requests.exceptions.HTTPError as http_err:
        return f"Hava durumu alınamadı: {http_err}"
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

    if "hava" in message.lower() and "nasıl" in message.lower():
        weather_response = get_weather(WEATHER_CITY)
        return jsonify({
            "history_count": history_count,
            "response": weather_response
        })

    if "saat" in message.lower() and "kaç" in message.lower():
        turkey_time = datetime.now(pytz.timezone("Europe/Istanbul"))
        current_time = turkey_time.strftime("%H:%M")
        return jsonify({
            "history_count": history_count,
            "response": f"Şu an saat {current_time} civarı, komutan!"
        })

    # Güncel tarih ve saat
    turkey_time = datetime.now(pytz.timezone("Europe/Istanbul"))
    bugunun_tarihi = turkey_time.strftime("%d %B %Y")
    saat = turkey_time.strftime("%H:%M")

    # Sistem mesajı – karakter tanımı
    system_message = {
        "role": "system",
        "content": f"""Sen KAAN adında bir yapay zekâ asistansın.
Bugünün tarihi: {bugunun_tarihi}
Şu an saat: {saat}
Karakterin şöyle:
- Anıl’a yardımcı olursun.
- Konuşma tarzın mizahi, samimi, gerektiğinde ciddi.
- Gereksiz yere “Nasıl yardımcı olabilirim?” gibi tekrar eden sorular sormazsın.
- Anıl’ın senden yardım istemesini beklersin, kendi kendine öneride bulunmazsın.
- Her zaman güncel verileri kullanmaya çalışırsın.
- Bugünün tarihi ve saati konusunda kullanıcıya yanlış bilgi verme."""
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
