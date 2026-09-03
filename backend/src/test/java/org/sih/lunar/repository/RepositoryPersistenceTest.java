package org.sih.lunar.repository;

import org.junit.jupiter.api.Test;
import org.sih.lunar.entity.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.test.context.ActiveProfiles;

import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;

@DataJpaTest
@ActiveProfiles("test")
class RepositoryPersistenceTest {

    @Autowired
    private ImageRepository imageRepository;

    @Autowired
    private RegistrationJobRepository jobRepository;

    @Autowired
    private ExperimentRepository experimentRepository;

    @Test
    void testImagePersistenceAndSha256Lookup() {
        ImageEntity img = new ImageEntity("tmc2_north.png", "/path/to/tmc2.png", "PNG", 1024L, "abc123sha256hash", "AUTHENTIC_CH2_PRADAN");
        img.setSensorName("TMC-2");
        img.setGsdMeters(5.0);

        ImageEntity saved = imageRepository.save(img);
        assertNotNull(saved.getId());

        Optional<ImageEntity> found = imageRepository.findBySha256Checksum("abc123sha256hash");
        assertTrue(found.isPresent());
        assertEquals("TMC-2", found.get().getSensorName());
        assertEquals("AUTHENTIC_CH2_PRADAN", found.get().getDataCategory());
    }

    @Test
    void testRegistrationJobWithCascadingMetricsAndMatchPoints() {
        ImageEntity src = imageRepository.save(new ImageEntity("src.png", "/p/src.png", "PNG", 500L, "hash1", "SYNTHETIC_BENCHMARK"));
        ImageEntity ref = imageRepository.save(new ImageEntity("ref.png", "/p/ref.png", "PNG", 500L, "hash2", "SYNTHETIC_BENCHMARK"));

        RegistrationJobEntity job = new RegistrationJobEntity(src, ref, "Proposed_Method", "HOMOGRAPHY");
        job.setStatus("SUCCESS");
        job.setSelectedTransformationModel("HOMOGRAPHY");

        RegistrationMetricsEntity metrics = new RegistrationMetricsEntity();
        metrics.setCandidateMatchesCount(95);
        metrics.setInlierMatchesCount(87);
        metrics.setInlierRatioPercent(91.58);
        metrics.setRmseInliersPx(1.27);
        metrics.setRmseGroundTruthPx(0.41);
        metrics.setSpatialGiniCoefficient(0.32);
        metrics.setLatencyMs(390.0);
        metrics.setDataCategory("SYNTHETIC_BENCHMARK");
        job.setMetrics(metrics);

        MatchPointEntity pt1 = new MatchPointEntity(job, 10.0, 20.0, 12.0, 22.0, true);
        MatchPointEntity pt2 = new MatchPointEntity(job, 50.0, 60.0, 52.0, 62.0, true);
        job.getMatchPoints().add(pt1);
        job.getMatchPoints().add(pt2);

        RegistrationJobEntity savedJob = jobRepository.save(job);
        assertNotNull(savedJob.getId());
        assertNotNull(savedJob.getMetrics().getId());
        assertEquals(2, savedJob.getMatchPoints().size());
        assertEquals(0.41, savedJob.getMetrics().getRmseGroundTruthPx(), 0.001);
    }

    @Test
    void testExperimentPersistenceAndSuiteQuery() {
        ExperimentEntity exp = new ExperimentEntity();
        exp.setExperimentId("EXP-P4-01");
        exp.setSuiteName("suite_c_scale_disparity");
        exp.setPairName("pair_04_scale_4x");
        exp.setAlgorithm("Proposed_Method");
        exp.setInlierCount(87);
        exp.setInlierRatioPercent(91.58);
        exp.setRmseGroundTruthPx(0.41);
        exp.setStatus("SUCCESS");
        exp.setDataCategory("SYNTHETIC_BENCHMARK");

        experimentRepository.save(exp);

        List<ExperimentEntity> list = experimentRepository.findBySuiteName("suite_c_scale_disparity");
        assertFalse(list.isEmpty());
        assertEquals("pair_04_scale_4x", list.get(0).getPairName());
    }
}
