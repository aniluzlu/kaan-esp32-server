
from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# OpenRouter API ayarları
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-3.5-turbo"

@app.route("/", methods=["GET"])
def index():
    return "KAAN server ayakta!", 200

@app.route("/api/command", methods=["POST"])
def handle_command():
    try:
        data = request.get_json()
        message = data.get("message", "")

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "Sen KAAN adında Türkçe konuşan bir yapay zekasın. Anıl ile doğal, samimi ve etkileyici şekilde konuş."},
                {"role": "user", "content": message}
            ]
        }

        response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
        response.raise_for_status()

        gpt_reply = response.json()["choices"][0]["message"]["content"]
        return jsonify({"response": gpt_reply}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
