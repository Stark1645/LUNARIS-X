package org.sih.lunar.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.sih.lunar.dto.ImageUploadResponseDTO;
import org.sih.lunar.entity.ImageEntity;
import org.sih.lunar.exception.ResourceNotFoundException;
import org.sih.lunar.repository.ImageRepository;
import org.sih.lunar.service.ImageStorageService;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

@RestController
@RequestMapping("/api/v1/images")
@Tag(name = "Images", description = "Endpoints for lunar optical and reference image upload and metadata inspection")
public class ImageController {

    private final ImageStorageService storageService;
    private final ImageRepository imageRepository;

    public ImageController(ImageStorageService storageService, ImageRepository imageRepository) {
        this.storageService = storageService;
        this.imageRepository = imageRepository;
    }

    @PostMapping(value = "/upload", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    @Operation(summary = "Upload image file", description = "Uploads a lunar image (PNG/TIFF/RAW), computes cryptographic SHA-256 hash, and saves metadata.")
    public ResponseEntity<ImageUploadResponseDTO> uploadImage(
            @RequestParam("file") MultipartFile file,
            @RequestParam(value = "sensor_name", required = false, defaultValue = "OPTICAL") String sensorName,
            @RequestParam(value = "mission_name", required = false, defaultValue = "CHANDRAYAAN-2") String missionName,
            @RequestParam(value = "gsd_meters", required = false) Double gsdMeters,
            @RequestParam(value = "data_category", required = false, defaultValue = "SYNTHETIC_BENCHMARK") String dataCategory) {

        ImageEntity entity = storageService.storeImage(file, sensorName, missionName, gsdMeters, dataCategory);
        return new ResponseEntity<>(mapToDTO(entity), HttpStatus.CREATED);
    }

    @GetMapping
    @Operation(summary = "List all images", description = "Returns all uploaded source and reference images.")
    public ResponseEntity<List<ImageUploadResponseDTO>> listImages() {
        List<ImageUploadResponseDTO> list = imageRepository.findAll().stream()
                .map(this::mapToDTO).toList();
        return ResponseEntity.ok(list);
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get image metadata by ID", description = "Retrieves stored image metadata and cryptographic hash.")
    public ResponseEntity<ImageUploadResponseDTO> getImageById(@PathVariable("id") Long id) {
        ImageEntity entity = imageRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Image not found with ID: " + id));
        return ResponseEntity.ok(mapToDTO(entity));
    }

    private ImageUploadResponseDTO mapToDTO(ImageEntity e) {
        ImageUploadResponseDTO dto = new ImageUploadResponseDTO();
        dto.setId(e.getId());
        dto.setFilename(e.getFilename());
        dto.setFileType(e.getFileType());
        dto.setFileSize(e.getFileSize());
        dto.setSha256Checksum(e.getSha256Checksum());
        dto.setWidth(e.getWidth());
        dto.setHeight(e.getHeight());
        dto.setGsdMeters(e.getGsdMeters());
        dto.setSensorName(e.getSensorName());
        dto.setMissionName(e.getMissionName());
        dto.setDataCategory(e.getDataCategory());
        dto.setUploadedAt(e.getUploadedAt());
        return dto;
    }
}
