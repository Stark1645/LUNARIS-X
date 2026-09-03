package org.sih.lunar.dto;

import java.time.LocalDateTime;

public class ExperimentDTO {
    private Long id;
    private String experimentId;
    private String suiteName;
    private String pairName;
    private String algorithm;
    private String configurationName;
    private String dataCategory;
    private Double scaleRatio;
    private Double deltaSunAzimuthDeg;
    private Integer inlierCount;
    private Double inlierRatioPercent;
    private Double rmseInliersPx;
    private Double rmseGroundTruthPx;
    private Double spatialGini;
    private Double latencyMs;
    private String status;
    private LocalDateTime executedAt;

    public ExperimentDTO() {}

    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getExperimentId() { return experimentId; }
    public void setExperimentId(String experimentId) { this.experimentId = experimentId; }

    public String getSuiteName() { return suiteName; }
    public void setSuiteName(String suiteName) { this.suiteName = suiteName; }

    public String getPairName() { return pairName; }
    public void setPairName(String pairName) { this.pairName = pairName; }

    public String getAlgorithm() { return algorithm; }
    public void setAlgorithm(String algorithm) { this.algorithm = algorithm; }

    public String getConfigurationName() { return configurationName; }
    public void setConfigurationName(String configurationName) { this.configurationName = configurationName; }

    public String getDataCategory() { return dataCategory; }
    public void setDataCategory(String dataCategory) { this.dataCategory = dataCategory; }

    public Double getScaleRatio() { return scaleRatio; }
    public void setScaleRatio(Double scaleRatio) { this.scaleRatio = scaleRatio; }

    public Double getDeltaSunAzimuthDeg() { return deltaSunAzimuthDeg; }
    public void setDeltaSunAzimuthDeg(Double deltaSunAzimuthDeg) { this.deltaSunAzimuthDeg = deltaSunAzimuthDeg; }

    public Integer getInlierCount() { return inlierCount; }
    public void setInlierCount(Integer inlierCount) { this.inlierCount = inlierCount; }

    public Double getInlierRatioPercent() { return inlierRatioPercent; }
    public void setInlierRatioPercent(Double inlierRatioPercent) { this.inlierRatioPercent = inlierRatioPercent; }

    public Double getRmseInliersPx() { return rmseInliersPx; }
    public void setRmseInliersPx(Double rmseInliersPx) { this.rmseInliersPx = rmseInliersPx; }

    public Double getRmseGroundTruthPx() { return rmseGroundTruthPx; }
    public void setRmseGroundTruthPx(Double rmseGroundTruthPx) { this.rmseGroundTruthPx = rmseGroundTruthPx; }

    public Double getSpatialGini() { return spatialGini; }
    public void setSpatialGini(Double spatialGini) { this.spatialGini = spatialGini; }

    public Double getLatencyMs() { return latencyMs; }
    public void setLatencyMs(Double latencyMs) { this.latencyMs = latencyMs; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public LocalDateTime getExecutedAt() { return executedAt; }
    public void setExecutedAt(LocalDateTime executedAt) { this.executedAt = executedAt; }
}
