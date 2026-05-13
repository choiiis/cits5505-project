document.addEventListener("DOMContentLoaded", () => {
    const shell = document.querySelector(".bookmark-stage-shell");
    const emptyState = document.getElementById("bookmarkEmptyState");

    if (shell) {
        shell.setAttribute("data-stage", "jinja");
    }

    function updateEmptyState() {
        if (!emptyState) {
            return;
        }

        const visibleCards = document.querySelectorAll("[data-bookmark-card]:not(.d-none)");
        emptyState.classList.toggle("d-none", visibleCards.length > 0);
    }

    document.querySelectorAll("[data-remove-bookmark]").forEach((button) => {
        button.addEventListener("click", () => {
            const card = button.closest("[data-bookmark-card]");

            if (card) {
                card.classList.add("d-none");
                updateEmptyState();
            }
        });
    });

    updateEmptyState();
});
