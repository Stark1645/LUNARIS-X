package org.sih.lunar.repository;

import org.sih.lunar.entity.MatchPointEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface MatchPointRepository extends JpaRepository<MatchPointEntity, Long> {
    List<MatchPointEntity> findByJobId(Long jobId);
    List<MatchPointEntity> findByJobIdAndIsInlier(Long jobId, Boolean isInlier);
}
