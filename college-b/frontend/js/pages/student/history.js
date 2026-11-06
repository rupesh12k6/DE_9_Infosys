/**
 * College B student consent history and active grant revocation.
 */
window.DF_PAGE_STUDENT_HISTORY = (function () {
    'use strict';

    let records = [];
    let filter = 'ALL';

    async function render(container) {
        if (!container) return;
        container.innerHTML = `<div class="py-5">${window.DF_UI.renderLoadingState('Loading Consent History...')}</div>`;
        try {
            const response = await window.DF_API.student.getConsentHistory();
            records = Array.isArray(response) ? response : [];
            renderRecords(container);
        } catch (error) {
            container.innerHTML = `<div class="py-5">${window.DF_UI.renderErrorState({
                title: 'Unable to Load Consent History',
                message: error.message,
                onRetry: () => render(container)
            })}</div>`;
        }
    }

    function renderRecords(container) {
        const active = records.filter(record => record.status === 'ACTIVE').length;
        const revoked = records.filter(record => record.status === 'REVOKED').length;
        const shown = records.filter(record => filter === 'ALL' || record.status === filter);
        container.innerHTML = `
            <div class="d-flex flex-wrap justify-content-between align-items-center gap-3 mb-4">
                <div>
                    <h3 class="fw-bold text-dark mb-1">Consent History & Revocation</h3>
                    <p class="text-muted small mb-0">Review your past decisions and revoke active permissions for future data access.</p>
                </div>
                <button class="btn btn-sm btn-outline-secondary" id="btn-refresh-colb-history">
                    <i class="bi bi-arrow-clockwise me-1"></i> Refresh
                </button>
            </div>
            <div class="alert alert-warning small">
                Revoking consent blocks future retrievals. It cannot recall data already lawfully retrieved before revocation.
            </div>
            <div class="d-flex gap-2 mb-3">
                ${[['ALL', `All (${records.length})`], ['ACTIVE', `Active (${active})`], ['REVOKED', `Revoked (${revoked})`]]
                    .map(([key, label]) => `<button class="btn btn-sm ${filter === key ? 'btn-primary' : 'btn-outline-secondary'} rounded-pill consent-history-filter" data-filter="${key}">${label}</button>`)
                    .join('')}
            </div>
            <div class="card border-0 shadow-sm rounded-4 overflow-hidden">
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-light small text-uppercase"><tr>
                            <th class="ps-3">Consent</th><th>Institution</th><th>Purpose</th>
                            <th>Approved Fields</th><th>Granted</th><th>Status</th><th class="text-end pe-3">Action</th>
                        </tr></thead>
                        <tbody>
                            ${shown.map(renderRow).join('') || `<tr><td colspan="7" class="text-center text-muted py-5">No consent records found.</td></tr>`}
                        </tbody>
                    </table>
                </div>
            </div>
        `;

        container.querySelector('#btn-refresh-colb-history').addEventListener('click', () => render(container));
        container.querySelectorAll('.consent-history-filter').forEach(button => {
            button.addEventListener('click', () => {
                filter = button.dataset.filter;
                renderRecords(container);
            });
        });
        container.querySelectorAll('.revoke-consent').forEach(button => {
            button.addEventListener('click', () => revoke(button.dataset.consentId, button.dataset.orgName, container));
        });
    }

    function renderRow(record) {
        const consentId = record.id || record.consentId;
        const fields = Array.isArray(record.approvedFields) ? record.approvedFields : [];
        const orgName = record.requesterOrganizationName || record.requesterOrganizationCode || 'Requesting institution';
        return `<tr>
            <td class="ps-3 font-monospace small fw-bold">${window.DF_UI.escapeHtml(consentId)}</td>
            <td class="fw-semibold">${window.DF_UI.escapeHtml(orgName)}</td>
            <td class="small">${window.DF_UI.escapeHtml(record.purpose || 'Academic verification')}</td>
            <td>${fields.map(field => `<span class="badge bg-light text-dark border me-1">${window.DF_UI.escapeHtml(field)}</span>`).join('') || '<span class="text-muted">None</span>'}</td>
            <td class="small text-muted">${record.grantedAt ? window.DF_UI.escapeHtml(new Date(record.grantedAt).toLocaleString()) : '—'}</td>
            <td>${window.DF_UI.renderStatusBadge(record.status)}</td>
            <td class="text-end pe-3">${record.status === 'ACTIVE'
                ? `<button type="button" class="btn btn-sm btn-outline-danger revoke-consent"
                    data-consent-id="${window.DF_UI.escapeHtml(consentId)}"
                    data-org-name="${window.DF_UI.escapeHtml(orgName)}">Revoke</button>`
                : '<span class="text-muted small">—</span>'}</td>
        </tr>`;
    }

    function revoke(consentId, organizationName, container) {
        window.DF_UI.showConfirmDialog({
            title: 'Revoke Consent?',
            message: `Future access to your records will be blocked for ${organizationName}.`,
            confirmText: 'Revoke Access',
            confirmBtnClass: 'btn-danger',
            onConfirm: async () => {
                try {
                    await window.DF_API.student.revokeConsent(consentId);
                    window.DF_UI.showToast('Consent revoked. Future access is blocked.', 'success');
                    await render(container);
                } catch (error) {
                    window.DF_UI.showToast(`Revocation failed: ${error.message}`, 'error');
                }
            }
        });
    }

    return { render };
})();
