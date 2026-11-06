package com.depa.consumer.controller;

import com.depa.consumer.dto.ApproveConsentRequest;
import com.depa.consumer.dto.ConsentDecisionResponse;
import com.depa.consumer.dto.ConsentHistoryDTO;
import com.depa.consumer.dto.ConsentRequestDTO;
import com.depa.consumer.security.CollegeBUserPrincipal;
import com.depa.consumer.service.CollegeBStudentConsentService;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/student/consents")
@PreAuthorize("hasRole('STUDENT')")
public class CollegeBStudentConsentController {

    private final CollegeBStudentConsentService consentService;

    public CollegeBStudentConsentController(CollegeBStudentConsentService consentService) {
        this.consentService = consentService;
    }

    @GetMapping("/pending")
    public ResponseEntity<List<ConsentRequestDTO>> getPendingConsents(
            @AuthenticationPrincipal CollegeBUserPrincipal principal) {
        return ResponseEntity.ok(consentService.getPendingConsents(principal));
    }

    @GetMapping("/history")
    public ResponseEntity<List<ConsentHistoryDTO>> getConsentHistory(
            @AuthenticationPrincipal CollegeBUserPrincipal principal) {
        return ResponseEntity.ok(consentService.getConsentHistory(principal));
    }

    @PostMapping("/{id}/approve")
    public ResponseEntity<ConsentDecisionResponse> approveConsent(
            @PathVariable("id") String requestId,
            @RequestBody(required = false) ApproveConsentRequest request,
            @AuthenticationPrincipal CollegeBUserPrincipal principal) {
        List<String> approvedFields = request != null ? request.getApprovedFields() : null;
        return ResponseEntity.ok(consentService.approveConsent(requestId, approvedFields, principal));
    }

    @PostMapping("/{id}/reject")
    public ResponseEntity<Map<String, Object>> rejectConsent(
            @PathVariable("id") String requestId,
            @AuthenticationPrincipal CollegeBUserPrincipal principal) {
        return ResponseEntity.ok(consentService.rejectConsent(requestId, principal));
    }

    @PostMapping("/{id}/revoke")
    public ResponseEntity<Map<String, Object>> revokeConsent(
            @PathVariable("id") String consentId,
            @AuthenticationPrincipal CollegeBUserPrincipal principal) {
        return ResponseEntity.ok(consentService.revokeConsent(consentId, principal));
    }
}
