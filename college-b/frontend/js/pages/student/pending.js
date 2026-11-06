/**
 * College B student consent inbox: review requests and choose which fields to disclose.
 */
window.DF_PAGE_STUDENT_PENDING = (function () {
    'use strict';

    async function render(container) {
        if (!container) return;
        container.innerHTML = `<div class="py-5">${window.DF_UI.renderLoadingState('Checking Consent Inbox...')}</div>`;

        try {
            const response = await window.DF_API.student.getPendingConsents();
            const requests = Array.isArray(response) ? response : [];
            container.innerHTML = `
                <div class="d-flex flex-wrap justify-content-between align-items-center gap-3 mb-4">
                    <div>
                        <h3 class="fw-bold text-dark mb-1">Consent Decision Inbox</h3>
                        <p class="text-muted small mb-0">Review requests for your College B academic records. Choose exactly which fields to share.</p>
                    </div>
                    <div class="d-flex align-items-center gap-2">
                        <span class="badge ${requests.length ? 'bg-warning-subtle text-warning' : 'bg-light text-muted'} border px-3 py-2 rounded-pill">
                            ${requests.length} PENDING REQUEST${requests.length === 1 ? '' : 'S'}
                        </span>
                        <button class="btn btn-sm btn-outline-secondary" id="btn-refresh-colb-consents">
                            <i class="bi bi-arrow-clockwise me-1"></i> Refresh
                        </button>
                    </div>
                </div>
                <div class="alert alert-info small">
                    <i class="bi bi-shield-lock-fill me-2"></i>
                    No fields are selected by default. Approving discloses only the fields you select. You can reject a request or revoke an active consent later.
                </div>
                <div class="row g-3">
                    ${requests.map(renderRequest).join('')}
                    ${requests.length === 0 ? `
                        <div class="col-12">
                            <div class="card border-0 shadow-sm rounded-4 p-5 text-center">
                                <i class="bi bi-inbox text-muted display-4 mb-3"></i>
                                <h5 class="fw-bold">Your consent inbox is clear</h5>
                                <p class="text-muted mb-0">New requests to access your College B records will appear here.</p>
                            </div>
                        </div>` : ''}
                </div>
            `;

            container.querySelector('#btn-refresh-colb-consents')
                .addEventListener('click', () => render(container));
            requests.forEach(request => wireRequestActions(request, container));
        } catch (error) {
            container.innerHTML = `<div class="py-5">${window.DF_UI.renderErrorState({
                title: 'Unable to Load Consent Requests',
                message: error.message,
                onRetry: () => render(container)
            })}</div>`;
        }
    }

    function renderRequest(request) {
        const requestId = request.id || request.consentRequestId;
        const safeId = window.DF_UI.escapeHtml(requestId);
        const fields = Array.isArray(request.requestedFields) ? request.requestedFields : [];
        const fieldItems = fields.map(field => {
            const safeField = window.DF_UI.escapeHtml(field);
            return `<div class="col-md-6">
                <label class="form-check border rounded-3 bg-white p-2 d-flex gap-2 align-items-start h-100">
                    <input class="form-check-input ms-1 consent-field" type="checkbox" value="${safeField}">
                    <span class="small"><strong>${safeField}</strong><br><span class="text-muted">Academic record field</span></span>
                </label>
            </div>`;
        }).join('');

        return `<div class="col-12">
            <article class="card border-0 shadow-sm rounded-4" data-consent-id="${safeId}">
                <div class="card-header bg-white border-bottom p-3 d-flex flex-wrap justify-content-between gap-2">
                    <div>
                        <span class="badge bg-light text-dark border font-monospace mb-1">REQUEST: ${safeId}</span>
                        <h5 class="fw-bold mb-0">${window.DF_UI.escapeHtml(request.requesterOrganizationName || request.requesterOrganizationCode || 'Requesting institution')}</h5>
                    </div>
                    <span class="badge bg-warning-subtle text-warning border rounded-pill align-self-start">
                        Expires ${request.expiresAt ? window.DF_UI.escapeHtml(new Date(request.expiresAt).toLocaleDateString()) : 'in 7 days'}
                    </span>
                </div>
                <div class="card-body p-4">
                    <div class="mb-3">
                        <div class="text-muted small fw-bold text-uppercase mb-1">Purpose</div>
                        <p class="mb-0">${window.DF_UI.escapeHtml(request.purpose || 'Academic verification')}</p>
                    </div>
                    <div class="mb-4">
                        <div class="text-muted small fw-bold text-uppercase mb-2">Select fields to disclose</div>
                        <div class="row g-2">${fieldItems || '<div class="col-12 text-muted small">No fields were listed in this request.</div>'}</div>
                    </div>
                    <div class="d-flex justify-content-between flex-wrap gap-2 pt-3 border-top">
                        <button type="button" class="btn btn-outline-danger btn-sm reject-consent">
                            <i class="bi bi-x-circle me-1"></i> Reject
                        </button>
                        <button type="button" class="btn btn-primary btn-sm approve-consent" ${fields.length ? '' : 'disabled'}>
                            <i class="bi bi-check-circle me-1"></i> Approve Selected Fields
                        </button>
                    </div>
                </div>
            </article>
        </div>`;
    }

    function wireRequestActions(request, container) {
        const requestId = request.id || request.consentRequestId;
        const card = Array.from(container.querySelectorAll('[data-consent-id]'))
            .find(item => item.getAttribute('data-consent-id') === window.DF_UI.escapeHtml(requestId));
        if (!card) return;
        const approveButton = card.querySelector('.approve-consent');
        const rejectButton = card.querySelector('.reject-consent');

        approveButton.addEventListener('click', () => {
            const fields = Array.from(card.querySelectorAll('.consent-field:checked')).map(item => item.value);
            if (!fields.length) {
                window.DF_UI.showToast('Select at least one requested field, or reject the request.', 'warning');
                return;
            }
            const requestedFields = Array.isArray(request.requestedFields) ? request.requestedFields : [];
            if (!fields.every(field => requestedFields.includes(field))) {
                window.DF_UI.showToast('Only fields included in this request can be approved.', 'error');
                return;
            }
            window.DF_UI.showConfirmDialog({
                title: 'Approve Academic Data Request?',
                message: `Share ${fields.join(', ')} with ${request.requesterOrganizationName || request.requesterOrganizationCode || 'the requesting institution'}?`,
                confirmText: 'Approve Selected Fields',
                confirmBtnClass: 'btn-primary',
                onConfirm: async () => {
                    approveButton.disabled = true;
                    rejectButton.disabled = true;
                    try {
                        await window.DF_API.student.approveConsent(requestId, fields);
                        window.DF_UI.showToast('Consent approved. Only the selected fields were authorized.', 'success');
                        await render(container);
                    } catch (error) {
                        window.DF_UI.showToast(`Approval failed: ${error.message}`, 'error');
                        approveButton.disabled = false;
                        rejectButton.disabled = false;
                    }
                }
            });
        });

        rejectButton.addEventListener('click', () => window.DF_UI.showConfirmDialog({
            title: 'Reject Consent Request?',
            message: `No records will be shared with ${request.requesterOrganizationName || request.requesterOrganizationCode || 'the requesting institution'}.`,
            confirmText: 'Reject Request',
            confirmBtnClass: 'btn-danger',
            onConfirm: async () => {
                approveButton.disabled = true;
                rejectButton.disabled = true;
                try {
                    await window.DF_API.student.rejectConsent(requestId);
                    window.DF_UI.showToast('Consent request rejected. No records were shared.', 'info');
                    await render(container);
                } catch (error) {
                    window.DF_UI.showToast(`Rejection failed: ${error.message}`, 'error');
                    approveButton.disabled = false;
                    rejectButton.disabled = false;
                }
            }
        }));
    }

    return { render };
})();
