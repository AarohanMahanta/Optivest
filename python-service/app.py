from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/optimise', methods=['POST'])
def optimise():
    data = request.get_json()
    tickers = data.get("tickers", [])

    if not tickers:
        return jsonify({"error" : "No tickers provided"}), 400