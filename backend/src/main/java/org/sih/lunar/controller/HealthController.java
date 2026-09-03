package org.sih.lunar.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.sih.lunar.dto.HealthStatusDTO;
import org.sih.lunar.service.PythonMlClientService;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.sql.DataSource;
import java.sql.Connection;
import java.util.List;

@RestController
@RequestMapping("/api/v1/health")
@Tag(name = "Health", description = "System health check and microservice status endpoints")
public class HealthController {

    private final PythonMlClientService pythonMlClient;
    private final DataSource dataSource;

    @Value("${python.ml.service.url:http://localhost:8000}")
    private String pythonServiceUrl;

    public HealthController(PythonMlClientService pythonMlClient, DataSource dataSource) {
        this.pythonMlClient = pythonMlClient;
        this.dataSource = dataSource;
    }

    @GetMapping
    @Operation(summary = "System health check", description = "Checks database connectivity and Python ML microservice operational status.")
    public ResponseEntity<HealthStatusDTO> getHealth() {
        HealthStatusDTO dto = new HealthStatusDTO();
        dto.setBackendVersion("1.0.0");
        dto.setPythonServiceUrl(this.pythonServiceUrl);
        dto.setSupportedAlgorithms(List.of("Proposed_Method", "SIFT_Baseline", "RIFT_Baseline"));

        // Check DB
        boolean dbOk = false;
        try (Connection conn = dataSource.getConnection()) {
            dbOk = conn.isValid(2);
        } catch (Exception ignored) {}
        dto.setDatabaseStatus(dbOk ? "UP" : "DOWN");

        // Check Python
        boolean pyOk = pythonMlClient.checkHealth();
        dto.setPythonServiceStatus(pyOk ? "UP" : "DOWN");

        dto.setStatus((dbOk && pyOk) ? "UP" : (dbOk ? "DEGRADED (Python ML Down)" : "DOWN"));

        return ResponseEntity.ok(dto);
    }
}
