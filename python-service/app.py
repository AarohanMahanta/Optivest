from flask import Flask, request, jsonify
import yfinance as yf


app = Flask(__name__)

@app.route('/optimise', methods=['POST'])
def optimise():
    data = request.get_json()
    tickers = data.get("tickers", [])

    if not tickers:
        return jsonify({"error" : "No tickers provided"}), 400

    #retrieving prices from yfinance
    prices = yf.download(tickers, period="1y")['Adj Close'] #Adjusted Close prices; better suited for return calculations compared to raw close prices

