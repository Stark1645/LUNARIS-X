package org.sih.lunar.repository;

import org.sih.lunar.entity.RegistrationMetricsEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface RegistrationMetricsRepository extends JpaRepository<RegistrationMetricsEntity, Long> {
}
