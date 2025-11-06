package com.mpt.mpt_optimiser;
import static org.hamcrest.Matchers.containsInAnyOrder;
import com.mpt.mpt_optimiser.controller.AssetController;
import com.mpt.mpt_optimiser.dao.AssetDAO;
import com.mpt.mpt_optimiser.dto.PortfolioResult;
import com.mpt.mpt_optimiser.model.Asset;
import com.mpt.mpt_optimiser.service.AssetService;
import com.mpt.mpt_optimiser.service.PortfolioService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.easymock.EasyMock;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import static org.hamcrest.Matchers.containsInAnyOrder;
import java.util.Arrays;
import java.util.List;
import static org.easymock.EasyMock.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
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

    @Test
    void testAddAsset() throws Exception {
        Asset asset = new Asset(0.1, 1L, "AAPL", 0.2);

        expect(assetService.addAsset(isA(Asset.class))).andReturn(asset);
        replay(assetService);

        mockMvc.perform(post("/api/assets")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"ticker\":\"AAPL\",\"expectedReturn\":0.1,\"volatility\":0.2}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.ticker").value("AAPL"))
                .andExpect(jsonPath("$.expectedReturn").value(0.1));

        verify(assetService);
    }

    @Test
    void testDeleteAsset() throws Exception {
        assetService.deleteAsset(1L);
        expectLastCall(); //Expect last recorded void method call
        replay(assetService);

        mockMvc.perform(delete("/api/assets/1"))
                        .andExpect(status().isOk());

        verify(assetService);
    }

    @Test
    void testDeleteAllAssets() throws Exception {
        assetService.deleteAllAssets();
        expectLastCall(); //Expect last recorded void method call
        replay(assetService);

        mockMvc.perform(delete("/api/assets"))
                .andExpect(status().isOk());

        verify(assetService);
    }

    @Test
    void testOptimise() throws Exception {
        PortfolioResult result = new PortfolioResult();
        result.setExpectedReturn(0.2);
        result.setVolatility(0.3);
        result.setSharpeRatio(1.5);

        expect(portfolioService.optimise()).andReturn(result);
        replay(portfolioService);

        mockMvc.perform(get("/api/assets/optimise"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.expectedReturn").value(0.2))
                .andExpect(jsonPath("$.volatility").value(0.3))
                .andExpect(jsonPath("$.sharpeRatio").value(1.5));
        verify(portfolioService);
    }

}
