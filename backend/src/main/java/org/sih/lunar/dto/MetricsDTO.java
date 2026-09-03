package org.sih.lunar.dto;

public class MetricsDTO {

    private Integer candidateMatchesCount;
    private Integer inlierMatchesCount;
    private Double inlierRatioPercent;

    private Double rmseInliersPx;
    private Double rmseGroundTruthPx;
    private Double meanSubpixelResidualPx;
    private Double subpixelAccuracyRate05px;
    private Double spatialGiniCoefficient;
    private Double latencyMs;
    private String dataCategory;

    public MetricsDTO() {}

    // Getters and Setters
    public Integer getCandidateMatchesCount() { return candidateMatchesCount; }
    public void setCandidateMatchesCount(Integer candidateMatchesCount) { this.candidateMatchesCount = candidateMatchesCount; }

    public Integer getInlierMatchesCount() { return inlierMatchesCount; }
    public void setInlierMatchesCount(Integer inlierMatchesCount) { this.inlierMatchesCount = inlierMatchesCount; }

    public Double getInlierRatioPercent() { return inlierRatioPercent; }
    public void setInlierRatioPercent(Double inlierRatioPercent) { this.inlierRatioPercent = inlierRatioPercent; }

    public Double getRmseInliersPx() { return rmseInliersPx; }
    public void setRmseInliersPx(Double rmseInliersPx) { this.rmseInliersPx = rmseInliersPx; }

    public Double getRmseGroundTruthPx() { return rmseGroundTruthPx; }
    public void setRmseGroundTruthPx(Double rmseGroundTruthPx) { this.rmseGroundTruthPx = rmseGroundTruthPx; }

    public Double getMeanSubpixelResidualPx() { return meanSubpixelResidualPx; }
    public void setMeanSubpixelResidualPx(Double meanSubpixelResidualPx) { this.meanSubpixelResidualPx = meanSubpixelResidualPx; }

    public Double getSubpixelAccuracyRate05px() { return subpixelAccuracyRate05px; }
    public void setSubpixelAccuracyRate05px(Double subpixelAccuracyRate05px) { this.subpixelAccuracyRate05px = subpixelAccuracyRate05px; }

    public Double getSpatialGiniCoefficient() { return spatialGiniCoefficient; }
    public void setSpatialGiniCoefficient(Double spatialGiniCoefficient) { this.spatialGiniCoefficient = spatialGiniCoefficient; }

    public Double getLatencyMs() { return latencyMs; }
    public void setLatencyMs(Double latencyMs) { this.latencyMs = latencyMs; }

    public String getDataCategory() { return dataCategory; }
    public void setDataCategory(String dataCategory) { this.dataCategory = dataCategory; }
}
