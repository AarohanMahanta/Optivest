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

    #calculating daily daily_returns
    daily_returns = prices.pct_change().dropna() #Day to day percentage change in those prices

    #expected return expressed as arithmetic mean of historical daily daily_returns
    mean_returns = daily_returns.mean()
    #calculating the covariance between each pair of tickers
    covariance_matrix = daily_returns.cov()