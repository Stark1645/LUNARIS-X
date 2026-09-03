package org.sih.lunar.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "registration_jobs")
public class RegistrationJobEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "source_image_id", nullable = false)
    private ImageEntity sourceImage;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "reference_image_id", nullable = false)
    private ImageEntity referenceImage;

    @Column(nullable = false)
    private String algorithm; // Proposed_Method | SIFT_Baseline | RIFT_Baseline

    @Column(nullable = false)
    private String requestedTransformationModel; // HOMOGRAPHY | AFFINE | SIMILARITY | TRANSLATION

    private String selectedTransformationModel;

    @Column(columnDefinition = "TEXT")
    private String transformationMatrixJson;

    @Column(nullable = false)
    private String status; // PENDING | PROCESSING | SUCCESS | DEGRADED | FAILED

    private String failureReason;

    private String warpedImageStoragePath;
    private String matchVisStoragePath;
    private String alphaOverlayStoragePath;
    private String checkerboardStoragePath;
    private String differenceMapStoragePath;

    @OneToOne(cascade = CascadeType.ALL, fetch = FetchType.EAGER)
    @JoinColumn(name = "metrics_id")
    private RegistrationMetricsEntity metrics;

    @OneToMany(mappedBy = "job", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    private List<MatchPointEntity> matchPoints = new ArrayList<>();

    @Column(nullable = false)
    private LocalDateTime createdAt;

    private LocalDateTime completedAt;

    public RegistrationJobEntity() {
        this.status = "PENDING";
        this.createdAt = LocalDateTime.now();
    }

    public RegistrationJobEntity(ImageEntity sourceImage, ImageEntity referenceImage, String algorithm, String requestedTransformationModel) {
        this.sourceImage = sourceImage;
        this.referenceImage = referenceImage;
        this.algorithm = algorithm;
        this.requestedTransformationModel = requestedTransformationModel;
        this.status = "PENDING";
        this.createdAt = LocalDateTime.now();
    }

    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public ImageEntity getSourceImage() { return sourceImage; }
    public void setSourceImage(ImageEntity sourceImage) { this.sourceImage = sourceImage; }

    public ImageEntity getReferenceImage() { return referenceImage; }
    public void setReferenceImage(ImageEntity referenceImage) { this.referenceImage = referenceImage; }

    public String getAlgorithm() { return algorithm; }
    public void setAlgorithm(String algorithm) { this.algorithm = algorithm; }

    public String getRequestedTransformationModel() { return requestedTransformationModel; }
    public void setRequestedTransformationModel(String requestedTransformationModel) { this.requestedTransformationModel = requestedTransformationModel; }

    public String getSelectedTransformationModel() { return selectedTransformationModel; }
    public void setSelectedTransformationModel(String selectedTransformationModel) { this.selectedTransformationModel = selectedTransformationModel; }

    public String getTransformationMatrixJson() { return transformationMatrixJson; }
    public void setTransformationMatrixJson(String transformationMatrixJson) { this.transformationMatrixJson = transformationMatrixJson; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public String getFailureReason() { return failureReason; }
    public void setFailureReason(String failureReason) { this.failureReason = failureReason; }

    public String getWarpedImageStoragePath() { return warpedImageStoragePath; }
    public void setWarpedImageStoragePath(String warpedImageStoragePath) { this.warpedImageStoragePath = warpedImageStoragePath; }

    public String getMatchVisStoragePath() { return matchVisStoragePath; }
    public void setMatchVisStoragePath(String matchVisStoragePath) { this.matchVisStoragePath = matchVisStoragePath; }

    public String getAlphaOverlayStoragePath() { return alphaOverlayStoragePath; }
    public void setAlphaOverlayStoragePath(String alphaOverlayStoragePath) { this.alphaOverlayStoragePath = alphaOverlayStoragePath; }

    public String getCheckerboardStoragePath() { return checkerboardStoragePath; }
    public void setCheckerboardStoragePath(String checkerboardStoragePath) { this.checkerboardStoragePath = checkerboardStoragePath; }

    public String getDifferenceMapStoragePath() { return differenceMapStoragePath; }
    public void setDifferenceMapStoragePath(String differenceMapStoragePath) { this.differenceMapStoragePath = differenceMapStoragePath; }

    public RegistrationMetricsEntity getMetrics() { return metrics; }
    public void setMetrics(RegistrationMetricsEntity metrics) { this.metrics = metrics; }

    public List<MatchPointEntity> getMatchPoints() { return matchPoints; }
    public void setMatchPoints(List<MatchPointEntity> matchPoints) { this.matchPoints = matchPoints; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }

    public LocalDateTime getCompletedAt() { return completedAt; }
    public void setCompletedAt(LocalDateTime completedAt) { this.completedAt = completedAt; }
}
