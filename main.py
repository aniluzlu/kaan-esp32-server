
from flask import Flask, request, jsonify
import openai

app = Flask(__name__)

# OpenRouter API ayarları
openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

@app.route("/", methods=["GET"])
def index():
    return "KAAN ESP32 Sunucusu (OpenRouter bağlantılı) çalışıyor."

@app.route("/api/command", methods=["POST"])
def command():
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "Mesaj boş olamaz"}), 400

    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-3.5-turbo",  # OpenRouter'da desteklenen model
            messages=[
                {"role": "system", "content": "Sen KAAN adında Türk yapımı bir zırhlı kask asistanısın."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7
        )

        assistant_reply = response.choices[0].message.content

        return jsonify({
            "response": assistant_reply
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

if __name__ == "__main__":
    app.run(debug=True)
