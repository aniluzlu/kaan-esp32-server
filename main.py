from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

# OpenRouter API ayarları
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-3.5-turbo"

# Konuşma geçmişi (sunucu yeniden başlatıldığında sıfırlanır)
chat_history = []

@app.route("/", methods=["GET"])
def index():
    return "KAAN server ayakta! Konuşma geçmişi destekliyor.", 200

@app.route("/api/command", methods=["POST"])
def handle_command():
    try:
        data = request.get_json()
        user_message = data.get("message", "")
        if not user_message:
            return jsonify({"error": "Mesaj alanı boş olamaz"}), 400

        # Güncel tarihi al
        current_date = datetime.now().strftime("%d %B %Y")

        # Mesaj geçmişine yeni kullanıcı mesajını ekle
        chat_history.append({"role": "user", "content": user_message})

        # Sistem mesajı (karakter + tarih)
        system_prompt = (
            f"Bugünün tarihi: {current_date}. "
            "Sen KAAN adında bir yapay zekasın. Hafif fırlama, esprili ama gerektiğinde ağırbaşlısın. "
            "Anıl ile samimi bir arkadaş gibi konuş, teknik konularda detaylı açıklamalar yap."
        )

        # Tüm geçmişi modele gönder
        messages = [{"role": "system", "content": system_prompt}] + chat_history

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": MODEL,
            "messages": messages
        }

        response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
        response.raise_for_status()

        gpt_reply = response.json()["choices"][0]["message"]["content"]

        # Modelin cevabını geçmişe ekle
        chat_history.append({"role": "assistant", "content": gpt_reply})

        return jsonify({"response": gpt_reply, "history_count": len(chat_history)}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
