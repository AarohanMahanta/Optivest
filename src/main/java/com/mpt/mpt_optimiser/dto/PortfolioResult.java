package com.mpt.mpt_optimiser.dto;

import java.util.Map;

//DTO to match Python response
public class PortfolioResult {
    private Map<String, Double> weights;
    private Double expectedReturn;
    private Double volatility;
    private Double sharpeRatio;
}
