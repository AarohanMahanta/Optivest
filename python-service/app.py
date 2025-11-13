import os
import time
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from scipy.optimize import minimize
import yfinance as yf
import finnhub


class PortfolioOptimiser:
    def __init__(self):
        self.app = Flask(__name__)
        self.register_routes()

        # Finnhub setup
        self.finnhub_api_key = os.getenv("FINNHUB_API_KEY")
        self.finnhub_client = finnhub.Client(api_key=self.finnhub_api_key) if self.finnhub_api_key else None

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
    def download_prices_yf(tickers, period, retries=3, delay=5):
        """Download ticker data from yfinance with retry logic."""
        for attempt in range(retries):
            try:
                data = yf.download(
                    tickers,
                    period=period,
                    group_by="ticker",
                    auto_adjust=True,
                    progress=False,
                )
                return data
            except Exception as e:
                print(f"yfinance attempt {attempt+1} failed: {e}")
                time.sleep(delay)
        return pd.DataFrame()

    def download_prices_finnhub(self, tickers, period):
        """Download data from Finnhub as fallback."""
        if not self.finnhub_client:
            print("Finnhub API key not found, skipping fallback.")
            return pd.DataFrame()

        days_map = {"1y": 365, "6mo": 180, "3mo": 90, "1mo": 30}
        days = days_map.get(period, 365)
        now = int(pd.Timestamp.now().timestamp())
        frm = int((pd.Timestamp.now() - pd.Timedelta(days=days)).timestamp())

        price_data = {}
        for t in tickers:
            try:
                candles = self.finnhub_client.stock_candles(
                    symbol=t, resolution="D", _from=frm, to=now
                )
                if candles and candles.get("s") == "ok" and "c" in candles:
                    price_data[t] = pd.Series(candles["c"], dtype=float)
            except Exception as e:
                print(f"Finnhub failed for {t}: {e}")

        if not price_data:
            return pd.DataFrame()

        return pd.DataFrame(price_data)

    def optimise(self):
        data = request.get_json()
        tickers = data.get("tickers", [])
        period = data.get("period", "1y")

        if not tickers:
            return jsonify({"error": "No tickers provided"}), 400

        # Step 1: Try Yahoo Finance
        prices = self.download_prices_yf(tickers, period)
        if prices.empty:
            print("Falling back to Finnhub...")
            prices = self.download_prices_finnhub(tickers, period)

        if prices.empty:
            return jsonify({"error": "No valid ticker data available"}), 400

        # Handle MultiIndex vs single ticker
        adj_close = pd.DataFrame()
        valid_tickers = []
        if isinstance(prices.columns, pd.MultiIndex):
            for t in tickers:
                if t in prices:
                    adj_close[t] = prices[t]["Close"]
                    valid_tickers.append(t)
        else:
            if "Close" in prices.columns:
                adj_close = prices["Close"].to_frame() if len(tickers) == 1 else prices
            else:
                adj_close = prices
            adj_close = adj_close[[c for c in adj_close.columns if c in tickers]]
            valid_tickers = list(adj_close.columns)

        if adj_close.empty:
            return jsonify({"error": "No valid ticker data available"}), 400

        # Calculate daily returns
        daily_returns = adj_close.pct_change().dropna()
        if daily_returns.empty:
            return jsonify({"error": "Insufficient data to calculate returns"}), 400

        mean_returns = daily_returns.mean() * 252
        covariance_matrix = daily_returns.cov() * 252

        n = len(valid_tickers)
        if n == 0:
            return jsonify({"error": "No valid tickers after processing"}), 400

        # Sharpe ratio optimization
        def negative_sharpe(weights):
            port_return = np.dot(weights, mean_returns)
            port_vol = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
            return -(port_return / port_vol) if port_vol > 0 else 0

        constraints = {"type": "eq", "fun": lambda w: np.sum(w) - 1}
        bounds = tuple((0, 1) for _ in range(n))
        initial_guess = np.ones(n) / n

        opt_result = minimize(
            negative_sharpe,
            initial_guess,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
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
        }

        return jsonify(self.clean_json(result))

    def run(self):
        port = int(os.environ.get("PORT", 5000))
        self.app.run(host="0.0.0.0", port=port, debug=True)


if __name__ == "__main__":
    optimiser = PortfolioOptimiser()
    optimiser.run()
