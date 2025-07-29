from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return "KAAN ESP32 Sunucusu çalışıyor!"

@app.route('/command', methods=['POST'])
def command():
    data = request.get_json()
    print("Komut alındı:", data)
    return jsonify({"status": "OK", "received": data})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
