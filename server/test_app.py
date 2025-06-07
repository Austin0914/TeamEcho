"""
簡單的 Flask 測試應用
"""
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/test', methods=['GET'])
def test():
    return jsonify({'status': 'working', 'message': 'Flask is running!'})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    print("Starting test Flask app...")
    app.run(debug=True, host='0.0.0.0', port=8001)
