document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-row-url]").forEach((row) => {
        row.addEventListener("click", (event) => {
            if (event.target.closest("a, button, input, select, textarea, form")) {
                return;
            }

            window.location.href = row.dataset.rowUrl;
        });
    });

    document.querySelectorAll("[data-status-select]").forEach((select) => {
        const statusClasses = [
            "admin-status-select--approved",
            "admin-status-select--pending",
            "admin-status-select--reported",
            "admin-status-select--active",
            "admin-status-select--suspended",
            "admin-status-select--hidden",
        ];

        function updateStatusClass() {
            select.classList.remove(...statusClasses);
            select.classList.add(`admin-status-select--${select.value}`);
        }

        select.addEventListener("change", updateStatusClass);
        updateStatusClass();
    });
});