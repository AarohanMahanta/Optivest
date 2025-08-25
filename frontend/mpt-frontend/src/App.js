import React, { useState } from "react";
import AddAssetForm from "./Components/AddAssetForm";
import AssetList from "./Components/AssetList";

function App() {
  const [selectedAssets, setSelectedAssets] = useState([]);
  const [result, setResult] = useState(null);
  const [period, setPeriod] = useState("1y");

  const handleOptimise = async () => {
  try {
    const response = await fetch("http://localhost:8080/api/assets/optimise/chosen", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        tickers: selectedAssets.map(asset => asset.ticker),
        period: period
      })
    });

    if (!response.ok) throw new Error("Network response was not ok");
    const data = await response.json();
    console.log("Optimisation result:", data);
    setResult(data);   //display results
  } catch (error) {
    console.error("Optimisation error:", error);
  }
};




  return (
    <div style={{ padding: "20px" }}>
      <h1>MPT Optimiser</h1>

      {/* Step 1: Add asset */}
      <AddAssetForm onAssetAdded={() => window.location.reload()} />

      {/* Step 2: Show assets as boxes */}
      <AssetList onSelectionChange={setSelectedAssets} />

      {/* Step 3: Period + optimise button */}
      <div style={{ marginTop: "20px" }}>
        <label>Period: </label>
        <select value={period} onChange={(e) => setPeriod(e.target.value)}>
          <option value="1d">1 Day</option>
          <option value="5d">5 Days</option>
          <option value="1mo">1 Month</option>
          <option value="6mo">6 Months</option>
          <option value="1y">1 Year</option>
          <option value="5y">5 Years</option>
        </select>
        <button onClick={handleOptimise} style={{ marginLeft: "10px" }}>
          Optimise
        </button>
      </div>

      {/* Show results */}
      {result && (
        <div style={{ marginTop: "20px" }}>
          <h3>Results</h3>
          <p>Expected Return: {result.expectedReturn}</p>
          <p>Volatility: {result.volatility}</p>
          <p>Sharpe Ratio: {result.sharpeRatio}</p>
          <h4>Weights:</h4>
          <ul>
            {result.weights &&
              Object.entries(result.weights).map(([ticker, weight]) => (
                <li key={ticker}>
                  {ticker}: {weight}
                </li>
              ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;
