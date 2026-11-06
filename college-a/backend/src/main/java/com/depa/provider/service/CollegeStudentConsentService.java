package com.depa.provider.service;

import com.depa.provider.client.ConsentManagerClient;
import com.depa.provider.dto.ConsentDecisionResponse;
import com.depa.provider.dto.ConsentHistoryDTO;
import com.depa.provider.dto.ConsentRequestDTO;
import com.depa.provider.entity.Student;
import com.depa.provider.entity.StudentStatus;
import com.depa.provider.repository.StudentRepository;
import com.depa.provider.security.CollegeAUserPrincipal;
import com.depa.provider.security.CollegeAssertionKeyPairProvider;
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
public class CollegeStudentConsentService {

    private static final Logger log = LoggerFactory.getLogger(CollegeStudentConsentService.class);

    private final CollegeAssertionKeyPairProvider keyPairProvider;
    private final ConsentManagerClient cmClient;
    private final StudentRepository studentRepository;
    private final String internalApiKey;
    private final ObjectMapper objectMapper;
    private volatile boolean assertionKeyRegistered;

    public CollegeStudentConsentService(
            CollegeAssertionKeyPairProvider keyPairProvider,
            ConsentManagerClient cmClient,
            StudentRepository studentRepository,
            @Value("${app.internal.api-key:A-INTERNAL-SECRET-KEY}") String internalApiKey,
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
            log.warn("Consent Manager unavailable during startup; College A assertion key registration will retry on demand.");
        }
    }

    public List<ConsentRequestDTO> getPendingConsents(CollegeAUserPrincipal principal) {
        Student student = validateAndGetStudent(principal);
        ensureAssertionKeyRegistered();

        try {
            String rawJson = withAssertionKeyRefresh(() ->
                    cmClient.getPendingConsentRequestsRaw(
                            keyPairProvider.signStudentAssertion(student.getStudentId(), "READ_PENDING", null)));
            return extractPageOrList(rawJson, new TypeReference<List<ConsentRequestDTO>>() {});
        } catch (Exception e) {
            log.error("Failed to fetch pending consents from Consent Manager: {}", e.getMessage());
            throw new RuntimeException("Consent Manager communication failed: " + e.getMessage(), e);
        }
    }

    public List<ConsentHistoryDTO> getConsentHistory(CollegeAUserPrincipal principal) {
        Student student = validateAndGetStudent(principal);
        ensureAssertionKeyRegistered();

        try {
            String rawJson = withAssertionKeyRefresh(() ->
                    cmClient.getConsentHistoryRaw(
                            keyPairProvider.signStudentAssertion(student.getStudentId(), "READ_HISTORY", null)));
            return extractPageOrList(rawJson, new TypeReference<List<ConsentHistoryDTO>>() {});
        } catch (Exception e) {
            log.error("Failed to fetch consent history from Consent Manager: {}", e.getMessage());
            throw new RuntimeException("Consent Manager communication failed: " + e.getMessage(), e);
        }
    }

    public ConsentDecisionResponse approveConsent(String consentRequestId, List<String> approvedFields, CollegeAUserPrincipal principal) {
        Student student = validateAndGetStudent(principal);
        ensureAssertionKeyRegistered();

        try {
            return withAssertionKeyRefresh(() -> cmClient.approveConsent(
                    consentRequestId,
                    approvedFields,
                    keyPairProvider.signStudentAssertion(student.getStudentId(), "APPROVE", consentRequestId)));
        } catch (Exception e) {
            log.error("Failed to submit consent approval to Consent Manager: {}", e.getMessage());
            throw new RuntimeException("Consent Manager approval failed: " + e.getMessage(), e);
        }
    }

    public Map<String, Object> rejectConsent(String consentRequestId, CollegeAUserPrincipal principal) {
        Student student = validateAndGetStudent(principal);
        ensureAssertionKeyRegistered();

        try {
            return withAssertionKeyRefresh(() -> cmClient.rejectConsent(
                    consentRequestId,
                    keyPairProvider.signStudentAssertion(student.getStudentId(), "REJECT", consentRequestId)));
        } catch (Exception e) {
            log.error("Failed to submit consent rejection to Consent Manager: {}", e.getMessage());
            throw new RuntimeException("Consent Manager rejection failed: " + e.getMessage(), e);
        }
    }

    public Map<String, Object> revokeConsent(String consentId, CollegeAUserPrincipal principal) {
        Student student = validateAndGetStudent(principal);
        ensureAssertionKeyRegistered();

        try {
            return withAssertionKeyRefresh(() -> cmClient.revokeConsent(
                    consentId,
                    keyPairProvider.signStudentAssertion(student.getStudentId(), "REVOKE", consentId)));
        } catch (Exception e) {
            log.error("Failed to submit consent revocation to Consent Manager: {}", e.getMessage());
            throw new RuntimeException("Consent Manager revocation failed: " + e.getMessage(), e);
        }
    }

    private Student validateAndGetStudent(CollegeAUserPrincipal principal) {
        if (principal == null || principal.getStudentId() == null) {
            throw new AccessDeniedException("Access Denied: Unauthenticated or non-student user");
        }

        Student student = studentRepository.findByStudentId(principal.getStudentId())
                .orElseThrow(() -> new AccessDeniedException("Student profile not found in local college registry: " + principal.getStudentId()));

        if (student.getStatus() != StudentStatus.ACTIVE) {
            throw new AccessDeniedException("Student account is not active (status: " + student.getStatus() + ")");
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
            log.info("Successfully registered College A assertion RSA public key with Consent Manager (kid={})", keyPairProvider.getKeyId());
        }
        return assertionKeyRegistered;
    }

    private void ensureAssertionKeyRegistered() {
        if (!registerAssertionKey(false)) {
            throw new IllegalStateException("College A assertion key could not be registered with the Consent Manager.");
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

            log.warn("Consent Manager rejected College A assertion key; re-registering key before retry.");
            if (!registerAssertionKey(true)) {
                throw new IllegalStateException("College A assertion key could not be refreshed with the Consent Manager.", e);
            }
            return request.get();
        }
    }

    private <T> List<T> extractPageOrList(String rawJson, TypeReference<List<T>> typeRef) {
        if (rawJson == null || rawJson.isBlank()) {
            return Collections.emptyList();
        }

        try {
            JsonNode root = objectMapper.readTree(rawJson);
            if (root.isArray()) {
                return objectMapper.readValue(rawJson, typeRef);
            } else if (root.has("content") && root.get("content").isArray()) {
                return objectMapper.readValue(root.get("content").toString(), typeRef);
            }
            return Collections.emptyList();
        } catch (Exception e) {
            log.warn("Failed to parse list/page JSON: {}", e.getMessage());
            return Collections.emptyList();
        }
    }
}
