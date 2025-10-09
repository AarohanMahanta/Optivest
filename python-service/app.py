from flask import Flask, request, jsonify
import yfinance as yf
import numpy as np
import pandas as pd
from scipy.optimize import minimize
import traceback

app = Flask(__name__)

def clean_json(value):
    #New Addition: Handling the edge-case
    """Convert NaN/Inf to None for JSON serialization"""
    if isinstance(value, float) and (np.isnan(value) or np.isinf(value)):
        return None
    if isinstance(value, list):
        return [clean_json(v) for v in value]
    if isinstance(value, dict):
        return {k: clean_json(v) for k, v in value.items()}
    return value

@app.route('/optimise', methods=['POST'])
def optimise():
    try:
        data = request.get_json()
        tickers = data.get("tickers", [])
        period = data.get("period", "1y")  #Default to 1 year

        if not tickers:
            return jsonify({"error": "No tickers provided"}), 400

        #Fetch historical prices
        prices = yf.download(tickers, period=period, group_by='ticker', auto_adjust=True)

        if prices.empty:
            return jsonify({"error": "No data returned from yfinance for these tickers"}), 400

        #Handle single vs multiple tickers
        if len(tickers) == 1:
            adj_close = prices['Close'].to_frame()
            if isinstance(adj_close, pd.Series):
                adj_close = adj_close.to_frame()
            adj_close.columns = tickers
        else:
            try:
                adj_close = pd.DataFrame({t: prices[t]['Close'] for t in tickers})
            except KeyError:
                return jsonify({"error": "Some tickers returned no data"}), 400

        #Calculate daily returns
        daily_returns = adj_close.pct_change().dropna()
        if daily_returns.empty:
            return jsonify({"error": "Not enough data to calculate returns"}), 400

        mean_returns = daily_returns.mean() * 252  #Annualized
        covariance_matrix = daily_returns.cov() * 252  #Annualized

        n = len(tickers)

        def negative_sharpe(weights, mean_returns, covariance_matrix):
            portfolio_return = np.dot(weights, mean_returns)
            portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
            if portfolio_volatility == 0:
                return 0
            return -(portfolio_return / portfolio_volatility)

        constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
        bounds = tuple((0, 1) for _ in range(n))
        initial_weights = np.ones(n) / n

        opt_result = minimize(
            negative_sharpe,
            initial_weights,
            args=(mean_returns, covariance_matrix),
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        if not opt_result.success:
            return jsonify({"error": "Optimization failed"}), 400

        weights = opt_result.x
        portfolio_return = np.dot(weights, mean_returns)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
        sharpe_ratio = portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0

        result = {
            "weights": {tickers[i]: round(weights[i], 4) for i in range(n)},
            "expectedReturn": round(portfolio_return * 100, 2),
            "volatility": round(portfolio_volatility * 100, 2),
            "sharpeRatio": round(sharpe_ratio, 2),
            "period": period
        }

        return jsonify(clean_json(result))

    except Exception as e:
        #Print full traceback for debugging
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5500)
