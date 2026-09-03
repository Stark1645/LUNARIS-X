package org.sih.lunar.service;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.sih.lunar.dto.ExperimentDTO;
import org.sih.lunar.entity.ExperimentEntity;
import org.sih.lunar.repository.ExperimentRepository;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ExperimentServiceTest {

    @Mock
    private ExperimentRepository experimentRepository;

    private ExperimentService experimentService;

    @BeforeEach
    void setUp() {
        this.experimentService = new ExperimentService(experimentRepository);
    }

    @Test
    void testSaveAndGetExperiments() {
        ExperimentDTO dto = new ExperimentDTO();
        dto.setExperimentId("EXP-001");
        dto.setSuiteName("suite_a_intra_sensor");
        dto.setPairName("pair_01_baseline_same_sun");
        dto.setAlgorithm("Proposed_Method");
        dto.setStatus("SUCCESS");

        when(experimentRepository.save(any(ExperimentEntity.class))).thenAnswer(i -> {
            ExperimentEntity e = i.getArgument(0);
            e.setId(1L);
            return e;
        });

        ExperimentDTO saved = experimentService.saveExperiment(dto);
        assertNotNull(saved);
        assertEquals(1L, saved.getId());
        assertEquals("EXP-001", saved.getExperimentId());

        ExperimentEntity e = new ExperimentEntity();
        e.setId(1L);
        e.setSuiteName("suite_a_intra_sensor");
        e.setPairName("pair_01_baseline_same_sun");
        e.setAlgorithm("Proposed_Method");
        e.setStatus("SUCCESS");

        when(experimentRepository.findBySuiteName("suite_a_intra_sensor")).thenReturn(List.of(e));

        List<ExperimentDTO> list = experimentService.getExperimentsBySuite("suite_a_intra_sensor");
        assertEquals(1, list.size());
        assertEquals("pair_01_baseline_same_sun", list.get(0).getPairName());
    }
}
