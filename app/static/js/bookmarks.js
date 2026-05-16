document.addEventListener("DOMContentLoaded", () => {
    const shell = document.querySelector(".bookmark-stage-shell");
    const emptyState = document.getElementById("bookmarkEmptyState");
    const collectionsData = document.getElementById("bookmarkCollectionsData");
    const bookmarkCollections = collectionsData ? JSON.parse(collectionsData.textContent) : [];

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

    function copyText(text, button) {
        navigator.clipboard.writeText(text).then(() => {
            const originalText = button.textContent;

            button.textContent = "Copied";

            setTimeout(() => {
                button.textContent = originalText;
            }, 1400);
        }).catch(() => {
            button.textContent = "Copy failed";
        });
    }

    document.querySelectorAll("[data-open-collection]").forEach((button) => {
        button.addEventListener("click", () => {
            const collectionId = button.dataset.openCollection;
            const modal = document.getElementById(`collectionModal-${collectionId}`);

            openModal(modal);
        });
    });

    document.querySelectorAll("[data-open-collection-settings]").forEach((button) => {
        button.addEventListener("click", () => {
            const collectionId = button.dataset.openCollectionSettings;
            const modal = document.getElementById(`collectionSettings-${collectionId}`);

            openModal(modal);
        });
    });

    document.querySelectorAll("[data-close-modal]").forEach((button) => {
        button.addEventListener("click", () => {
            closeModal(button.closest(".bookmark-modal"));
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

    document.querySelectorAll("[data-copy-share-code]").forEach((button) => {
        button.addEventListener("click", () => {
            const input = button.closest(".collection-copy-row").querySelector("[data-share-code-input]");

            copyText(input.value, button);
        });
    });

    document.querySelectorAll("[data-save-collection-settings]").forEach((button) => {
        button.addEventListener("click", () => {
            const modal = button.closest("[data-collection-settings-modal]");
            const collectionId = modal.id.replace("collectionSettings-", "");
            const card = document.querySelector(`[data-collection-id="${collectionId}"]`);
            const nameInput = modal.querySelector("[data-collection-name-input]");
            const visibilityInput = modal.querySelector("[data-collection-visibility-input]");
            const nextName = nameInput.value.trim();

            if (card && nextName) {
                card.querySelector("[data-collection-name-label]").textContent = nextName;
                card.querySelector("[data-collection-visibility-label]").textContent = visibilityInput.value;
            }

            modal.querySelector("h2").textContent = nextName || modal.querySelector("h2").textContent;
            button.textContent = "Saved";

            setTimeout(() => {
                button.textContent = "Save settings";
            }, 1400);
        });
    });

    document.querySelectorAll("[data-open-share-import]").forEach((button) => {
        button.addEventListener("click", () => {
            openModal(document.getElementById("shareImportModal"));
        });
    });

    document.querySelector("[data-preview-share-code]")?.addEventListener("click", () => {
        const input = document.getElementById("shareCodeInput");
        const preview = document.getElementById("sharePreview");
        const shareCode = input.value.trim().toUpperCase();
        const collection = bookmarkCollections.find((item) => item.share_code === shareCode);

        if (!collection) {
            preview.textContent = "No matching collection was found for that share code.";
            return;
        }

        preview.innerHTML = `
            <div class="collection-share-preview__eyebrow">Matched collection</div>
            <h3>${collection.name}</h3>
            <p>${collection.restaurant_count} places · ${collection.visibility}</p>
            <div class="collection-share-preview__actions">
                <button class="btn btn-success" type="button" data-subscribe-shared-collection>
                    Subscribe
                </button>
                <button class="btn btn-outline-success" type="button" data-copy-shared-collection>
                    Copy
                </button>
            </div>
        `;
    });

    document.getElementById("sharePreview")?.addEventListener("click", (event) => {
        const button = event.target.closest("button");

        if (!button) {
            return;
        }

        if (button.matches("[data-subscribe-shared-collection]")) {
            button.textContent = "Subscribed";
        }

        if (button.matches("[data-copy-shared-collection]")) {
            button.textContent = "Copied";
        }
    });

    document.addEventListener("keydown", (event) => {
        if (event.key !== "Escape") {
            return;
        }

        document.querySelectorAll(".bookmark-modal.is-open").forEach(closeModal);
    });

    updateEmptyState();
});
