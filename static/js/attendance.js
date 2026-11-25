// Attendance marking UI — Task 12
// - Live summary counter (Task 11)
// - Bulk mark actions (Task 11)
// - Save flow: confirmation dialog -> fetch POST -> redirect / error (Task 12)

(function () {
    'use strict';

    const form = document.getElementById('attendance-form');
    if (!form) return;

    const summary = document.getElementById('attendance-summary');
    const errorBox = document.getElementById('attendance-error');
    const saveBtn = document.getElementById('save-btn');
    const dialog = document.getElementById('save-dialog');
    const dialogSummary = document.getElementById('save-dialog-summary');
    const dialogCancel = document.getElementById('save-dialog-cancel');
    const dialogConfirm = document.getElementById('save-dialog-confirm');

    function counts() {
        const c = { present: 0, absent: 0, late: 0, excused: 0 };
        form.querySelectorAll('input.attendance-radio:checked').forEach((r) => {
            if (Object.prototype.hasOwnProperty.call(c, r.value)) {
                c[r.value] += 1;
            }
        });
        return c;
    }

    function summaryText(c) {
        return `${c.present} present · ${c.absent} absent · ` +
               `${c.late} late · ${c.excused} excused`;
    }

    function recount() {
        if (summary) summary.textContent = summaryText(counts());
    }

    function markAll(status) {
        form.querySelectorAll(`input.attendance-radio[value="${status}"]`)
            .forEach((r) => { r.checked = true; });
        recount();
    }

    function showError(msg) {
        if (!errorBox) return;
        errorBox.textContent = msg;
        errorBox.hidden = false;
        errorBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    function clearError() {
        if (!errorBox) return;
        errorBox.hidden = true;
        errorBox.textContent = '';
    }

    function buildPayload() {
        const records = [];
        form.querySelectorAll('input.attendance-radio:checked').forEach((r) => {
            const eid = parseInt(r.name.replace('status_', ''), 10);
            records.push({ enrollment_id: eid, status: r.value });
        });
        return { records };
    }

    function csrfToken() {
        const input = form.querySelector('input[name="csrfmiddlewaretoken"]');
        return input ? input.value : '';
    }

    async function doSave() {
        clearError();
        const payload = buildPayload();
        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken(),
                },
                body: JSON.stringify(payload),
            });
            const data = await response.json().catch(() => ({
                ok: false, error: 'Server returned non-JSON response.',
            }));
            if (data.ok && data.redirect_url) {
                window.location.href = data.redirect_url;
            } else {
                showError(data.error || 'Save failed.');
            }
        } catch (err) {
            showError('Network error: ' + err.message);
        }
    }

    // --- Wire up ---

    form.addEventListener('change', (e) => {
        if (e.target.classList.contains('attendance-radio')) recount();
    });

    form.querySelectorAll('.attendance-bulk').forEach((btn) => {
        btn.addEventListener('click', () => {
            markAll(btn.dataset.bulk);
        });
    });

    if (saveBtn && dialog) {
        saveBtn.addEventListener('click', () => {
            clearError();
            const c = counts();
            const total = c.present + c.absent + c.late + c.excused;
            if (total === 0) {
                showError('No students to save.');
                return;
            }
            if (dialogSummary) {
                dialogSummary.textContent =
                    `Save attendance for ${total} student${total === 1 ? '' : 's'}? ` +
                    summaryText(c);
            }
            dialog.showModal();
        });
    }

    if (dialogCancel) {
        dialogCancel.addEventListener('click', () => dialog && dialog.close());
    }

    if (dialogConfirm) {
        dialogConfirm.addEventListener('click', () => {
            dialog && dialog.close();
            doSave();
        });
    }

    // Initial render
    recount();
})();
