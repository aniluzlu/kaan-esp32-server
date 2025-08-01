import os
import json
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

# Ortam değişkeninden API anahtarını al
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise ValueError("OPENROUTER_API_KEY environment variable not set.")

# OpenRouter API'sine bağlanmak için istemci oluştur
client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)

@app.route("/api/command", methods=["POST"])
def handle_command():
    try:
        data = request.get_json()
        user_message = data.get("message", "")

        if not user_message:
            return jsonify({"error": "Message field is required"}), 400

        print(f"Gelen mesaj: {user_message}")

        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Sen KAAN adında, Türkçe konuşan bir yardımcı yapay zekasın."},
                {"role": "user", "content": user_message}
            ]
        )

        reply = response.choices[0].message.content.strip()
        print(f"Yanıt: {reply}")

        return jsonify({"response": reply}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
