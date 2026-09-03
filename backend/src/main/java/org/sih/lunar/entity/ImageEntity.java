package org.sih.lunar.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "images")
public class ImageEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String filename;

    @Column(nullable = false)
    private String storagePath;

    @Column(nullable = false)
    private String fileType; // PNG, TIFF, GEOTIFF, RAW

    @Column(nullable = false)
    private Long fileSize;

    @Column(nullable = false, length = 64)
    private String sha256Checksum;

    private Integer width;
    private Integer height;
    private Double gsdMeters;
    private String sensorName; // TMC-2, OHRC, IIRS, SYNTHETIC
    private String missionName; // Chandrayaan-2, LRO, Synthetic
    
    @Column(nullable = false)
    private String dataCategory; // SYNTHETIC_BENCHMARK | AUTHENTIC_CH2_PRADAN

    @Column(nullable = false)
    private LocalDateTime uploadedAt;

    public ImageEntity() {
        this.uploadedAt = LocalDateTime.now();
        this.dataCategory = "SYNTHETIC_BENCHMARK";
    }

    public ImageEntity(String filename, String storagePath, String fileType, Long fileSize, String sha256Checksum, String dataCategory) {
        this.filename = filename;
        this.storagePath = storagePath;
        this.fileType = fileType;
        this.fileSize = fileSize;
        this.sha256Checksum = sha256Checksum;
        this.dataCategory = dataCategory != null ? dataCategory : "SYNTHETIC_BENCHMARK";
        this.uploadedAt = LocalDateTime.now();
    }

    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getFilename() { return filename; }
    public void setFilename(String filename) { this.filename = filename; }

    public String getStoragePath() { return storagePath; }
    public void setStoragePath(String storagePath) { this.storagePath = storagePath; }

    public String getFileType() { return fileType; }
    public void setFileType(String fileType) { this.fileType = fileType; }

    public Long getFileSize() { return fileSize; }
    public void setFileSize(Long fileSize) { this.fileSize = fileSize; }

    public String getSha256Checksum() { return sha256Checksum; }
    public void setSha256Checksum(String sha256Checksum) { this.sha256Checksum = sha256Checksum; }

    public Integer getWidth() { return width; }
    public void setWidth(Integer width) { this.width = width; }

    public Integer getHeight() { return height; }
    public void setHeight(Integer height) { this.height = height; }

    public Double getGsdMeters() { return gsdMeters; }
    public void setGsdMeters(Double gsdMeters) { this.gsdMeters = gsdMeters; }

    public String getSensorName() { return sensorName; }
    public void setSensorName(String sensorName) { this.sensorName = sensorName; }

    public String getMissionName() { return missionName; }
    public void setMissionName(String missionName) { this.missionName = missionName; }

    public String getDataCategory() { return dataCategory; }
    public void setDataCategory(String dataCategory) { this.dataCategory = dataCategory; }

    public LocalDateTime getUploadedAt() { return uploadedAt; }
    public void setUploadedAt(LocalDateTime uploadedAt) { this.uploadedAt = uploadedAt; }
}
