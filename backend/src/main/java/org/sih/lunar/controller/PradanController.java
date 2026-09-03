package org.sih.lunar.controller;

import com.fasterxml.jackson.databind.JsonNode;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.sih.lunar.service.PythonMlClientService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/pradan")
@Tag(name = "PRADAN Products & Overlap", description = "Endpoints for indexing PRADAN Chandrayaan-2 products, checking geographic overlap, and autonomous reference selection.")
public class PradanController {

    private final PythonMlClientService pythonMlClient;

    public PradanController(PythonMlClientService pythonMlClient) {
        this.pythonMlClient = pythonMlClient;
    }

    @PostMapping("/scan")
    @Operation(summary = "Scan directory for PRADAN PDS4 products", description = "Scans a given filesystem path for PDS4 XML and PDS3 LBL products and registers them into the catalog.")
    public ResponseEntity<JsonNode> scanDirectory(
            @RequestParam(value = "directoryPath", defaultValue = "data/pradan") String directoryPath,
            @RequestParam(value = "dataCategory", defaultValue = "AUTHENTIC_CH2_PRADAN") String dataCategory,
            @RequestParam(value = "isSynthetic", defaultValue = "false") Boolean isSynthetic) {
        JsonNode result = pythonMlClient.scanPradanCatalog(directoryPath, dataCategory, isSynthetic);
        return ResponseEntity.ok(result);
    }

    @GetMapping("/products")
    @Operation(summary = "List cataloged PRADAN products", description = "Returns registered products, optionally filtered by instrument (OHRC, TMC2, IIRS).")
    public ResponseEntity<JsonNode> getProducts(@RequestParam(value = "instrument", required = false) String instrument) {
        JsonNode result = pythonMlClient.getPradanProducts(instrument);
        return ResponseEntity.ok(result);
    }

    @PostMapping("/overlap")
    @Operation(summary = "Check autonomous geographic overlap", description = "Computes spherical 2D footprint intersection and overlap percentage between reference and moving products.")
    public ResponseEntity<JsonNode> checkOverlap(
            @RequestParam("referenceId") String referenceId,
            @RequestParam("movingId") String movingId,
            @RequestParam(value = "isBenchmark", defaultValue = "false") Boolean isBenchmark) {
        JsonNode result = pythonMlClient.checkOverlap(referenceId, movingId, isBenchmark);
        return ResponseEntity.ok(result);
    }

    @PostMapping("/reference-select")
    @Operation(summary = "Select Reference vs Moving role", description = "Evaluates mission designation, user choice, objective, and multi-factor heuristic to assign reference and moving roles.")
    public ResponseEntity<JsonNode> selectReference(
            @RequestParam("productAId") String productAId,
            @RequestParam("productBId") String productBId,
            @RequestParam(value = "userChoice", required = false) String userChoice,
            @RequestParam(value = "objective", required = false) String objective) {
        JsonNode result = pythonMlClient.selectReferenceMoving(productAId, productBId, userChoice, objective);
        return ResponseEntity.ok(result);
    }
}
