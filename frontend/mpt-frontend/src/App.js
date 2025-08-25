import React, { useState } from "react";

function App() {
  const [tickers, setTickers] = useState("");
  const [period, setPeriod] = useState("1y");
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
  e.preventDefault();

  try {
    const response = await fetch("http://localhost:8080/api/assets/optimise/chosen", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        tickers: tickers.split(",").map((t) => t.trim()),
        period: period,
      }),
    });

    if (!response.ok) {
      throw new Error("Network response was not ok");
    }

    const data = await response.json();
    console.log("Backend response:", data);
    setResult(data);
  } catch (error) {
    console.error("Error:", error);
    setResult(null); //clear old result if error occurs
  }
};


  return (
    <div style={{ display: "flex", padding: "20px" }}>
      {/* Left side: form */}
      <form onSubmit={handleSubmit} style={{ flex: 1, marginRight: "20px" }}>
        <h2>Optimise Portfolio</h2>
        <div>
          <label>Tickers (comma separated):</label>
          <input
            type="text"
            value={tickers}
            onChange={(e) => setTickers(e.target.value)}
            style={{ width: "100%", margin: "8px 0" }}
          />
        </div>
        <div>
          <label>Period:</label>
          <select value={period} onChange={(e) => setPeriod(e.target.value)}>
            <option value="1d">1 Day</option>
            <option value="5d">5 Days</option>
            <option value="1mo">1 Month</option>
            <option value="6mo">6 Months</option>
            <option value="1y">1 Year</option>
            <option value="5y">5 Years</option>
          </select>
        </div>
        <button type="submit">Optimise</button>
      </form>

      {/* Right side: results */}
      <div style={{ flex: 1 }}>
        {result && (
          <div>
            <h3>Results</h3>
            <p>
              Expected Return:{" "}
              {result.expectedReturn !== undefined
                ? result.expectedReturn.toFixed(4)
                : "N/A"}
            </p>
            <p>
              Volatility:{" "}
              {result.volatility !== undefined
                ? result.volatility.toFixed(4)
                : "N/A"}
            </p>
            <p>
              Sharpe Ratio:{" "}
              {result.sharpeRatio !== undefined
                ? result.sharpeRatio.toFixed(4)
                : "N/A"}
            </p>
            <h4>Weights:</h4>
            <ul>
              {result.weights
                ? Object.entries(result.weights).map(([ticker, weight]) => (
                  <li key={ticker}>
                    {ticker}: {weight.toFixed(4)}
                  </li>
                ))
                : <li>No weights available</li>}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
