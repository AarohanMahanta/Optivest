package com.mpt.mpt_optimiser.service;

import com.mpt.mpt_optimiser.dao.AssetDAO;
import com.mpt.mpt_optimiser.dto.PortfolioResult;
import com.mpt.mpt_optimiser.model.Asset;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class PortfolioService {

    private final RestTemplate restTemplate = new RestTemplate();
    private final AssetDAO assetDAO;
    private static final String pythonUrl = "https://optivest-python-service-production.up.railway.app/optimise";

    @Autowired
    public PortfolioService(AssetDAO assetDAO) {
        this.assetDAO = assetDAO;
    }

    public PortfolioResult optimise() {
        List<Asset> assets = assetDAO.findAll();
        return getPortfolioResult(assets, "1y");
    }

    public PortfolioResult optimiseWithChosenAssets(List<String> tickers, String period) {
        List<Asset> assets = assetDAO.findByTickerIn(tickers);

        if (assets.isEmpty()) {
            throw new IllegalArgumentException("No matching assets found in DB for tickers: " + tickers);
        }

        return getPortfolioResult(assets, period);
    }


    private PortfolioResult getPortfolioResult(List<Asset> assets, String period) {
        List<String> tickers = assets.stream()
                .map(Asset::getTicker)
                .toList();
        Map<String, Object> request = new HashMap<>();
        request.put("tickers", tickers);
        request.put("period", period);


        return restTemplate.postForObject(pythonUrl, request, PortfolioResult.class);
    }

    //Health Check
    private boolean isPythonAlive() {
        try {
            restTemplate.getForObject("http://optivest-python:5000/health", String.class);
            return true;
        } catch (Exception e) {
            return false;
        }
    }

}
