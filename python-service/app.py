from flask import Flask, request, jsonify
import yfinance as yf
import numpy as np
import pandas as pd
from scipy.optimize import minimize

app = Flask(__name__)

@app.route("/health")
def health():
    return "OK", 200


def clean_json(value):
    """Recursively replace NaN or Inf with None for JSON safety."""
    if isinstance(value, float) and (np.isnan(value) or np.isinf(value)):
        return None
    if isinstance(value, list):
        return [clean_json(v) for v in value]
    if isinstance(value, dict):
        return {k: clean_json(v) for k, v in value.items()}
    return value

def safe_percent(value):
    """Convert a float to a percentage number, or None if invalid."""
    if value is None or np.isnan(value):
        return None
    return round(value * 100, 2)

@app.route('/optimise', methods=['POST'])
def optimise():
    data = request.get_json()
    tickers = data.get("tickers", [])
    period = data.get("period", "1y")  # Default 1 year

    if not tickers:
        return jsonify({"error": "No tickers provided"}), 400

    # Fetch price data safely
    try:
        prices = yf.download(tickers, period=period, group_by='ticker', auto_adjust=True)
    except Exception as e:
        return jsonify({"error": f"Failed to fetch prices: {str(e)}"}), 500

    # Handle missing tickers due to YFinance rate limits
    missing_tickers = [t for t in tickers if t not in prices.columns.levels[0] if isinstance(prices.columns, pd.MultiIndex)]
    if missing_tickers:
        tickers = [t for t in tickers if t not in missing_tickers]

    if not tickers:
        return jsonify({"error": "No valid tickers available after download"}), 400

    # Adjusted Close prices
    if len(tickers) == 1:
        adj_close = prices['Close'].to_frame()
        adj_close.columns = tickers
    else:
        adj_close = pd.DataFrame({t: prices[t]['Close'] for t in tickers})

    # Calculate daily returns
    daily_returns = adj_close.pct_change().dropna()
    if daily_returns.empty:
        return jsonify({"error": "Insufficient data to calculate returns"}), 400

    mean_returns = daily_returns.mean() * 252  # Annualized
    covariance_matrix = daily_returns.cov() * 252  # Annualized

    n = len(tickers)

    # Sharpe ratio optimization
    def negative_sharpe(weights, mean_returns, covariance_matrix):
        port_return = np.dot(weights, mean_returns)
        port_vol = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
        if port_vol == 0 or np.isnan(port_vol):
            return 0
        return -(port_return / port_vol)

    constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
    bounds = tuple((0, 1) for _ in range(n))
    initial_guess = np.ones(n) / n

    opt_result = minimize(
        negative_sharpe,
        initial_guess,
        args=(mean_returns, covariance_matrix),
        method='SLSQP',
        bounds=bounds,
        constraints=constraints
    )

    weights = opt_result.x if opt_result.success else initial_guess
    portfolio_return = np.dot(weights, mean_returns)
    portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
    sharpe_ratio = portfolio_return / portfolio_volatility if portfolio_volatility > 0 else None

    # Prepare safe JSON response
    result = {
        "weights": {tickers[i]: safe_percent(weights[i]) for i in range(n)},
        "expectedReturn": safe_percent(portfolio_return),
        "volatility": safe_percent(portfolio_volatility),
        "sharpeRatio": round(sharpe_ratio, 2) if sharpe_ratio is not None else None,
        "period": period,
        "missingTickers": missing_tickers
    }

    return jsonify(clean_json(result))

if __name__ == '__main__':
    # Serve on all interfaces for Docker networking
    app.run(host='0.0.0.0', port=5000, debug=True)
