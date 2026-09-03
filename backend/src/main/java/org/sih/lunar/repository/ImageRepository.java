package org.sih.lunar.repository;

import org.sih.lunar.entity.ImageEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.Optional;
import java.util.List;

@Repository
public interface ImageRepository extends JpaRepository<ImageEntity, Long> {
    Optional<ImageEntity> findBySha256Checksum(String sha256Checksum);
    List<ImageEntity> findByDataCategory(String dataCategory);
    List<ImageEntity> findBySensorName(String sensorName);
}
