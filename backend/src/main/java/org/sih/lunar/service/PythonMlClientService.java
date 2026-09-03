package org.sih.lunar.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.sih.lunar.exception.PythonServiceUnavailableException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.FileSystemResource;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import java.io.File;

@Service
public class PythonMlClientService {

    private static final org.slf4j.Logger log = org.slf4j.LoggerFactory.getLogger(PythonMlClientService.class);

    private final RestTemplate restTemplate;
    private final String pythonBaseUrl;
    private final ObjectMapper objectMapper;

    public PythonMlClientService(
            RestTemplate restTemplate,
            @Value("${python.ml.service.url:http://localhost:8000}") String pythonBaseUrl,
            ObjectMapper objectMapper) {
        this.restTemplate = restTemplate;
        this.pythonBaseUrl = pythonBaseUrl.endsWith("/") ? pythonBaseUrl.substring(0, pythonBaseUrl.length() - 1) : pythonBaseUrl;
        this.objectMapper = objectMapper;
    }

    public boolean checkHealth() {
        try {
            String healthUrl = this.pythonBaseUrl + "/api/v1/health";
            ResponseEntity<String> response = restTemplate.getForEntity(healthUrl, String.class);
            return response.getStatusCode().is2xxSuccessful();
        } catch (Exception e) {
            return false;
        }
    }

    public JsonNode registerImages(
            File sourceFile,
            File referenceFile,
            String algorithm,
            String transformationModel,
            Double ratioThreshold,
            Double ransacThreshold,
            Boolean enableSubpixel,
            Boolean enableSpatialFilter,
            Double gsdSourceM,
            Double gsdReferenceM) {

        String registerUrl = this.pythonBaseUrl + "/api/v1/register";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("source_file", new FileSystemResource(sourceFile));
        body.add("reference_file", new FileSystemResource(referenceFile));
        body.add("algorithm", algorithm != null ? algorithm : "Proposed_Method");
        body.add("transformation_model", transformationModel != null ? transformationModel : "HOMOGRAPHY");
        body.add("ratio_threshold", ratioThreshold != null ? ratioThreshold.toString() : "0.80");
        body.add("ransac_threshold", ransacThreshold != null ? ransacThreshold.toString() : "3.0");
        body.add("enable_subpixel", enableSubpixel != null ? enableSubpixel.toString() : "true");
        body.add("enable_spatial_filter", enableSpatialFilter != null ? enableSpatialFilter.toString() : "true");

        if (gsdSourceM != null) {
            body.add("gsd_source_m", gsdSourceM.toString());
        }
        if (gsdReferenceM != null) {
            body.add("gsd_reference_m", gsdReferenceM.toString());
        }

        HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);

        try {
            ResponseEntity<String> response = restTemplate.postForEntity(registerUrl, requestEntity, String.class);
            if (!response.getStatusCode().is2xxSuccessful() || response.getBody() == null) {
                throw new PythonServiceUnavailableException("Python ML service returned error HTTP status: " + response.getStatusCode() + " body: " + response.getBody());
            }
            return objectMapper.readTree(response.getBody());
        } catch (PythonServiceUnavailableException e) {
            throw e;
        } catch (org.springframework.web.client.HttpStatusCodeException e) {
            log.error("Python ML service returned HTTP error: {} body: {}", e.getStatusCode(), e.getResponseBodyAsString(), e);
            throw new PythonServiceUnavailableException("Python ML service error (" + e.getStatusCode() + "): " + e.getResponseBodyAsString(), e);
        } catch (RestClientException e) {
            log.error("Failed to communicate with Python ML Service at: {}", registerUrl, e);
            throw new PythonServiceUnavailableException("Failed to communicate with Python ML Service at: " + registerUrl + ". Cause: " + e.getMessage(), e);
        } catch (Exception e) {
            log.error("Failed to parse Python ML response", e);
            throw new RuntimeException("Failed to parse Python ML response: " + e.getMessage(), e);
        }
    }

    public JsonNode scanPradanCatalog(String directoryPath, String dataCategory, Boolean isSynthetic) {
        String url = this.pythonBaseUrl + "/api/v1/catalog/scan";
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_FORM_URLENCODED);

        MultiValueMap<String, String> body = new LinkedMultiValueMap<>();
        body.add("directory_path", directoryPath != null ? directoryPath : "data/pradan");
        body.add("data_category", dataCategory != null ? dataCategory : "AUTHENTIC_CH2_PRADAN");
        body.add("is_synthetic", isSynthetic != null ? isSynthetic.toString() : "false");

        HttpEntity<MultiValueMap<String, String>> requestEntity = new HttpEntity<>(body, headers);
        try {
            ResponseEntity<String> response = restTemplate.postForEntity(url, requestEntity, String.class);
            return objectMapper.readTree(response.getBody());
        } catch (Exception e) {
            throw new PythonServiceUnavailableException("Failed to scan PRADAN catalog: " + e.getMessage(), e);
        }
    }

    public JsonNode getPradanProducts(String instrument) {
        String url = this.pythonBaseUrl + "/api/v1/catalog/products" + (instrument != null ? "?instrument=" + instrument : "");
        try {
            ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
            return objectMapper.readTree(response.getBody());
        } catch (Exception e) {
            throw new PythonServiceUnavailableException("Failed to query PRADAN products: " + e.getMessage(), e);
        }
    }

    public JsonNode checkOverlap(String referenceId, String movingId, Boolean isBenchmark) {
        String url = this.pythonBaseUrl + "/api/v1/overlap/check";
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_FORM_URLENCODED);

        MultiValueMap<String, String> body = new LinkedMultiValueMap<>();
        body.add("reference_id", referenceId);
        body.add("moving_id", movingId);
        body.add("is_benchmark", isBenchmark != null ? isBenchmark.toString() : "false");

        HttpEntity<MultiValueMap<String, String>> requestEntity = new HttpEntity<>(body, headers);
        try {
            ResponseEntity<String> response = restTemplate.postForEntity(url, requestEntity, String.class);
            return objectMapper.readTree(response.getBody());
        } catch (Exception e) {
            throw new PythonServiceUnavailableException("Failed to check overlap: " + e.getMessage(), e);
        }
    }

    public JsonNode selectReferenceMoving(String productAId, String productBId, String userChoice, String objective) {
        String url = this.pythonBaseUrl + "/api/v1/reference/select";
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_FORM_URLENCODED);

        MultiValueMap<String, String> body = new LinkedMultiValueMap<>();
        body.add("product_a_id", productAId);
        body.add("product_b_id", productBId);
        if (userChoice != null) body.add("user_choice", userChoice);
        if (objective != null) body.add("registration_objective", objective);

        HttpEntity<MultiValueMap<String, String>> requestEntity = new HttpEntity<>(body, headers);
        try {
            ResponseEntity<String> response = restTemplate.postForEntity(url, requestEntity, String.class);
            return objectMapper.readTree(response.getBody());
        } catch (Exception e) {
            throw new PythonServiceUnavailableException("Failed to select reference/moving: " + e.getMessage(), e);
        }
    }
}
