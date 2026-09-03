package org.sih.lunar.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.sih.lunar.dto.JobStatusDTO;
import org.sih.lunar.dto.RegistrationRequestDTO;
import org.sih.lunar.dto.RegistrationResponseDTO;
import org.sih.lunar.service.RegistrationService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/jobs")
@Tag(name = "Registration Jobs", description = "Endpoints for orchestrating, executing, and retrieving lunar image registration jobs")
public class RegistrationJobController {

    private final RegistrationService registrationService;

    public RegistrationJobController(RegistrationService registrationService) {
        this.registrationService = registrationService;
    }

    @PostMapping("/register")
    @Operation(summary = "Submit and execute registration job", description = "Executes multi-scale registration between source and reference images using SIFT, RIFT, or Proposed AMSR.")
    public ResponseEntity<RegistrationResponseDTO> submitRegistration(
            @Valid @RequestBody RegistrationRequestDTO request) {
        RegistrationResponseDTO response = registrationService.createAndExecuteJob(request);
        return new ResponseEntity<>(response, HttpStatus.OK);
    }

    @GetMapping
    @Operation(summary = "List all registration jobs", description = "Returns a summary list of all executed registration jobs.")
    public ResponseEntity<List<JobStatusDTO>> listAllJobs() {
        return ResponseEntity.ok(registrationService.getAllJobs());
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get registration job by ID", description = "Retrieves complete metrics, transformation matrix, and visual overlay products for a specific job.")
    public ResponseEntity<RegistrationResponseDTO> getJobById(@PathVariable("id") Long id) {
        return ResponseEntity.ok(registrationService.getJobById(id));
    }
}
