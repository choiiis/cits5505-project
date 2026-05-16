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

    function openModal(modal) {
        if (!modal) {
            return;
        }

        modal.classList.add("is-open");
        modal.setAttribute("aria-hidden", "false");
        document.body.classList.add("modal-open");
    }

    function closeModal(modal) {
        if (!modal) {
            return;
        }

        modal.classList.remove("is-open");
        modal.setAttribute("aria-hidden", "true");
        document.body.classList.remove("modal-open");
    }

    document.querySelectorAll("[data-open-collection]").forEach((button) => {
        button.addEventListener("click", () => {
            const collectionId = button.dataset.openCollection;
            const modal = document.getElementById(`collectionModal-${collectionId}`);

            openModal(modal);
        });
    });

    document.querySelectorAll("[data-close-modal]").forEach((button) => {
        button.addEventListener("click", () => {
            closeModal(button.closest("[data-collection-modal]"));
        });
    });

    document.querySelectorAll("[data-toggle-collection-heart]").forEach((button) => {
        button.addEventListener("click", () => {
            const isSaved = button.classList.toggle("is-saved");

            button.textContent = isSaved ? "♥" : "♡";
            button.setAttribute("aria-pressed", String(isSaved));
            button.setAttribute(
                "aria-label",
                isSaved ? "Remove saved status" : "Save restaurant"
            );
        });
    });

    document.querySelectorAll("[data-remove-collection-restaurant]").forEach((button) => {
        button.addEventListener("click", () => {
            const card = button.closest("[data-collection-restaurant]");

            if (card) {
                card.remove();
            }
        });
    });

    document.addEventListener("keydown", (event) => {
        if (event.key !== "Escape") {
            return;
        }

        document.querySelectorAll("[data-collection-modal].is-open").forEach(closeModal);
    });

    updateEmptyState();
});
