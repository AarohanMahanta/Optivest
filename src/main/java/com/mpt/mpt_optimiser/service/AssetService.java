package com.mpt.mpt_optimiser.service;

import com.mpt.mpt_optimiser.dao.AssetDAO;
import com.mpt.mpt_optimiser.model.Asset;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class AssetService {

    private final AssetDAO assetDAO;

    @Autowired
    public AssetService(AssetDAO assetDAO) {
        this.assetDAO = assetDAO;
    }

    public Asset getAsset(Long id) {
        return assetDAO.findById(id).orElse(new Asset());
    }

    public List<Asset> getAllAssets() {
        return assetDAO.findAll();
    }

    public Asset addAsset(Asset asset) {
        return assetDAO .save(asset);
    }
}