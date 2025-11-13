import os
import time
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from scipy.optimize import minimize
import finnhub

class PortfolioOptimiser:
    def __init__(self):
        self.app = Flask(__name__)
        self.register_routes()
        self.finnhub_client = finnhub.Client(api_key=os.getenv("FINNHUB_API_KEY"))

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

    def fetch_prices(self, ticker, period="1y"):
        """Fetch historical OHLC data from Finnhub."""
        now = int(time.time())
        period_map = {
            "1mo": 30 * 24 * 60 * 60,
            "3mo": 90 * 24 * 60 * 60,
            "6mo": 180 * 24 * 60 * 60,
            "1y": 365 * 24 * 60 * 60,
            "2y": 2 * 365 * 24 * 60 * 60,
            "5y": 5 * 365 * 24 * 60 * 60
        }
        start = now - period_map.get(period, 365 * 24 * 60 * 60)

        try:
            res = self.finnhub_client.stock_candles(ticker, 'D', start, now)
            if res.get("s") != "ok":
                return None
            df = pd.DataFrame({
                "Date": pd.to_datetime(res["t"], unit="s"),
                "Close": res["c"]
            }).set_index("Date")
            return df
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            return None

    def optimise(self):
        data = request.get_json()
        tickers = data.get("tickers", [])
        period = data.get("period", "1y")

        if not tickers:
            return jsonify({"error": "No tickers provided"}), 400

        price_data = {}
        for ticker in tickers:
            df = self.fetch_prices(ticker, period)
            if df is not None and not df.empty:
                price_data[ticker] = df["Close"]

        if not price_data:
            return jsonify({"error": "No valid ticker data available"}), 400

        adj_close = pd.DataFrame(price_data)
        adj_close.dropna(inplace=True)
        valid_tickers = list(adj_close.columns)

        if adj_close.empty:
            return jsonify({"error": "No valid data after cleaning"}), 400

        daily_returns = adj_close.pct_change().dropna()
        if daily_returns.empty:
            return jsonify({"error": "Insufficient data to calculate returns"}), 400

        mean_returns = daily_returns.mean() * 252
        covariance_matrix = daily_returns.cov() * 252
        n = len(valid_tickers)

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
            "validTickers": valid_tickers,
            "source": "finnhub"
        }

        return jsonify(self.clean_json(result))

    def run(self):
        port = int(os.environ.get("PORT", 5000))
        self.app.run(host='0.0.0.0', port=port, debug=True)


if __name__ == "__main__":
    optimiser = PortfolioOptimiser()
    optimiser.run()
