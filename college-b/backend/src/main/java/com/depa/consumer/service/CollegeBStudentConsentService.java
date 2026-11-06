package com.depa.consumer.service;

import com.depa.consumer.client.ConsentManagerClient;
import com.depa.consumer.dto.ConsentDecisionResponse;
import com.depa.consumer.dto.ConsentHistoryDTO;
import com.depa.consumer.dto.ConsentRequestDTO;
import com.depa.consumer.entity.Student;
import com.depa.consumer.entity.StudentStatus;
import com.depa.consumer.repository.StudentRepository;
import com.depa.consumer.security.CollegeBAssertionKeyPairProvider;
import com.depa.consumer.security.CollegeBUserPrincipal;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.annotation.PostConstruct;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientResponseException;

import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.function.Supplier;

@Service
public class CollegeBStudentConsentService {

    private static final Logger log = LoggerFactory.getLogger(CollegeBStudentConsentService.class);

    private final CollegeBAssertionKeyPairProvider keyPairProvider;
    private final ConsentManagerClient cmClient;
    private final StudentRepository studentRepository;
    private final String internalApiKey;
    private final ObjectMapper objectMapper;
    private volatile boolean assertionKeyRegistered;

    public CollegeBStudentConsentService(
            CollegeBAssertionKeyPairProvider keyPairProvider,
            ConsentManagerClient cmClient,
            StudentRepository studentRepository,
            @Value("${app.internal.api-key:}") String internalApiKey,
            ObjectMapper objectMapper
    ) {
        this.keyPairProvider = keyPairProvider;
        this.cmClient = cmClient;
        this.studentRepository = studentRepository;
        this.internalApiKey = internalApiKey;
        this.objectMapper = objectMapper;
    }

    @PostConstruct
    public void init() {
        if (!registerAssertionKey(true)) {
            log.warn("Consent Manager unavailable during startup; College B assertion key registration will retry on demand.");
        }
    }

    public List<ConsentRequestDTO> getPendingConsents(CollegeBUserPrincipal principal) {
        Student student = validateAndGetStudent(principal);
        ensureAssertionKeyRegistered();
        try {
            return readList(withAssertionKeyRefresh(() -> cmClient.getPendingConsentRequestsRaw(
                    keyPairProvider.signStudentAssertion(student.getStudentId(), "READ_PENDING", null))),
                    new TypeReference<List<ConsentRequestDTO>>() {});
        } catch (Exception e) {
            log.error("Failed to fetch College B pending consents from Consent Manager: {}", e.getMessage());
            throw new IllegalStateException("Consent Manager communication failed: " + e.getMessage(), e);
        }
    }

    public List<ConsentHistoryDTO> getConsentHistory(CollegeBUserPrincipal principal) {
        Student student = validateAndGetStudent(principal);
        ensureAssertionKeyRegistered();
        try {
            return readList(withAssertionKeyRefresh(() -> cmClient.getConsentHistoryRaw(
                    keyPairProvider.signStudentAssertion(student.getStudentId(), "READ_HISTORY", null))),
                    new TypeReference<List<ConsentHistoryDTO>>() {});
        } catch (Exception e) {
            log.error("Failed to fetch College B consent history from Consent Manager: {}", e.getMessage());
            throw new IllegalStateException("Consent Manager communication failed: " + e.getMessage(), e);
        }
    }

    public ConsentDecisionResponse approveConsent(String requestId, List<String> fields, CollegeBUserPrincipal principal) {
        Student student = validateAndGetStudent(principal);
        ensureAssertionKeyRegistered();
        try {
            return withAssertionKeyRefresh(() -> cmClient.approveConsent(
                    requestId,
                    fields,
                    keyPairProvider.signStudentAssertion(student.getStudentId(), "APPROVE", requestId)));
        } catch (Exception e) {
            log.error("Failed to submit College B consent approval: {}", e.getMessage());
            throw new IllegalStateException("Consent Manager approval failed: " + e.getMessage(), e);
        }
    }

    public Map<String, Object> rejectConsent(String requestId, CollegeBUserPrincipal principal) {
        Student student = validateAndGetStudent(principal);
        ensureAssertionKeyRegistered();
        try {
            return withAssertionKeyRefresh(() -> cmClient.rejectConsent(
                    requestId,
                    keyPairProvider.signStudentAssertion(student.getStudentId(), "REJECT", requestId)));
        } catch (Exception e) {
            log.error("Failed to submit College B consent rejection: {}", e.getMessage());
            throw new IllegalStateException("Consent Manager rejection failed: " + e.getMessage(), e);
        }
    }

    public Map<String, Object> revokeConsent(String consentId, CollegeBUserPrincipal principal) {
        Student student = validateAndGetStudent(principal);
        ensureAssertionKeyRegistered();
        try {
            return withAssertionKeyRefresh(() -> cmClient.revokeConsent(
                    consentId,
                    keyPairProvider.signStudentAssertion(student.getStudentId(), "REVOKE", consentId)));
        } catch (Exception e) {
            log.error("Failed to submit College B consent revocation: {}", e.getMessage());
            throw new IllegalStateException("Consent Manager revocation failed: " + e.getMessage(), e);
        }
    }

    private Student validateAndGetStudent(CollegeBUserPrincipal principal) {
        if (principal == null || principal.getStudentId() == null) {
            throw new AccessDeniedException("Authenticated College B student is required.");
        }
        Student student = studentRepository.findByStudentId(principal.getStudentId())
                .orElseThrow(() -> new AccessDeniedException("Student profile not found in College B registry."));
        if (student.getStatus() != StudentStatus.ACTIVE) {
            throw new AccessDeniedException("Student account is not active.");
        }
        return student;
    }

    private synchronized boolean registerAssertionKey(boolean force) {
        if (assertionKeyRegistered && !force) {
            return true;
        }
        assertionKeyRegistered = cmClient.syncAssertionPublicKey(
                keyPairProvider.getPublicKeyPem(),
                keyPairProvider.getKeyId(),
                internalApiKey
        );
        if (assertionKeyRegistered) {
            log.info("Registered College B assertion public key with Consent Manager (kid={})", keyPairProvider.getKeyId());
        }
        return assertionKeyRegistered;
    }

    private void ensureAssertionKeyRegistered() {
        if (!registerAssertionKey(false)) {
            throw new IllegalStateException("College B assertion key could not be registered with the Consent Manager.");
        }
    }

    private <T> T withAssertionKeyRefresh(Supplier<T> request) {
        try {
            return request.get();
        } catch (RestClientResponseException e) {
            String responseBody = e.getResponseBodyAsString();
            if (e.getStatusCode().value() != 403
                    || !(responseBody.contains("Previous key ID has expired")
                    || responseBody.contains("Unknown or outdated key ID"))) {
                throw e;
            }

            log.warn("Consent Manager rejected College B assertion key; re-registering key before retry.");
            if (!registerAssertionKey(true)) {
                throw new IllegalStateException("College B assertion key could not be refreshed with the Consent Manager.", e);
            }
            return request.get();
        }
    }

    private <T> List<T> readList(String json, TypeReference<List<T>> type) {
        if (json == null || json.isBlank()) {
            return Collections.emptyList();
        }
        try {
            JsonNode root = objectMapper.readTree(json);
            if (root.isArray()) {
                return objectMapper.readValue(json, type);
            }
            if (root.has("content") && root.get("content").isArray()) {
                return objectMapper.readValue(root.get("content").toString(), type);
            }
            return Collections.emptyList();
        } catch (Exception e) {
            throw new IllegalStateException("Could not parse Consent Manager consent response.", e);
        }
    }
}
