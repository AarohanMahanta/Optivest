package com.mpt.mpt_optimiser.dto;

import java.util.List;
import java.util.Map;

//DTO to match Python response
public class PortfolioResult {
    private Map<String, Double> weights;
    private Double expectedReturn;
    private Double volatility;
    private Double sharpeRatio;

    public Double getExpectedReturn() {
        return expectedReturn;
    }

    public void setExpectedReturn(Double expectedReturn) {
        this.expectedReturn = expectedReturn;
    }

    public Double getSharpeRatio() {
        return sharpeRatio;
    }

    public void setSharpeRatio(Double sharpeRatio) {
        this.sharpeRatio = sharpeRatio;
    }

    public Double getVolatility() {
        return volatility;
    }

    public void setVolatility(Double volatility) {
        this.volatility = volatility;
    }

    public Map<String, Double> getWeights() {
        return weights;
    }

    public void setWeights(Map<String, Double> weights) {
        this.weights = weights;
    }

    @Override
    public String toString() {
        return "PortfolioResult{" +
                "expectedReturn=" + expectedReturn +
                ", weights=" + weights +
                ", volatility=" + volatility +
                ", sharpeRatio=" + sharpeRatio +
                '}';
    }
}
