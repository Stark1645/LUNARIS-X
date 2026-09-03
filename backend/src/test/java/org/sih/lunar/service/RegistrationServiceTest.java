package org.sih.lunar.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.sih.lunar.dto.RegistrationRequestDTO;
import org.sih.lunar.dto.RegistrationResponseDTO;
import org.sih.lunar.entity.ImageEntity;
import org.sih.lunar.entity.RegistrationJobEntity;
import org.sih.lunar.exception.ResourceNotFoundException;
import org.sih.lunar.repository.ImageRepository;
import org.sih.lunar.repository.RegistrationJobRepository;

import java.io.File;
import java.io.IOException;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class RegistrationServiceTest {

    @Mock
    private ImageRepository imageRepository;

    @Mock
    private RegistrationJobRepository jobRepository;

    @Mock
    private org.sih.lunar.repository.MatchPointRepository matchPointRepository;

    @Mock
    private ImageStorageService storageService;

    @Mock
    private PythonMlClientService pythonMlClient;

    private ObjectMapper objectMapper;
    private RegistrationService registrationService;

    @BeforeEach
    void setUp() {
        this.objectMapper = new ObjectMapper();
        this.registrationService = new RegistrationService(
                imageRepository,
                jobRepository,
                matchPointRepository,
                storageService,
                pythonMlClient,
                objectMapper
        );
    }

    @Test
    void testCreateAndExecuteJobThrowsWhenSourceNotFound() {
        RegistrationRequestDTO req = new RegistrationRequestDTO();
        req.setSourceImageId(999L);
        req.setReferenceImageId(2L);

        when(imageRepository.findById(999L)).thenReturn(Optional.empty());

        assertThrows(ResourceNotFoundException.class, () ->
                registrationService.createAndExecuteJob(req)
        );
    }

    @Test
    void testCreateAndExecuteJobSuccessFlow() throws IOException {
        RegistrationRequestDTO req = new RegistrationRequestDTO();
        req.setSourceImageId(1L);
        req.setReferenceImageId(2L);
        req.setAlgorithm("Proposed_Method");

        ImageEntity src = new ImageEntity("src.png", "/path/src.png", "PNG", 100L, "h1", "SYNTHETIC_BENCHMARK");
        src.setId(1L);
        ImageEntity ref = new ImageEntity("ref.png", "/path/ref.png", "PNG", 100L, "h2", "SYNTHETIC_BENCHMARK");
        ref.setId(2L);

        File fSrc = File.createTempFile("src_", ".png");
        File fRef = File.createTempFile("ref_", ".png");

        when(imageRepository.findById(1L)).thenReturn(Optional.of(src));
        when(imageRepository.findById(2L)).thenReturn(Optional.of(ref));
        when(storageService.getImageFile(src)).thenReturn(fSrc);
        when(storageService.getImageFile(ref)).thenReturn(fRef);

        when(jobRepository.save(any(RegistrationJobEntity.class))).thenAnswer(i -> {
            RegistrationJobEntity j = i.getArgument(0);
            if (j.getId() == null) j.setId(10L);
            return j;
        });

        String mockResp = """
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
        JsonNode node = objectMapper.readTree(mockResp);
        when(pythonMlClient.registerImages(any(), any(), any(), any(), any(), any(), any(), any(), any(), any()))
                .thenReturn(node);

        RegistrationResponseDTO resp = registrationService.createAndExecuteJob(req);

        assertNotNull(resp);
        assertEquals(10L, resp.getJobId());
        assertEquals("SUCCESS", resp.getStatus());
        assertEquals(87, resp.getMetrics().getInlierMatchesCount());
        assertEquals(0.41, resp.getMetrics().getRmseGroundTruthPx(), 0.001);

        fSrc.delete();
        fRef.delete();
    }
}
