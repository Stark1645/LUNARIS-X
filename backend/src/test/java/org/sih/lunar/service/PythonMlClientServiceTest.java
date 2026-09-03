package org.sih.lunar.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.sih.lunar.exception.PythonServiceUnavailableException;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.web.client.RestTemplate;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;

import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.method;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withStatus;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;

class PythonMlClientServiceTest {

    private RestTemplate restTemplate;
    private MockRestServiceServer mockServer;
    private PythonMlClientService clientService;
    private final ObjectMapper objectMapper = new ObjectMapper();

    @BeforeEach
    void setUp() {
        this.restTemplate = new RestTemplate();
        this.mockServer = MockRestServiceServer.createServer(restTemplate);
        this.clientService = new PythonMlClientService(
                this.restTemplate,
                "http://localhost:8000",
                objectMapper
        );
    }

    @Test
    void testCheckHealthReturnsTrueWhenPythonIsHealthy() {
        mockServer.expect(requestTo("http://localhost:8000/api/v1/health"))
                .andExpect(method(HttpMethod.GET))
                .andRespond(withSuccess("{\"status\":\"UP\"}", MediaType.APPLICATION_JSON));

        boolean isHealthy = clientService.checkHealth();
        assertTrue(isHealthy);
        mockServer.verify();
    }

    @Test
    void testCheckHealthReturnsFalseWhenPythonIsDown() {
        mockServer.expect(requestTo("http://localhost:8000/api/v1/health"))
                .andExpect(method(HttpMethod.GET))
                .andRespond(withStatus(HttpStatus.SERVICE_UNAVAILABLE));

        boolean isHealthy = clientService.checkHealth();
        assertFalse(isHealthy);
        mockServer.verify();
    }

    @Test
    void testRegisterImagesParsesSuccessfulResponse() throws IOException {
        File dummySrc = File.createTempFile("src_", ".png");
        File dummyRef = File.createTempFile("ref_", ".png");
        Files.write(dummySrc.toPath(), new byte[]{1, 2, 3});
        Files.write(dummyRef.toPath(), new byte[]{4, 5, 6});

        String mockResponseBody = """
                {
                    "status": "SUCCESS",
                    "algorithm": "Proposed_Method",
                    "transformation_model": "HOMOGRAPHY",
                    "candidate_matches_count": 95,
                    "inlier_matches_count": 87,
                    "metrics": {
                        "inlier_match_count": 87,
                        "inlier_ratio_percent": 91.58,
                        "rmse_inliers": 1.27,
                        "rmse_ground_truth": 0.41,
                        "mean_subpixel_residual": 0.22,
                        "spatial_gini_coefficient": 0.32,
                        "latency_ms": 390.0,
                        "dataset_category": "SYNTHETIC_BENCHMARK"
                    }
                }
                """;

        mockServer.expect(requestTo("http://localhost:8000/api/v1/register"))
                .andExpect(method(HttpMethod.POST))
                .andRespond(withSuccess(mockResponseBody, MediaType.APPLICATION_JSON));

        JsonNode result = clientService.registerImages(
                dummySrc, dummyRef, "Proposed_Method", "HOMOGRAPHY",
                0.80, 3.0, true, true, 5.0, 5.0
        );

        assertNotNull(result);
        assertEquals("SUCCESS", result.get("status").asText());
        assertEquals(87, result.get("inlier_matches_count").asInt());
        assertEquals(0.41, result.get("metrics").get("rmse_ground_truth").asDouble(), 0.001);

        mockServer.verify();
        dummySrc.delete();
        dummyRef.delete();
    }

    @Test
    void testRegisterImagesThrowsWhenPythonFails() throws IOException {
        File dummySrc = File.createTempFile("src_", ".png");
        File dummyRef = File.createTempFile("ref_", ".png");

        mockServer.expect(requestTo("http://localhost:8000/api/v1/register"))
                .andExpect(method(HttpMethod.POST))
                .andRespond(withStatus(HttpStatus.INTERNAL_SERVER_ERROR));

        assertThrows(PythonServiceUnavailableException.class, () ->
                clientService.registerImages(dummySrc, dummyRef, "Proposed_Method", "HOMOGRAPHY",
                        0.80, 3.0, true, true, null, null)
        );

        dummySrc.delete();
        dummyRef.delete();
    }
}
