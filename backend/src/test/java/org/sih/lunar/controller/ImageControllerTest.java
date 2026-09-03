package org.sih.lunar.controller;

import org.junit.jupiter.api.Test;
import org.sih.lunar.entity.ImageEntity;
import org.sih.lunar.repository.ImageRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.multipart;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class ImageControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ImageRepository imageRepository;

    @Test
    void testUploadValidImageSucceeds() throws Exception {
        MockMultipartFile file = new MockMultipartFile(
                "file",
                "test_crater.png",
                "image/png",
                "fake-png-binary-content-for-testing".getBytes()
        );

        mockMvc.perform(multipart("/api/v1/images/upload")
                        .file(file)
                        .param("sensor_name", "TMC-2")
                        .param("mission_name", "CHANDRAYAAN-2")
                        .param("gsd_meters", "5.0"))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id").exists())
                .andExpect(jsonPath("$.filename").value("test_crater.png"))
                .andExpect(jsonPath("$.sensorName").value("TMC-2"))
                .andExpect(jsonPath("$.sha256Checksum").exists());
    }

    @Test
    void testUploadUnsupportedExtensionFailsWithBadRequest() throws Exception {
        MockMultipartFile file = new MockMultipartFile(
                "file",
                "malicious_script.exe",
                "application/x-msdownload",
                "binary-bytes".getBytes()
        );

        mockMvc.perform(multipart("/api/v1/images/upload")
                        .file(file))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error").value("Bad Request"));
    }

    @Test
    void testListImagesReturnsList() throws Exception {
        mockMvc.perform(get("/api/v1/images"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$").isArray());
    }
}
