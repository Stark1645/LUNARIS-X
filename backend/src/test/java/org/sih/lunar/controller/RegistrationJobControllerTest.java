package org.sih.lunar.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.sih.lunar.dto.RegistrationRequestDTO;
import org.sih.lunar.dto.RegistrationResponseDTO;
import org.sih.lunar.service.RegistrationService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class RegistrationJobControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private RegistrationService registrationService;

    @Test
    void testSubmitRegistrationWithMissingSourceImageIdFailsValidation() throws Exception {
        RegistrationRequestDTO req = new RegistrationRequestDTO();
        req.setReferenceImageId(2L); // Missing sourceImageId

        mockMvc.perform(post("/api/v1/jobs/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error").value("Validation Failed"));
    }

    @Test
    void testSubmitValidRegistrationJobSucceeds() throws Exception {
        RegistrationRequestDTO req = new RegistrationRequestDTO();
        req.setSourceImageId(1L);
        req.setReferenceImageId(2L);
        req.setAlgorithm("Proposed_Method");

        RegistrationResponseDTO resp = new RegistrationResponseDTO();
        resp.setJobId(101L);
        resp.setStatus("SUCCESS");
        resp.setAlgorithm("Proposed_Method");
        resp.setSelectedTransformationModel("HOMOGRAPHY");

        when(registrationService.createAndExecuteJob(any(RegistrationRequestDTO.class))).thenReturn(resp);

        mockMvc.perform(post("/api/v1/jobs/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.jobId").value(101))
                .andExpect(jsonPath("$.status").value("SUCCESS"))
                .andExpect(jsonPath("$.algorithm").value("Proposed_Method"));
    }

    @Test
    void testListAllJobsReturnsList() throws Exception {
        mockMvc.perform(get("/api/v1/jobs"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$").isArray());
    }
}
