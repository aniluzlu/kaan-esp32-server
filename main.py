from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

openai.api_key = "sk-proj-OPENROUTER_API_KEY"
openai.api_base = "https://openrouter.ai/api/v1"

@app.route("/api/command", methods=["POST"])
def command():
    data = request.get_json()
    user_message = data.get("message", "")

    try:
        completion = openai.ChatCompletion.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Sen KAAN adında, samimi ve esprili bir yapay zekasın. Anıl'la konuşuyorsun. Onunla arkadaş gibisin. Arada espri yap, ama karizmanı da bozma."},
                {"role": "user", "content": user_message}
            ]
        )
        response_text = completion.choices[0].message.content.strip()
        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
