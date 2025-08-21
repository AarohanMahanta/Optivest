from flask import Flask, request, jsonify
import yfinance as yf
import numpy as np
import pandas as pd

app = Flask(__name__)

@app.route('/optimise', methods=['POST'])
def optimise():
    data = request.get_json()
    tickers = data.get("tickers", [])

    if not tickers:
        return jsonify({"error": "No tickers provided"}), 400

    # retrieving prices from yfinance
    prices = yf.download(tickers, period="1y", group_by='ticker', auto_adjust=True)
    # Adjusted Close prices; better suited for return calculations compared to raw close prices

    # handling single vs multiple tickers
    if len(tickers) == 1:
        adj_close = prices['Close'].to_frame()  # Single ticker: convert Series to DataFrame
        adj_close.columns = tickers
    else:
        adj_close = pd.DataFrame({t: prices[t]['Close'] for t in tickers})  # Multiple tickers

    # calculating daily daily_returns
    daily_returns = adj_close.pct_change().dropna()  # Day to day percentage change in those prices

    # expected return expressed as arithmetic mean of historical daily daily_returns
    mean_returns = daily_returns.mean()

    # calculating the covariance between each pair of tickers
    covariance_matrix = daily_returns.cov()

    # implementing a naive equal weights portfolio for temporary testing purposes
    n = len(tickers)
    weights = np.ones(n) / n  # np array of size n eg. [1, 1, 1, ... 1] for equal weights and dividing every value by n

    # calculating portfolio return and volatility
    portfolio_return = np.dot(weights, mean_returns) * 252  # 252 is number of trading days annually
    portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix * 252, weights)))
    sharpe_ratio = portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0

    result = {
        "weights": {tickers[i]: float(weights[i]) for i in range(n)},
        "expectedReturn": float(portfolio_return),
        "volatility": float(portfolio_volatility),
        "sharpeRatio": float(sharpe_ratio)
    }

    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
