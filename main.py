# -*- coding: utf-8 -*-
import os
import requests
from flask import Flask, request, Response, jsonify
from datetime import datetime
import pytz
import json

app = Flask(__name__)

# Hafıza sistemi
chat_history = []

# API Anahtarları ve ayarlar
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "openai/gpt-3.5-turbo"

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
WEATHER_CITY = "Bursa"
WEATHER_UNITS = "metric"
WEATHER_LANG = "tr"

# Saat ve tarih bilgisi
def get_datetime_info():
    now = datetime.now(pytz.timezone("Europe/Istanbul"))
    tarih = now.strftime("%d %B %Y")
    saat = now.strftime("%H:%M")
    return tarih, saat

# Hava durumu
def get_weather(city):
    if not WEATHER_API_KEY:
        return "Hava durumu servisi ayarlanmadı."
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
        return f"Hava durumu alınamadı: {str(e)}"

@app.route("/", methods=["GET"])
def home():
    return "KAAN server ayakta, komutan!", 200

@app.route("/api/command", methods=["POST"])
def chat():
    global chat_history

    data = request.get_json()
    message = data.get("message", "").lower()
    history_count = len(chat_history)

    # Komutlara özel teknik yanıtlar
    command_triggers = {
        "kaskı kapat": {
            "reply": "Tüm Ulu Kağanlara Selam Olsun!",
            "actions": "servo:kapat; led:yan; sound:servo.mp3; sound:metal.mp3"
        },
        "kaskı aç": {
            "reply": "Harp Türklüğündür!",
            "actions": "led:son; servo:ac; sound:servo.mp3"
        },
        "kaskı hazırla": {
            "reply": "Kask hazır, Anıl.",
            "actions": "sound:hazir.mp3"
        }
    }

    # Fonksiyon içindeyken kontrol
    for trigger, details in command_triggers.items():
        if trigger in message:
            return Response(
                json.dumps({
                    "history_count": history_count,
                    "response": details["reply"],
                    "actions": details["actions"]
                }, ensure_ascii=False).encode("utf-8"),
                content_type="application/json; charset=utf-8"
            )

    # 📅 Tarih ve saat
    if "hava" in message and "nasıl" in message:
        return Response(
            json.dumps({
                "history_count": history_count,
                "response": get_weather(WEATHER_CITY)
            }, ensure_ascii=False).encode("utf-8"),
            content_type="application/json; charset=utf-8"
        )

    if "tarih" in message:
        tarih, _ = get_datetime_info()
        return Response(
            json.dumps({
                "history_count": history_count,
                "response": f"Bugünün tarihi: {tarih}"
            }, ensure_ascii=False).encode("utf-8"),
            content_type="application/json; charset=utf-8"
        )

    if "saat" in message and "kaç" in message:
        _, saat = get_datetime_info()
        return Response(
            json.dumps({
                "history_count": history_count,
                "response": f"Şu an saat {saat} civarında, komutan!"
            }, ensure_ascii=False).encode("utf-8"),
            content_type="application/json; charset=utf-8"
        )

    # 💬 ChatGPT tabanlı doğal yanıtlar
    chat_history.append({"role": "user", "content": message})
    tarih, saat = get_datetime_info()

    system_content = f"""Sen KAAN adında bir yapay zekâ asistansın. Bugünün tarihi: {tarih}, saat: {saat}.
- Anıl'a yardımcı oluyorsun.
- Konuşma tarzın fırlama, samimi ama gerektiğinde ciddi.
- Sürekli 'Nasıl yardımcı olabilirim?' gibi şeyler söyleme.
- Anıl seni yönlendirdikçe yanıt ver, çağrı merkezi gibi davranma.
- Gereksiz kibarlıklardan kaçın."""

    system_message = {
        "role": "system",
        "content": system_content
    }

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
        return Response(
            json.dumps({
                "history_count": history_count,
                "response": reply
            }, ensure_ascii=False).encode("utf-8"),
            content_type="application/json; charset=utf-8"
        )
    else:
        return Response(
            json.dumps({
                "error": "OpenRouter yanıt vermedi.",
                "details": response.text
            }, ensure_ascii=False).encode("utf-8"),
            content_type="application/json; charset=utf-8"
        )

if __name__ == "__main__":
    app.run(debug=True)
