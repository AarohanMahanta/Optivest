import React, { useState } from "react";

export default function AddAssetForm({ onAssetAdded }) {
  const [ticker, setTicker] = useState("");

  const handleAdd = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch("http://localhost:8080/api/assets", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ticker }),
      });
      if (response.ok) {
        setTicker("");
        onAssetAdded(); // refresh asset list
      }
    } catch (err) {
      console.error("Error adding asset:", err);
    }
  };

  return (
    <form onSubmit={handleAdd} style={{ marginBottom: "20px" }}>
      <input
        type="text"
        value={ticker}
        placeholder="Enter ticker (e.g. AAPL)"
        onChange={(e) => setTicker(e.target.value)}
        style={{ marginRight: "10px" }}
      />
      <button type="submit">Add Asset</button>
    </form>
  );
}
