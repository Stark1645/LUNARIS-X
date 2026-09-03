package org.sih.lunar.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "match_points")
public class MatchPointEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "job_id", nullable = false)
    private RegistrationJobEntity job;

    @Column(nullable = false)
    private Double sourceX;

    @Column(nullable = false)
    private Double sourceY;

    @Column(nullable = false)
    private Double referenceX;

    @Column(nullable = false)
    private Double referenceY;

    @Column(nullable = false)
    private Boolean isInlier;

    public MatchPointEntity() {}

    public MatchPointEntity(RegistrationJobEntity job, Double sourceX, Double sourceY, Double referenceX, Double referenceY, Boolean isInlier) {
        this.job = job;
        this.sourceX = sourceX;
        this.sourceY = sourceY;
        this.referenceX = referenceX;
        this.referenceY = referenceY;
        this.isInlier = isInlier;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public RegistrationJobEntity getJob() { return job; }
    public void setJob(RegistrationJobEntity job) { this.job = job; }

    public Double getSourceX() { return sourceX; }
    public void setSourceX(Double sourceX) { this.sourceX = sourceX; }

    public Double getSourceY() { return sourceY; }
    public void setSourceY(Double sourceY) { this.sourceY = sourceY; }

    public Double getReferenceX() { return referenceX; }
    public void setReferenceX(Double referenceX) { this.referenceX = referenceX; }

    public Double getReferenceY() { return referenceY; }
    public void setReferenceY(Double referenceY) { this.referenceY = referenceY; }

    public Boolean getIsInlier() { return isInlier; }
    public void setIsInlier(Boolean inlier) { isInlier = inlier; }
}
