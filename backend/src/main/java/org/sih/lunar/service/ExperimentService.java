package org.sih.lunar.service;

import org.sih.lunar.dto.ExperimentDTO;
import org.sih.lunar.entity.ExperimentEntity;
import org.sih.lunar.repository.ExperimentRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class ExperimentService {

    private final ExperimentRepository experimentRepository;

    public ExperimentService(ExperimentRepository experimentRepository) {
        this.experimentRepository = experimentRepository;
    }

    @Transactional(readOnly = true)
    public List<ExperimentDTO> getAllExperiments() {
        return experimentRepository.findAllByOrderByExecutedAtDesc().stream()
                .map(this::mapToDTO).toList();
    }

    @Transactional(readOnly = true)
    public List<ExperimentDTO> getExperimentsBySuite(String suiteName) {
        return experimentRepository.findBySuiteName(suiteName).stream()
                .map(this::mapToDTO).toList();
    }

    @Transactional
    public ExperimentDTO saveExperiment(ExperimentDTO dto) {
        ExperimentEntity entity = new ExperimentEntity();
        entity.setExperimentId(dto.getExperimentId());
        entity.setSuiteName(dto.getSuiteName());
        entity.setPairName(dto.getPairName());
        entity.setAlgorithm(dto.getAlgorithm());
        entity.setConfigurationName(dto.getConfigurationName());
        entity.setDataCategory(dto.getDataCategory() != null ? dto.getDataCategory() : "SYNTHETIC_BENCHMARK");
        entity.setScaleRatio(dto.getScaleRatio());
        entity.setDeltaSunAzimuthDeg(dto.getDeltaSunAzimuthDeg());
        entity.setInlierCount(dto.getInlierCount());
        entity.setInlierRatioPercent(dto.getInlierRatioPercent());
        entity.setRmseInliersPx(dto.getRmseInliersPx());
        entity.setRmseGroundTruthPx(dto.getRmseGroundTruthPx());
        entity.setSpatialGini(dto.getSpatialGini());
        entity.setLatencyMs(dto.getLatencyMs());
        entity.setStatus(dto.getStatus());

        entity = experimentRepository.save(entity);
        return mapToDTO(entity);
    }

    private ExperimentDTO mapToDTO(ExperimentEntity entity) {
        ExperimentDTO dto = new ExperimentDTO();
        dto.setId(entity.getId());
        dto.setExperimentId(entity.getExperimentId());
        dto.setSuiteName(entity.getSuiteName());
        dto.setPairName(entity.getPairName());
        dto.setAlgorithm(entity.getAlgorithm());
        dto.setConfigurationName(entity.getConfigurationName());
        dto.setDataCategory(entity.getDataCategory());
        dto.setScaleRatio(entity.getScaleRatio());
        dto.setDeltaSunAzimuthDeg(entity.getDeltaSunAzimuthDeg());
        dto.setInlierCount(entity.getInlierCount());
        dto.setInlierRatioPercent(entity.getInlierRatioPercent());
        dto.setRmseInliersPx(entity.getRmseInliersPx());
        dto.setRmseGroundTruthPx(entity.getRmseGroundTruthPx());
        dto.setSpatialGini(entity.getSpatialGini());
        dto.setLatencyMs(entity.getLatencyMs());
        dto.setStatus(entity.getStatus());
        dto.setExecutedAt(entity.getExecutedAt());
        return dto;
    }
}
