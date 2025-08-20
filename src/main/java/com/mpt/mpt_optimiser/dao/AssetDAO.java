package com.mpt.mpt_optimiser.dao;

import com.mpt.mpt_optimiser.model.Asset;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AssetDAO extends JpaRepository<Asset, Long> {
}
