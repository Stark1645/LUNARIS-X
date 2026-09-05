package org.sih.lunar.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.sih.lunar.dto.*;
import org.sih.lunar.entity.*;
import org.sih.lunar.exception.ResourceNotFoundException;
import org.sih.lunar.repository.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.io.File;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Service
public class RegistrationService {

    private static final org.slf4j.Logger log = org.slf4j.LoggerFactory.getLogger(RegistrationService.class);

    private final ImageRepository imageRepository;
    private final RegistrationJobRepository jobRepository;
    private final MatchPointRepository matchPointRepository;
    private final ImageStorageService storageService;
    private final PythonMlClientService pythonMlClient;
    private final ObjectMapper objectMapper;

    public RegistrationService(
            ImageRepository imageRepository,
            RegistrationJobRepository jobRepository,
            MatchPointRepository matchPointRepository,
            ImageStorageService storageService,
            PythonMlClientService pythonMlClient,
            ObjectMapper objectMapper) {
        this.imageRepository = imageRepository;
        this.jobRepository = jobRepository;
        this.matchPointRepository = matchPointRepository;
        this.storageService = storageService;
        this.pythonMlClient = pythonMlClient;
        this.objectMapper = objectMapper;
    }

    @Transactional(noRollbackFor = Exception.class)
    public RegistrationResponseDTO createAndExecuteJob(RegistrationRequestDTO request) {
        ImageEntity srcEntity = imageRepository.findById(request.getSourceImageId())
                .orElseThrow(() -> new ResourceNotFoundException("Source image not found with ID: " + request.getSourceImageId()));

        ImageEntity refEntity = imageRepository.findById(request.getReferenceImageId())
                .orElseThrow(() -> new ResourceNotFoundException("Reference image not found with ID: " + request.getReferenceImageId()));

        RegistrationJobEntity job = new RegistrationJobEntity(
                srcEntity,
                refEntity,
                request.getAlgorithm() != null ? request.getAlgorithm() : "Proposed_Method",
                request.getTransformationModel() != null ? request.getTransformationModel() : "HOMOGRAPHY"
        );
        job.setStatus("PROCESSING");
        job = jobRepository.save(job);

        File srcFile = storageService.getImageFile(srcEntity);
        File refFile = storageService.getImageFile(refEntity);

        try {
            JsonNode mlResp = pythonMlClient.registerImages(
                    srcFile,
                    refFile,
                    request.getAlgorithm(),
                    request.getTransformationModel(),
                    request.getRatioThreshold(),
                    request.getRansacThreshold(),
                    request.getEnableSubpixel(),
                    request.getEnableSpatialFilter(),
                    srcEntity.getGsdMeters(),
                    refEntity.getGsdMeters()
            );

            // Parse response
            String status = mlResp.has("status") ? mlResp.get("status").asText() : "SUCCESS";
            String selectedModel = mlResp.has("transformation_model") ? mlResp.get("transformation_model").asText() : "HOMOGRAPHY";
            String matrixJson = mlResp.has("transformation_matrix") ? mlResp.get("transformation_matrix").toString() : "[]";

            job.setStatus(status);
            job.setSelectedTransformationModel(selectedModel);
            job.setTransformationMatrixJson(matrixJson);
            job.setCompletedAt(LocalDateTime.now());

            // Metrics: check both "metrics" sub-node and root node
            JsonNode mNode = mlResp.has("metrics") ? mlResp.get("metrics") : mlResp;
            RegistrationMetricsEntity metrics = new RegistrationMetricsEntity();
            
            metrics.setCandidateMatchesCount(
                    mNode.has("candidate_matches_count") ? mNode.get("candidate_matches_count").asInt() :
                    (mNode.has("candidate_match_count") ? mNode.get("candidate_match_count").asInt() : 0)
            );
            metrics.setInlierMatchesCount(
                    mNode.has("inlier_matches_count") ? mNode.get("inlier_matches_count").asInt() :
                    (mNode.has("inlier_match_count") ? mNode.get("inlier_match_count").asInt() :
                    (mlResp.has("inlier_matches_count") ? mlResp.get("inlier_matches_count").asInt() : 0))
            );
            metrics.setInlierRatioPercent(mNode.has("inlier_ratio_percent") ? mNode.get("inlier_ratio_percent").asDouble() : 0.0);
            metrics.setRmseInliersPx(mNode.has("rmse_inliers") && !mNode.get("rmse_inliers").isNull() ? mNode.get("rmse_inliers").asDouble() : null);
            metrics.setRmseGroundTruthPx(mNode.has("rmse_ground_truth") && !mNode.get("rmse_ground_truth").isNull() ? mNode.get("rmse_ground_truth").asDouble() : null);
            metrics.setMeanSubpixelResidualPx(mNode.has("mean_subpixel_residual") && !mNode.get("mean_subpixel_residual").isNull() ? mNode.get("mean_subpixel_residual").asDouble() : null);
            metrics.setSubpixelAccuracyRate05px(mNode.has("subpixel_accuracy_rate_05px") && !mNode.get("subpixel_accuracy_rate_05px").isNull() ? mNode.get("subpixel_accuracy_rate_05px").asDouble() : null);
            metrics.setSpatialGiniCoefficient(mNode.has("spatial_gini_coefficient") && !mNode.get("spatial_gini_coefficient").isNull() ? mNode.get("spatial_gini_coefficient").asDouble() : null);
            metrics.setLatencyMs(mNode.has("latency_ms") && !mNode.get("latency_ms").isNull() ? mNode.get("latency_ms").asDouble() : null);
            metrics.setDataCategory(mNode.has("dataset_category") ? mNode.get("dataset_category").asText() : srcEntity.getDataCategory());

            job.setMetrics(metrics);

            // Save job
            job = jobRepository.save(job);

            // Persist match points if returned
            if (mlResp.has("match_points") && mlResp.get("match_points").isArray()) {
                List<MatchPointEntity> pointEntities = new ArrayList<>();
                for (JsonNode ptNode : mlResp.get("match_points")) {
                    double srcX = ptNode.has("source_x") ? ptNode.get("source_x").asDouble() : 0.0;
                    double srcY = ptNode.has("source_y") ? ptNode.get("source_y").asDouble() : 0.0;
                    double refX = ptNode.has("reference_x") ? ptNode.get("reference_x").asDouble() : 0.0;
                    double refY = ptNode.has("reference_y") ? ptNode.get("reference_y").asDouble() : 0.0;
                    boolean isInlier = ptNode.has("is_inlier") && ptNode.get("is_inlier").asBoolean();

                    pointEntities.add(new MatchPointEntity(job, srcX, srcY, refX, refY, isInlier));
                }
                matchPointRepository.saveAll(pointEntities);
            }

            // Construct DTO
            RegistrationResponseDTO dto = mapToResponseDTO(job);
            
            // Handle image visual products
            if (mlResp.has("warped_source_base64")) {
                dto.setWarpedImageBase64(mlResp.get("warped_source_base64").asText());
            } else if (mlResp.has("warped_image_base64")) {
                dto.setWarpedImageBase64(mlResp.get("warped_image_base64").asText());
            }

            if (mlResp.has("reference_image_base64")) dto.setReferenceImageBase64(mlResp.get("reference_image_base64").asText());
            if (mlResp.has("match_vis_base64")) dto.setMatchVisBase64(mlResp.get("match_vis_base64").asText());
            if (mlResp.has("alpha_overlay_base64")) dto.setAlphaOverlayBase64(mlResp.get("alpha_overlay_base64").asText());
            if (mlResp.has("checkerboard_base64")) dto.setCheckerboardBase64(mlResp.get("checkerboard_base64").asText());
            if (mlResp.has("difference_map_base64")) dto.setDifferenceMapBase64(mlResp.get("difference_map_base64").asText());
            if (mlResp.has("panoramic_mosaic_base64")) dto.setPanoramicMosaicBase64(mlResp.get("panoramic_mosaic_base64").asText());

            return dto;

        } catch (Exception e) {
            log.error("Registration execution failed for job ID: {}", job.getId(), e);
            job.setStatus("FAILED");
            job.setFailureReason(e.getMessage());
            job.setCompletedAt(LocalDateTime.now());
            job = jobRepository.save(job);

            RegistrationResponseDTO failedDto = mapToResponseDTO(job);
            failedDto.setStatus("FAILED");
            failedDto.setFailureReason(e.getMessage());
            return failedDto;
        }
    }

    @Transactional(readOnly = true)
    public RegistrationResponseDTO getJobById(Long jobId) {
        RegistrationJobEntity job = jobRepository.findById(jobId)
                .orElseThrow(() -> new ResourceNotFoundException("Registration job not found with ID: " + jobId));
        return mapToResponseDTO(job);
    }

    @Transactional(readOnly = true)
    public List<JobStatusDTO> getAllJobs() {
        return jobRepository.findAllByOrderByCreatedAtDesc().stream()
                .map(j -> new JobStatusDTO(
                        j.getId(),
                        j.getStatus(),
                        j.getAlgorithm(),
                        j.getFailureReason(),
                        j.getCreatedAt(),
                        j.getCompletedAt()
                )).toList();
    }

    private RegistrationResponseDTO mapToResponseDTO(RegistrationJobEntity job) {
        RegistrationResponseDTO dto = new RegistrationResponseDTO();
        dto.setJobId(job.getId());
        dto.setStatus(job.getStatus());
        dto.setAlgorithm(job.getAlgorithm());
        dto.setSelectedTransformationModel(job.getSelectedTransformationModel());
        dto.setTransformationMatrixJson(job.getTransformationMatrixJson());
        dto.setFailureReason(job.getFailureReason());

        if (job.getSourceImage() != null) {
            dto.setSourceImageId(job.getSourceImage().getId());
            dto.setSourceFilename(job.getSourceImage().getFilename());
        }
        if (job.getReferenceImage() != null) {
            dto.setReferenceImageId(job.getReferenceImage().getId());
            dto.setReferenceFilename(job.getReferenceImage().getFilename());
        }

        if (job.getMetrics() != null) {
            RegistrationMetricsEntity m = job.getMetrics();
            MetricsDTO mDto = new MetricsDTO();
            mDto.setCandidateMatchesCount(m.getCandidateMatchesCount());
            mDto.setInlierMatchesCount(m.getInlierMatchesCount());
            mDto.setInlierRatioPercent(m.getInlierRatioPercent());
            mDto.setRmseInliersPx(m.getRmseInliersPx());
            mDto.setRmseGroundTruthPx(m.getRmseGroundTruthPx());
            mDto.setMeanSubpixelResidualPx(m.getMeanSubpixelResidualPx());
            mDto.setSubpixelAccuracyRate05px(m.getSubpixelAccuracyRate05px());
            mDto.setSpatialGiniCoefficient(m.getSpatialGiniCoefficient());
            mDto.setLatencyMs(m.getLatencyMs());
            mDto.setDataCategory(m.getDataCategory());
            dto.setMetrics(mDto);
        }

        dto.setCreatedAt(job.getCreatedAt());
        dto.setCompletedAt(job.getCompletedAt());
        return dto;
    }
}
