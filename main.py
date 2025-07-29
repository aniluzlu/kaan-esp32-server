from flask import Flask, request, jsonify

app = Flask(__name__)

# En son gönderilen komut burada saklanacak
latest_command = {"command": "KAAN, kaskı hazırla"}  # başlangıç komutu

@app.route('/')
def index():
    return "KAAN ESP32 Sunucusu çalışıyor!"

# Android uygulaması bu endpoint'e POST ile komut gönderiyor
@app.route('/api/command', methods=['POST'])
def post_command():
    global latest_command
    latest_command = request.get_json()
    print("Komut alındı:", latest_command)
    return jsonify({"status": "OK", "received": latest_command})

# ESP32 bu endpoint'ten komutu GET ile çekiyor
@app.route('/api/command', methods=['GET'])
def get_command():
    return jsonify(latest_command)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
