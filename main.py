
from flask import Flask, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)

# OpenAI API istemcisi oluşturuluyor
client = OpenAI(api_key=os.getenv("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"))

@app.route("/", methods=["GET"])
def index():
    return "KAAN ESP32 Sunucusu Aktif! 🧠"

@app.route("/api/command", methods=["POST"])
def command():
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "Mesaj boş olamaz"}), 400

    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Sen KAAN adında Türk yapımı bir zırhlı kask asistanısın."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7
        )

        assistant_reply = completion.choices[0].message.content

        return jsonify({
            "response": assistant_reply
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

if __name__ == "__main__":
    app.run(debug=True)
