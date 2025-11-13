import os
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from scipy.optimize import minimize
import requests
from io import StringIO

ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY", "YOUR_API_KEY_HERE")

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
        if isinstance(value, float) and (np.isnan(value) or np.isinf(value)):
            return None
        if isinstance(value, list):
            return [PortfolioOptimiser.clean_json(v) for v in value]
        if isinstance(value, dict):
            return {k: PortfolioOptimiser.clean_json(v) for k, v in value.items()}
        return value

    @staticmethod
    def safe_percent(value):
        if value is None or np.isnan(value):
            return None
        return round(value * 100, 2)

    def fetch_prices_stooq(self, ticker, period="1y"):
        symbol = ticker.lower()
        if not symbol.endswith(".us"):
            symbol = f"{symbol}.us"
        url = f"https://stooq.com/q/d/l/?s={symbol}&i=d"
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                print(f"Failed to fetch {ticker}: HTTP {resp.status_code}")
                return None
            if "Date" not in resp.text:
                print(f"Invalid CSV for {ticker}")
                return None
            df = pd.read_csv(StringIO(resp.text), parse_dates=["Date"]).set_index("Date")
            df.sort_index(inplace=True)
            return df[["Close"]]
        except Exception as e:
            print(f"Exception fetching {ticker}: {e}")
            return None


    def optimise(self):
        data = request.get_json()
        tickers = data.get("tickers", [])
        period = data.get("period", "1y")

        if not tickers:
            return jsonify({"error": "No tickers provided"}), 400

        adj_close = pd.DataFrame()
        for ticker in tickers:
            df = self.fetch_prices_stooq(ticker)
            if df is not None:
                adj_close[ticker] = df["Close"]
            else:
                print(f"Failed to fetch data for {ticker}")

        valid_tickers = [t for t in tickers if t in adj_close.columns]
        if adj_close.empty:
            return jsonify({"error": "No valid ticker data available"}), 400

        # Limit to last 252 trading days (1 year)
        adj_close = adj_close.tail(252)

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
