package com.mpt.mpt_optimiser.controller;

import com.mpt.mpt_optimiser.dto.PortfolioResult;
import com.mpt.mpt_optimiser.model.Asset;
import com.mpt.mpt_optimiser.service.AssetService;
import com.mpt.mpt_optimiser.service.PortfolioService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.ListResourceBundle;
import java.util.Map;

@CrossOrigin(origins = {
        "http://localhost:3000",
        "http://127.0.0.1:5501",
        "https://optivest-static.onrender.com"
})@RestController
@RequestMapping("/api/assets")
public class AssetController {

    private final AssetService assetService;
    private final PortfolioService portfolioService;

    @Autowired
    public AssetController(AssetService assetService, PortfolioService portfolioService) {
        this.assetService = assetService;
        this.portfolioService = portfolioService;
    }

    @GetMapping("/{id}")
    public Asset getAsset(@PathVariable Long id) {
        return assetService.getAsset(id);
    }

    @GetMapping
    public List<Asset> getAllAssets() {
        return assetService.getAllAssets();
    }

    @PostMapping
    public Asset addAsset(@RequestBody Asset asset) {
        return assetService.addAsset(asset);
    }

    @DeleteMapping("/{id}")
    public void deleteAsset(@PathVariable Long id) {
        assetService.deleteAsset(id);
    }

    @DeleteMapping
    public void deleteAllAssets() {
        assetService.deleteAllAssets();
    }

    @PutMapping("/{id}")
    public Asset updateAsset(@PathVariable Long id, @RequestBody Asset newAsset) {
        return assetService.updateAsset(id, newAsset);
    }

    @GetMapping("/optimise")
    public PortfolioResult optimise() {
        return portfolioService.optimise();
    }

    @PostMapping("/optimise/chosen")
    public PortfolioResult optimiseWithChosenAssets(@RequestBody Map<String, Object> request) {
        List<String> tickers = (List<String>) request.get("tickers");
        String period = (String) request.getOrDefault("period", "1y");
        return portfolioService.optimiseWithChosenAssets(tickers, period);
    }

}
