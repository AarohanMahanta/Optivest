import React, { useEffect, useState } from "react";

function AssetList({ onSelectionChange }) {
  const [assets, setAssets] = useState([]);
  const [selected, setSelected] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8080/api/assets")
      .then(res => res.json())
      .then(data => setAssets(data));
  }, []);

  const toggleSelection = (asset) => {
    let updated;
    if (selected.find(a => a.id === asset.id)) {
      updated = selected.filter(a => a.id !== asset.id);
    } else {
      updated = [...selected, asset];
    }
    setSelected(updated);
    onSelectionChange(updated); // pass full asset (with ticker) back
  };

  return (
    <div style={{ marginTop: "20px" }}>
      <h3>Assets</h3>
      <ul>
        {assets.map(asset => (
          <li key={asset.id}>
            <label>
              <input
                type="checkbox"
                checked={!!selected.find(a => a.id === asset.id)}
                onChange={() => toggleSelection(asset)}
              />
              {asset.ticker} (Return: {asset.expectedReturn}, Volatility: {asset.volatility})
            </label>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default AssetList;
