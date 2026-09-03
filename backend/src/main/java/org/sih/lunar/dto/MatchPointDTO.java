package org.sih.lunar.dto;

public class MatchPointDTO {

    private Double sourceX;
    private Double sourceY;
    private Double referenceX;
    private Double referenceY;
    private Boolean isInlier;

    public MatchPointDTO() {}

    public MatchPointDTO(Double sourceX, Double sourceY, Double referenceX, Double referenceY, Boolean isInlier) {
        this.sourceX = sourceX;
        this.sourceY = sourceY;
        this.referenceX = referenceX;
        this.referenceY = referenceY;
        this.isInlier = isInlier;
    }

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
