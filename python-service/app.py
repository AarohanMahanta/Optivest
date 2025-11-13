import os
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from scipy.optimize import minimize
import investpy

class PortfolioOptimiser:
    def __init__(self):
        self.app = Flask(__name__)
        self.register_routes()

    def register_routes(self):
        self.app.add_url_rule("/health", "health", self.health)
        self.app.add_url_rule("/optimise", "optimise", self.optimise, methods=["POST"])

    def health(self):
        return "OK", 200

    @staticmethod
    def clean_json(value):
        """Recursively replace NaN or Inf with None for JSON safety."""
        if isinstance(value, float) and (np.isnan(value) or np.isinf(value)):
            return None
        if isinstance(value, list):
            return [PortfolioOptimiser.clean_json(v) for v in value]
        if isinstance(value, dict):
            return {k: PortfolioOptimiser.clean_json(v) for k, v in value.items()}
        return value

    @staticmethod
    def safe_percent(value):
        """Convert a float to a percentage number, or None if invalid."""
        if value is None or np.isnan(value):
            return None
        return round(value * 100, 2)

    @staticmethod
    def fetch_prices(tickers, period="1y"):
        """Fetch stock prices using investpy."""
        adj_close = pd.DataFrame()
        for ticker in tickers:
            try:
                df = investpy.stocks.get_stock_historical_data(
                    stock=ticker,
                    country="united states",
                    from_date="01/11/2023",
                    to_date="13/11/2025"
                )
                adj_close[ticker] = df["Close"]
            except Exception as e:
                print(f"Failed to fetch {ticker}: {e}")
        return adj_close

    def optimise(self):
        data = request.get_json()
        tickers = data.get("tickers", [])
        period = data.get("period", "1y")

        if not tickers:
            return jsonify({"error": "No tickers provided"}), 400

        adj_close = self.fetch_prices(tickers, period)
        valid_tickers = [t for t in tickers if t in adj_close.columns]

        if adj_close.empty:
            return jsonify({"error": "No valid ticker data available"}), 400

        daily_returns = adj_close.pct_change().dropna()
        if daily_returns.empty:
            return jsonify({"error": "Insufficient data to calculate returns"}), 400

        mean_returns = daily_returns.mean() * 252
        covariance_matrix = daily_returns.cov() * 252

        n = len(valid_tickers)
        if n == 0:
            return jsonify({"error": "No valid tickers after processing"}), 400

        def negative_sharpe(weights):
            port_return = np.dot(weights, mean_returns)
            port_vol = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
            return -(port_return / port_vol) if port_vol > 0 else 0

        constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
        bounds = tuple((0, 1) for _ in range(n))
        initial_guess = np.ones(n) / n

        opt_result = minimize(
            negative_sharpe,
            initial_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        weights = opt_result.x if opt_result.success else initial_guess
        portfolio_return = np.dot(weights, mean_returns)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
        sharpe_ratio = portfolio_return / portfolio_volatility if portfolio_volatility > 0 else None

        result = {
            "weights": {valid_tickers[i]: self.safe_percent(weights[i]) for i in range(n)},
            "expectedReturn": self.safe_percent(portfolio_return),
            "volatility": self.safe_percent(portfolio_volatility),
            "sharpeRatio": round(sharpe_ratio, 2) if sharpe_ratio is not None else None,
            "period": period,
            "requestedTickers": tickers,
            "validTickers": valid_tickers
        }

        return jsonify(self.clean_json(result))

    def run(self):
        port = int(os.environ.get("PORT", 5000))
        self.app.run(host="0.0.0.0", port=port, debug=True)


if __name__ == "__main__":
    optimiser = PortfolioOptimiser()
    optimiser.run()
