(function () {
    'use strict';

    const form = document.getElementById('attendance-form');
    if (!form) return;

    const summary = document.getElementById('attendance-summary');

    function recount() {
        const counts = { present: 0, absent: 0, late: 0, excused: 0 };
        form.querySelectorAll('input.attendance-radio:checked').forEach((r) => {
            if (Object.prototype.hasOwnProperty.call(counts, r.value)) {
                counts[r.value] += 1;
            }
        });
        if (summary) {
            summary.textContent =
                `${counts.present} present · ${counts.absent} absent · ` +
                `${counts.late} late · ${counts.excused} excused`;
        }
    }

    function markAll(status) {
        form.querySelectorAll(`input.attendance-radio[value="${status}"]`)
            .forEach((r) => { r.checked = true; });
        recount();
    }

    form.addEventListener('change', (e) => {
        if (e.target.classList.contains('attendance-radio')) recount();
    });

    form.querySelectorAll('.attendance-bulk').forEach((btn) => {
        btn.addEventListener('click', () => {
            markAll(btn.dataset.bulk);
        });
    });

    recount();
})();
