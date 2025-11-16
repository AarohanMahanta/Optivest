package com.mpt.mpt_optimiser.model;

import com.fasterxml.jackson.annotation.JsonInclude;
import jakarta.persistence.*;
import lombok.Data;


@Data
@Entity
public class Asset {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @JsonInclude(JsonInclude.Include.NON_NULL)
    private Long id;

    public Asset(Double expectedReturn, Long id, String ticker, Double volatility) {
        this.expectedReturn = expectedReturn;
        this.id = id;
        this.ticker = ticker;
        this.volatility = volatility;
    }

    public Asset() {

    }

    public Double getExpectedReturn() {
        return expectedReturn;
    }

    public void setExpectedReturn(Double expectedReturn) {
        this.expectedReturn = expectedReturn;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getTicker() {
        return ticker;
    }

    public void setTicker(String ticker) {
        this.ticker = ticker;
    }

    public Double getVolatility() {
        return volatility;
    }

    public void setVolatility(Double volatility) {
        this.volatility = volatility;
    }

    @Column(name = "ticker")
    private String ticker;
    @Column(name = "expected_return")
    private Double expectedReturn;  //mean return
    @Column(name = "volatility")
    private Double volatility;      //standard deviation
}

