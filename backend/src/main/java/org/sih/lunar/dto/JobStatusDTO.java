package org.sih.lunar.dto;

import java.time.LocalDateTime;

public class JobStatusDTO {
    private Long jobId;
    private String status;
    private String algorithm;
    private String failureReason;
    private LocalDateTime createdAt;
    private LocalDateTime completedAt;

    public JobStatusDTO() {}

    public JobStatusDTO(Long jobId, String status, String algorithm, String failureReason, LocalDateTime createdAt, LocalDateTime completedAt) {
        this.jobId = jobId;
        this.status = status;
        this.algorithm = algorithm;
        this.failureReason = failureReason;
        this.createdAt = createdAt;
        this.completedAt = completedAt;
    }

    public Long getJobId() { return jobId; }
    public void setJobId(Long jobId) { this.jobId = jobId; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public String getAlgorithm() { return algorithm; }
    public void setAlgorithm(String algorithm) { this.algorithm = algorithm; }

    public String getFailureReason() { return failureReason; }
    public void setFailureReason(String failureReason) { this.failureReason = failureReason; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }

    public LocalDateTime getCompletedAt() { return completedAt; }
    public void setCompletedAt(LocalDateTime completedAt) { this.completedAt = completedAt; }
}
