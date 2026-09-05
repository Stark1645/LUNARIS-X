package org.sih.lunar.dto;

import java.time.LocalDateTime;
import java.util.List;

public class RegistrationResponseDTO {

    private Long jobId;
    private String status; // SUCCESS | DEGRADED | FAILED
    private String algorithm;
    private String selectedTransformationModel;
    private String transformationMatrixJson;
    private String failureReason;

    private Long sourceImageId;
    private Long referenceImageId;
    private String sourceFilename;
    private String referenceFilename;

    private MetricsDTO metrics;
    private List<MatchPointDTO> matchPoints;

    private String warpedImageBase64;
    private String referenceImageBase64;
    private String matchVisBase64;
    private String alphaOverlayBase64;
    private String checkerboardBase64;
    private String differenceMapBase64;
    private String panoramicMosaicBase64;

    private LocalDateTime createdAt;
    private LocalDateTime completedAt;

    public RegistrationResponseDTO() {}

    // Getters and Setters
    public Long getJobId() { return jobId; }
    public void setJobId(Long jobId) { this.jobId = jobId; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public String getAlgorithm() { return algorithm; }
    public void setAlgorithm(String algorithm) { this.algorithm = algorithm; }

    public String getSelectedTransformationModel() { return selectedTransformationModel; }
    public void setSelectedTransformationModel(String selectedTransformationModel) { this.selectedTransformationModel = selectedTransformationModel; }

    public String getTransformationMatrixJson() { return transformationMatrixJson; }
    public void setTransformationMatrixJson(String transformationMatrixJson) { this.transformationMatrixJson = transformationMatrixJson; }

    public String getFailureReason() { return failureReason; }
    public void setFailureReason(String failureReason) { this.failureReason = failureReason; }

    public Long getSourceImageId() { return sourceImageId; }
    public void setSourceImageId(Long sourceImageId) { this.sourceImageId = sourceImageId; }

    public Long getReferenceImageId() { return referenceImageId; }
    public void setReferenceImageId(Long referenceImageId) { this.referenceImageId = referenceImageId; }

    public String getSourceFilename() { return sourceFilename; }
    public void setSourceFilename(String sourceFilename) { this.sourceFilename = sourceFilename; }

    public String getReferenceFilename() { return referenceFilename; }
    public void setReferenceFilename(String referenceFilename) { this.referenceFilename = referenceFilename; }

    public MetricsDTO getMetrics() { return metrics; }
    public void setMetrics(MetricsDTO metrics) { this.metrics = metrics; }

    public List<MatchPointDTO> getMatchPoints() { return matchPoints; }
    public void setMatchPoints(List<MatchPointDTO> matchPoints) { this.matchPoints = matchPoints; }

    public String getWarpedImageBase64() { return warpedImageBase64; }
    public void setWarpedImageBase64(String warpedImageBase64) { this.warpedImageBase64 = warpedImageBase64; }

    public String getReferenceImageBase64() { return referenceImageBase64; }
    public void setReferenceImageBase64(String referenceImageBase64) { this.referenceImageBase64 = referenceImageBase64; }

    public String getMatchVisBase64() { return matchVisBase64; }
    public void setMatchVisBase64(String matchVisBase64) { this.matchVisBase64 = matchVisBase64; }

    public String getAlphaOverlayBase64() { return alphaOverlayBase64; }
    public void setAlphaOverlayBase64(String alphaOverlayBase64) { this.alphaOverlayBase64 = alphaOverlayBase64; }

    public String getCheckerboardBase64() { return checkerboardBase64; }
    public void setCheckerboardBase64(String checkerboardBase64) { this.checkerboardBase64 = checkerboardBase64; }

    public String getDifferenceMapBase64() { return differenceMapBase64; }
    public void setDifferenceMapBase64(String differenceMapBase64) { this.differenceMapBase64 = differenceMapBase64; }

    public String getPanoramicMosaicBase64() { return panoramicMosaicBase64; }
    public void setPanoramicMosaicBase64(String panoramicMosaicBase64) { this.panoramicMosaicBase64 = panoramicMosaicBase64; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }

    public LocalDateTime getCompletedAt() { return completedAt; }
    public void setCompletedAt(LocalDateTime completedAt) { this.completedAt = completedAt; }
}
