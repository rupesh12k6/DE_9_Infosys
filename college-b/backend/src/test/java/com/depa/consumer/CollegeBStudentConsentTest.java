package com.depa.consumer;

import com.depa.consumer.client.ConsentManagerClient;
import com.depa.consumer.dto.ConsentDecisionResponse;
import com.depa.consumer.entity.Student;
import com.depa.consumer.entity.StudentStatus;
import com.depa.consumer.repository.StudentRepository;
import com.depa.consumer.security.CollegeBJwtUtil;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.web.client.HttpClientErrorException;

import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.List;
import java.util.Map;

import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.atLeastOnce;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
class CollegeBStudentConsentTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private StudentRepository studentRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Autowired
    private CollegeBJwtUtil jwtUtil;

    @MockBean
    private ConsentManagerClient consentManagerClient;

    private String studentToken;

    @BeforeEach
    void setUp() {
        studentRepository.deleteAll();
        studentRepository.save(new Student(
                "STU-B-CONSENT-001",
                "College B Student",
                "student.consent@collegeb.edu",
                StudentStatus.ACTIVE,
                "Enrolled",
                "Computer Science",
                "9.10",
                "Bachelor of Technology",
                passwordEncoder.encode("StudentPassword123")
        ));
        studentToken = jwtUtil.generateStudentToken(
                "STU-B-CONSENT-001",
                "student.consent@collegeb.edu",
                "COLLEGE_B",
                "College B Student"
        );
        when(consentManagerClient.syncAssertionPublicKey(anyString(), anyString(), anyString())).thenReturn(true);
    }

    @Test
    void studentCanReadPendingConsentInbox() throws Exception {
        when(consentManagerClient.getPendingConsentRequestsRaw(anyString())).thenReturn("""
                [{"id":"CREQ_B_01","requesterOrganizationCode":"COLLEGE_A",
                  "purpose":"Academic verification","requestedFields":["CGPA"],
                  "status":"PENDING"}]
                """);

        mockMvc.perform(get("/api/student/consents/pending")
                        .header("Authorization", "Bearer " + studentToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].id").value("CREQ_B_01"))
                .andExpect(jsonPath("$[0].requestedFields[0]").value("CGPA"));
    }

    @Test
    void studentInboxRefreshesExpiredAssertionKeyAndRetries() throws Exception {
        when(consentManagerClient.getPendingConsentRequestsRaw(anyString()))
                .thenThrow(new HttpClientErrorException(
                        HttpStatus.FORBIDDEN,
                        "Forbidden",
                        HttpHeaders.EMPTY,
                        "{\"message\":\"Previous key ID has expired\"}".getBytes(StandardCharsets.UTF_8),
                        StandardCharsets.UTF_8))
                .thenReturn("[]");

        mockMvc.perform(get("/api/student/consents/pending")
                        .header("Authorization", "Bearer " + studentToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$").isEmpty());
        verify(consentManagerClient, atLeastOnce()).syncAssertionPublicKey(anyString(), anyString(), anyString());
    }

    @Test
    void studentCanApproveOnlySelectedConsentFields() throws Exception {
        ConsentDecisionResponse response = new ConsentDecisionResponse();
        response.setSuccess(true);
        response.setConsentId("CONSENT_B_01");
        response.setStatus("ACTIVE");
        response.setApprovedFields(List.of("CGPA"));
        response.setExpiresAt(Instant.now().plusSeconds(3600));
        when(consentManagerClient.approveConsent(eq("CREQ_B_01"), eq(List.of("CGPA")), anyString()))
                .thenReturn(response);

        mockMvc.perform(post("/api/student/consents/CREQ_B_01/approve")
                        .header("Authorization", "Bearer " + studentToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(Map.of("approvedFields", List.of("CGPA")))))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.status").value("ACTIVE"))
                .andExpect(jsonPath("$.approvedFields[0]").value("CGPA"))
                .andExpect(jsonPath("$.accessToken").doesNotExist());
    }
}
