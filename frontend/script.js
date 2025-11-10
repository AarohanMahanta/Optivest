const assetInput = document.getElementById("asset-input");
const addAssetBtn = document.getElementById("add-asset-btn");
const assetList = document.getElementById("asset-list");
const optimiseBtn = document.getElementById("optimise-btn");
const periodSelect = document.getElementById("period-select");

const expectedReturnEl = document.getElementById("expected-return");
const volatilityEl = document.getElementById("volatility");
const sharpeRatioEl = document.getElementById("sharpe-ratio");
const weightsList = document.getElementById("weights-list");

const API_URL = "https://optivest-backend-production.up.railway.app/api/assets";
let selectedAssets = new Set();

async function loadAssets() {
    try {
        const res = await fetch(`${API_URL}/assets`);
        if (!res.ok) throw new Error("Failed to load assets");
        const assets = await res.json();

        assetList.innerHTML = "";
        assets.forEach(asset => {
            const li = document.createElement("li");
            li.textContent = asset.ticker;

            li.addEventListener("click", () => {
                if (selectedAssets.has(asset.ticker)) {
                    selectedAssets.delete(asset.ticker);
                    li.classList.remove("selected");
                } else {
                    selectedAssets.add(asset.ticker);
                    li.classList.add("selected");
                }
            });

            assetList.appendChild(li);
        });
    } catch (err) {
        console.error("Error loading assets:", err);
    }
}

addAssetBtn.addEventListener("click", async () => {
    const ticker = assetInput.value.trim().toUpperCase();
    if (!ticker) return;

    try {
        const res = await fetch(`${API_URL}/assets`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ticker })
        });

        if (!res.ok) throw new Error("Failed to add asset");
        assetInput.value = "";
        loadAssets();
    } catch (err) {
        console.error("Error adding asset:", err);
    }
});

optimiseBtn.addEventListener("click", async () => {
    if (selectedAssets.size === 0) {
        alert("Please select at least one asset.");
        return;
    }

    const payload = {
        tickers: Array.from(selectedAssets),
        period: periodSelect.value
    };

    try {
        const res = await fetch(`${API_URL}/assets/optimise/chosen`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error("Optimisation failed");
        const data = await res.json();

        expectedReturnEl.textContent = data.expectedReturn ?? "-";
        volatilityEl.textContent = data.volatility ?? "-";
        sharpeRatioEl.textContent = data.sharpeRatio ?? "-";

        weightsList.innerHTML = "";
        if (data.weights) {
            Object.entries(data.weights).forEach(([ticker, weight]) => {
                const li = document.createElement("li");
                li.textContent = `${ticker}: ${weight}`;
                weightsList.appendChild(li);
            });
        }
    } catch (err) {
        console.error("Error during optimisation:", err);
    }
});


loadAssets();
