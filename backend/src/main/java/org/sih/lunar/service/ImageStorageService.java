package org.sih.lunar.service;

import org.sih.lunar.entity.ImageEntity;
import org.sih.lunar.exception.ValidationException;
import org.sih.lunar.repository.ImageRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Service
public class ImageStorageService {

    private final Path storageRoot;
    private final ImageRepository imageRepository;
    private static final List<String> ALLOWED_EXTENSIONS = List.of(".png", ".jpg", ".jpeg", ".tif", ".tiff", ".raw");

    public ImageStorageService(
            @Value("${storage.location:data/storage}") String storageLocation,
            ImageRepository imageRepository) {
        this.storageRoot = Paths.get(storageLocation).toAbsolutePath().normalize();
        this.imageRepository = imageRepository;
        try {
            Files.createDirectories(this.storageRoot);
        } catch (IOException e) {
            throw new RuntimeException("Could not initialize storage directory: " + this.storageRoot, e);
        }
    }

    public ImageEntity storeImage(MultipartFile file, String sensorName, String missionName, Double gsdMeters, String dataCategory) {
        if (file == null || file.isEmpty()) {
            throw new ValidationException("Uploaded file cannot be null or empty.");
        }

        String originalFilename = file.getOriginalFilename();
        if (originalFilename == null || originalFilename.contains("..")) {
            throw new ValidationException("Invalid filename containing forbidden path traversal characters.");
        }

        // Validate extension
        String extension = "";
        int dotIdx = originalFilename.lastIndexOf('.');
        if (dotIdx >= 0) {
            extension = originalFilename.substring(dotIdx).toLowerCase();
        }

        if (!ALLOWED_EXTENSIONS.contains(extension)) {
            throw new ValidationException("Unsupported file type: " + extension + ". Allowed: " + ALLOWED_EXTENSIONS);
        }

        // Compute SHA-256
        String checksum = computeSha256(file);

        // Auto-detect sensor and category from filename if not explicitly provided or if default
        String lower = originalFilename.toLowerCase();
        if (lower.contains("ohr")) {
            sensorName = "OHRC";
            if (gsdMeters == null || gsdMeters == 5.0) {
                gsdMeters = 0.25;
            }
        } else if (lower.contains("tmc")) {
            sensorName = "TMC-2";
            if (gsdMeters == null || gsdMeters == 0.25) {
                gsdMeters = 5.0;
            }
        } else if (lower.contains("iirs")) {
            sensorName = "IIRS";
            if (gsdMeters == null) {
                gsdMeters = 5.0;
            }
        }

        if (lower.startsWith("ch2_") || lower.contains("pradan") || lower.contains("_b_brw_") || lower.contains("_d_img_")) {
            dataCategory = "AUTHENTIC_CH2_PRADAN";
        }

        // Check if identical image exists
        Optional<ImageEntity> existing = imageRepository.findBySha256Checksum(checksum);
        if (existing.isPresent()) {
            ImageEntity entity = existing.get();
            if (sensorName != null && !sensorName.isBlank()) entity.setSensorName(sensorName);
            if (missionName != null && !missionName.isBlank()) entity.setMissionName(missionName);
            if (gsdMeters != null) entity.setGsdMeters(gsdMeters);
            if (dataCategory != null && !dataCategory.isBlank()) entity.setDataCategory(dataCategory);
            return imageRepository.save(entity);
        }

        // Store file safely
        String safeName = UUID.randomUUID() + extension;
        Path targetPath = this.storageRoot.resolve(safeName).normalize();

        try (InputStream in = file.getInputStream()) {
            Files.copy(in, targetPath, StandardCopyOption.REPLACE_EXISTING);
        } catch (IOException e) {
            throw new RuntimeException("Failed to store file: " + targetPath, e);
        }

        ImageEntity entity = new ImageEntity(
                originalFilename,
                targetPath.toString(),
                extension.replace(".", "").toUpperCase(),
                file.getSize(),
                checksum,
                dataCategory != null ? dataCategory : "SYNTHETIC_BENCHMARK"
        );

        entity.setSensorName(sensorName != null ? sensorName : "OPTICAL");
        entity.setMissionName(missionName != null ? missionName : "CHANDRAYAAN-2");
        entity.setGsdMeters(gsdMeters);

        return imageRepository.save(entity);
    }

    public File getImageFile(ImageEntity entity) {
        Path filePath = Paths.get(entity.getStoragePath()).normalize();
        File file = filePath.toFile();
        if (!file.exists()) {
            throw new ValidationException("Stored image file not found on disk: " + filePath);
        }
        return file;
    }

    private String computeSha256(MultipartFile file) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(file.getBytes());
            return HexFormat.of().formatHex(hash);
        } catch (NoSuchAlgorithmException | IOException e) {
            throw new RuntimeException("Failed to compute SHA-256 checksum", e);
        }
    }
}
