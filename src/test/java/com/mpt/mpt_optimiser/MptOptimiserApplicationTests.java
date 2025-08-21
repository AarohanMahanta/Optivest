package com.mpt.mpt_optimiser;
import static org.hamcrest.Matchers.containsInAnyOrder;

import com.mpt.mpt_optimiser.controller.AssetController;
import com.mpt.mpt_optimiser.dao.AssetDAO;
import com.mpt.mpt_optimiser.model.Asset;
import com.mpt.mpt_optimiser.service.AssetService;
import com.mpt.mpt_optimiser.service.PortfolioService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.easymock.EasyMock;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import static org.hamcrest.Matchers.containsInAnyOrder;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;

import java.util.Arrays;
import java.util.List;

import static org.easymock.EasyMock.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
class MptOptimiserApplicationTests {

    private AssetService assetService;
    private PortfolioService portfolioService;
    private AssetController assetController;
    private MockMvc mockMvc;

    @BeforeEach
	void setUp() {
		assetService = createMock(AssetService.class);
        portfolioService = createMock(PortfolioService.class);
        assetController = new AssetController(assetService, portfolioService);
        mockMvc = MockMvcBuilders.standaloneSetup(assetController).build();
    }

    @Test
    void testGetAllAssets() throws Exception {
        Asset asset1 = new Asset(0.1, 1L, "AAPL", 0.2);
        Asset asset2 = new Asset(0.15, 2L, "PLTR", 0.25);

        expect(assetService.getAllAssets()).andReturn(Arrays.asList(asset1, asset2));
        replay(assetService);

        mockMvc.perform(get("/api/assets"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[*].ticker").value(containsInAnyOrder("AAPL", "PLTR")));
        verify(assetService);
    }


}
