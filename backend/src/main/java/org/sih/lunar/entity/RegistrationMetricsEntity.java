package org.sih.lunar.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "registration_metrics")
public class RegistrationMetricsEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private Integer candidateMatchesCount;
    private Integer inlierMatchesCount;
    private Double inlierRatioPercent;

    private Double rmseInliersPx;
    private Double rmseGroundTruthPx;
    private Double meanSubpixelResidualPx;
    private Double subpixelAccuracyRate05px;
    private Double spatialGiniCoefficient;
    private Double latencyMs;

    @Column(nullable = false)
    private String dataCategory; // SYNTHETIC_BENCHMARK | AUTHENTIC_CH2_PRADAN

    public RegistrationMetricsEntity() {
        this.dataCategory = "SYNTHETIC_BENCHMARK";
    }

    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

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
