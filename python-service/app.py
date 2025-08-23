from flask import Flask, request, jsonify
import yfinance as yf
import numpy as np
import pandas as pd
from scipy.optimize import minimize

app = Flask(__name__)

def clean_json(value):
    if isinstance(value, float) and (np.isnan(value) or np.isinf(value)):
        return None
    if isinstance(value, list):
        return [clean_json(v) for v in value]
    if isinstance(value, dict):
        return {k: clean_json(v) for k, v in value.items()}
    return value


@app.route('/optimise', methods=['POST'])
def optimise():
    data = request.get_json()
    tickers = data.get("tickers", [])
    period = data.get("period", "1y") #1y is default period

    if not tickers:
        return jsonify({"error": "No tickers provided"}), 400

    # retrieving prices from yfinance
    prices = yf.download(tickers, period=period, group_by='ticker', auto_adjust=True)
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
    mean_returns = daily_returns.mean() * 252 #(annualised)

    # calculating the covariance between each pair of tickers
    covariance_matrix = daily_returns.cov()* 252 #(annualised)

    # implementing a naive equal weights portfolio for temporary testing purposes
    n = len(tickers)

    def negative_sharpe(weights, mean_returns, covariance_matrix):
        portfolio_return = np.dot(weights, mean_returns)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
        return -(portfolio_return / portfolio_volatility)

    #sum of weights should be 1
    constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
    bounds = tuple((0, 1) for _ in range(n))

    #initially we assume that the optimisation includes equal weights
    initial_prediction = np.ones(n) / n

    #now optimise:
    opt_result = minimize(negative_sharpe, initial_prediction,
                          args=(mean_returns, covariance_matrix),
                          method='SLSQP',
                          bounds=bounds,
                          constraints=constraints)

    weights = opt_result.x
    portfolio_return = np.dot(weights, mean_returns)
    portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
    sharpe_ratio = portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0

    result = {
        "weights": {tickers[i]: float(weights[i]) for i in range(n)},
        "expectedReturn": float(portfolio_return),
        "volatility": float(portfolio_volatility),
        "sharpeRatio": float(sharpe_ratio),
        "period": period
    }

    return jsonify(clean_json(result))

if __name__ == '__main__':
    app.run(port=5000, debug=True)
