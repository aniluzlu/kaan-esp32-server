from flask import Flask, request, Response
import requests
import json
from datetime import datetime
from pytz import timezone

app = Flask(__name__)

@app.route("/api/command", methods=["POST"])
def command():
    user_message = request.json.get("message", "")

    # Sistem mesajı
    now = datetime.now(timezone("Europe/Istanbul"))
    formatted_time = now.strftime("%H:%M")
    formatted_date = now.strftime("%d %B %Y")

    system_message = {
        "role": "system",
        "content": f"Sen KAAN adında bir yapay zekâ asistansın. Bugünün tarihi: {formatted_date}, saat: {formatted_time}. Konuşma dilin Türkçe. Mizahi, samimi ve gerektiğinde ağırbaşlı bir tavrın var. Kullanıcı sana soru sormadıkça asla 'Size nasıl yardımcı olabilirim?' gibi sorular sorma. Direkt yanıt ver. Kendini kibar bir çağrı merkezi robotu gibi değil, dost gibi hisset. Ama gerekirse disiplinli de ol. Eğer kullanıcı tarihi, saati, hava durumunu veya güncel verileri sorarsa doğru ve dinamik şekilde yanıtla."
    }

    messages = [system_message, {"role": "user", "content": user_message}]

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": "Bearer YOUR_API_KEY",
            "Content-Type": "application/json"
        },
        json={
            "model": "openai/gpt-3.5-turbo",
            "messages": messages
        }
    )

    assistant_reply = response.json()["choices"][0]["message"]["content"]

    return Response(
        json.dumps({"history_count": 1, "response": assistant_reply}, ensure_ascii=False),
        mimetype="application/json"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
