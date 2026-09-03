package org.sih.lunar.repository;

import org.sih.lunar.entity.ExperimentEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface ExperimentRepository extends JpaRepository<ExperimentEntity, Long> {
    List<ExperimentEntity> findBySuiteName(String suiteName);
    List<ExperimentEntity> findByAlgorithm(String algorithm);
    List<ExperimentEntity> findByDataCategory(String dataCategory);
    List<ExperimentEntity> findAllByOrderByExecutedAtDesc();
}
