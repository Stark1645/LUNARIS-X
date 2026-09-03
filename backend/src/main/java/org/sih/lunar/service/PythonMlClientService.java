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
                throw new PythonServiceUnavailableException("Python ML service returned error HTTP status: " + response.getStatusCode());
            }
            return objectMapper.readTree(response.getBody());
        } catch (RestClientException e) {
            throw new PythonServiceUnavailableException("Failed to communicate with Python ML Service at: " + registerUrl + ". Cause: " + e.getMessage(), e);
        } catch (Exception e) {
            throw new RuntimeException("Failed to parse Python ML response", e);
        }
    }
}
