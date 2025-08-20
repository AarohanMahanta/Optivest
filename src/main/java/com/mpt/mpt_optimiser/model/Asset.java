package com.mpt.mpt_optimiser.model;

import jakarta.persistence.*;
import lombok.Data;

@Data
@Entity
public class Asset {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String ticker;
    private Double expectedReturn;  //mean return
    private Double volatility;      //standard deviation
}

