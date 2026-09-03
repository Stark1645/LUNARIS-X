package org.sih.lunar.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.sih.lunar.dto.ExperimentDTO;
import org.sih.lunar.service.ExperimentService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/experiments")
@Tag(name = "Experiments", description = "Endpoints for inspecting benchmark suites, baseline evaluations, and ablation studies")
public class ExperimentController {

    private final ExperimentService experimentService;

    public ExperimentController(ExperimentService experimentService) {
        this.experimentService = experimentService;
    }

    @GetMapping
    @Operation(summary = "List all experiment records", description = "Retrieves stored baseline and ablation experiment evaluation logs.")
    public ResponseEntity<List<ExperimentDTO>> listAllExperiments() {
        return ResponseEntity.ok(experimentService.getAllExperiments());
    }

    @GetMapping("/suite/{suiteName}")
    @Operation(summary = "List experiments by benchmark suite", description = "Filters experiment records by suite name (e.g. suite_b_sun_angle, suite_c_scale_disparity).")
    public ResponseEntity<List<ExperimentDTO>> getExperimentsBySuite(@PathVariable("suiteName") String suiteName) {
        return ResponseEntity.ok(experimentService.getExperimentsBySuite(suiteName));
    }
}
