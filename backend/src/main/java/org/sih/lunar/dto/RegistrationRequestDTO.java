package org.sih.lunar.dto;

import jakarta.validation.constraints.NotNull;

public class RegistrationRequestDTO {

    @NotNull(message = "Source image ID must not be null")
    private Long sourceImageId;

    @NotNull(message = "Reference image ID must not be null")
    private Long referenceImageId;

    private String algorithm = "Proposed_Method"; // Proposed_Method | SIFT_Baseline | RIFT_Baseline
    private String transformationModel = "HOMOGRAPHY"; // HOMOGRAPHY | AFFINE | SIMILARITY | TRANSLATION
    private Double ratioThreshold = 0.80;
    private Double ransacThreshold = 3.0;
    private Boolean enableSubpixel = true;
    private Boolean enableSpatialFilter = true;

    public RegistrationRequestDTO() {}

    public Long getSourceImageId() { return sourceImageId; }
    public void setSourceImageId(Long sourceImageId) { this.sourceImageId = sourceImageId; }

    public Long getReferenceImageId() { return referenceImageId; }
    public void setReferenceImageId(Long referenceImageId) { this.referenceImageId = referenceImageId; }

    public String getAlgorithm() { return algorithm; }
    public void setAlgorithm(String algorithm) { this.algorithm = algorithm; }

    public String getTransformationModel() { return transformationModel; }
    public void setTransformationModel(String transformationModel) { this.transformationModel = transformationModel; }

    public Double getRatioThreshold() { return ratioThreshold; }
    public void setRatioThreshold(Double ratioThreshold) { this.ratioThreshold = ratioThreshold; }

    public Double getRansacThreshold() { return ransacThreshold; }
    public void setRansacThreshold(Double ransacThreshold) { this.ransacThreshold = ransacThreshold; }

    public Boolean getEnableSubpixel() { return enableSubpixel; }
    public void setEnableSubpixel(Boolean enableSubpixel) { this.enableSubpixel = enableSubpixel; }

    public Boolean getEnableSpatialFilter() { return enableSpatialFilter; }
    public void setEnableSpatialFilter(Boolean enableSpatialFilter) { this.enableSpatialFilter = enableSpatialFilter; }
}
